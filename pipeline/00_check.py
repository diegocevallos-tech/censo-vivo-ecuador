"""Reproduce phase-0 schema and geography QA from verified private ZIPs.

Run ``python pipeline/fetch_raw.py`` first with access to the private Release.
Only aggregate CSVs and JSON results are written outside gitignored data/raw/.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
INTERIM = ROOT / "data/interim"
OFFICIAL_POPULATION = 16_938_986
OFFICIAL_DWELLINGS = 6_611_555
EXTRACT = {
    "BDD_CPV2022_MANLOC_CSV.zip": [
        "1.3 BDD_CPV_2022_MANLOC_CSV/CPV_2022_Poblacion_Manloc.csv",
        "1.3 BDD_CPV_2022_MANLOC_CSV/CPV_2022_Vivienda_Manloc.csv",
        "1.3 BDD_CPV_2022_MANLOC_CSV/CPV_2022_Hogar_Manloc.csv",
        "1.3 BDD_CPV_2022_MANLOC_CSV/CPV_2022_Emigracion_Manloc.csv",
        "1.3 BDD_CPV_2022_MANLOC_CSV/CPV_2022_Mortalidad_Manloc.csv",
    ],
    "CapaSectores.zip": ["sectores_anonimizados.gpkg"],
    "GEODATABASE_NACIONAL_2021.zip": ["GEODATABASE_NACIONAL_2021/GEODATABASE_NACIONAL_2021.gpkg"],
}


def extract_required(*, compact: bool) -> None:
    order = list(EXTRACT)
    if compact:
        order.remove("GEODATABASE_NACIONAL_2021.zip")
        order.insert(0, "GEODATABASE_NACIONAL_2021.zip")
    for archive_name in order:
        members = EXTRACT[archive_name]
        archive = RAW / archive_name
        if not archive.is_file():
            raise FileNotFoundError(f"Run pipeline/fetch_raw.py first: {archive}")
        with ZipFile(archive) as source:
            for member in members:
                target = RAW / member
                if target.is_file():
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with source.open(member) as input_stream, target.open("wb") as output:
                    shutil.copyfileobj(input_stream, output, length=8 * 1024 * 1024)
                print(f"Extracted {member}", flush=True)
        if compact and archive_name == "GEODATABASE_NACIONAL_2021.zip":
            # This mode is for ephemeral CI runners with limited disk. The
            # original and its verified split parts remain in the Release.
            raw_root = RAW.resolve()
            for path in [archive, *RAW.glob(f"{archive_name}.part-*")]:
                if not path.resolve().is_relative_to(raw_root):
                    raise ValueError(f"Unexpected cleanup path: {path}")
                path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample", action="store_true", help="Read ZIP headers and 100 rows without extraction"
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Discard verified geodatabase ZIP after extraction on ephemeral CI",
    )
    args = parser.parse_args()
    if args.sample:
        sample_archives()
        return
    extract_required(compact=args.compact)
    for script in ("00_validate_sources.py", "00_geography_keys.py"):
        subprocess.run([sys.executable, str(ROOT / "pipeline" / script)], check=True)

    schema = json.loads((INTERIM / "fase0_schema.json").read_text(encoding="utf-8"))
    assert len(schema) == 5
    assert all(
        item["csv_matches_duckdb"]
        and not item["csv_not_in_dictionary"]
        and not item["dictionary_not_in_csv"]
        for item in schema.values()
    )
    with (INTERIM / "sector_match.csv").open(encoding="utf-8", newline="") as stream:
        sectors = list(csv.DictReader(stream))
    with (INTERIM / "manzana_match.csv").open(encoding="utf-8", newline="") as stream:
        manzanas = list(csv.DictReader(stream))
    with (ROOT / "docs/qa/manzanas_sin_match.csv").open(encoding="utf-8", newline="") as stream:
        unmatched = list(csv.DictReader(stream))
    assert len(sectors) == len(manzanas) == 24
    assert all(float(row["census_match_percent"]) > 95 for row in sectors + manzanas)
    assert len(unmatched) == sum(int(row["unmatched_manzanas"]) for row in manzanas)
    assert sum(int(row["population"]) for row in sectors) == OFFICIAL_POPULATION

    connection = duckdb.connect(str(INTERIM / "fase0.duckdb"), read_only=True)
    population, dwellings = connection.execute(
        "SELECT SUM(population), SUM(dwellings) FROM census_sectors"
    ).fetchone()
    assert population == OFFICIAL_POPULATION
    assert dwellings == OFFICIAL_DWELLINGS
    unassigned_to_sector = connection.execute(
        """
        SELECT COUNT(*) FROM census_manzanas m
        LEFT JOIN geometry_manzanas g ON m.manzana_key = g.manzana_key
        LEFT JOIN geometry_sectors s ON m.sector_key = s.sector_key
        WHERE m.is_matchable AND g.manzana_key IS NULL AND s.sector_key IS NULL
        """
    ).fetchone()[0]
    assert unassigned_to_sector == 0
    for level, digits in (("province", 2), ("canton", 4), ("parish", 6)):
        totals = connection.execute(
            f"SELECT SUM(population), SUM(dwellings) FROM "
            f"(SELECT SUBSTR(sector_key, 1, {digits}) AS key, "
            "SUM(population) AS population, SUM(dwellings) AS dwellings "
            "FROM census_sectors GROUP BY 1)"
        ).fetchone()
        assert totals == (OFFICIAL_POPULATION, OFFICIAL_DWELLINGS), level
    connection.close()
    result = {
        "official_population": population,
        "official_dwellings": dwellings,
        "provinces": len(manzanas),
        "unmatched_real_manzanas": len(unmatched),
        "unmatched_real_manzanas_without_sector_polygon": unassigned_to_sector,
        "minimum_provincial_manzana_match_percent": min(
            float(row["census_match_percent"]) for row in manzanas
        ),
    }
    (INTERIM / "fase0_check.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    public_qa = {
        "source": "INEC CPV 2022, MANLOC CSV; geometrías INEC de sector y respaldo 2021",
        "national": {
            "population": population,
            "dwellings": dwellings,
            "matchable_manzanas": sum(int(row["matchable_manzanas"]) for row in manzanas),
            "matched_manzanas": sum(int(row["matched_manzanas"]) for row in manzanas),
            "unmatched_manzanas": len(unmatched),
        },
        "provinces": [
            {
                "code": row["province"],
                "matched_manzanas": int(row["matched_manzanas"]),
                "matchable_manzanas": int(row["matchable_manzanas"]),
                "manzana_match_percent": float(row["census_match_percent"]),
                "population_match_percent": float(row["population_match_percent"]),
                "dwellings_match_percent": float(row["dwellings_match_percent"]),
                "unmatched_manzanas": int(row["unmatched_manzanas"]),
            }
            for row in manzanas
        ],
    }
    output = ROOT / "web/public/data/fase0_qa.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(public_qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)


def sample_archives() -> None:
    archives = {
        "BDD_CPV2022_MANLOC_CSV.zip": 5,
        "BDD_CPV2022_SECT_CSV.zip": 5,
        "BDD_CPV2022_CANT_CSV.zip": 5,
    }
    for archive_name, expected_tables in archives.items():
        archive = RAW / archive_name
        if not archive.is_file():
            raise FileNotFoundError(f"Run pipeline/fetch_raw.py first: {archive}")
        with ZipFile(archive) as source:
            tables = [name for name in source.namelist() if name.lower().endswith(".csv")]
            assert len(tables) == expected_tables, archive_name
            for table in tables:
                with source.open(table) as stream:
                    header = next(
                        csv.reader([stream.readline().decode("utf-8-sig")], delimiter=";")
                    )
                    sample_size = sum(
                        1 for _, line in zip(range(100), stream, strict=False) if line
                    )
                assert header and sample_size == 100, table
                if "Pobl" in table and archive_name != "BDD_CPV2022_MANLOC_CSV.zip":
                    assert "P11R" in header, table
                print(
                    f"{archive_name}: {Path(table).name}, {len(header)} columns, {sample_size} rows"
                )


if __name__ == "__main__":
    main()
