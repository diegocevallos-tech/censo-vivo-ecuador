"""Sparse additive category counts for the available CPV 2022 variables."""

from __future__ import annotations

import csv
import json
import re
import shutil
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import duckdb
from counts_schema import GEOM_VERSION

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data/interim"
PUBLIC = ROOT / "web/public/data/counts/v1a/categories"
SECTOR_ZIP = ROOT / "data/raw/BDD_CPV2022_SECT_CSV.zip"
HIGH_CARDINALITY = {
    "P08P", "P08C", "P08Q", "P0803A", "P09P", "P09C", "P09Q", "P1001I"
}
DERIVED = {
    "poblacion": {
        "AUR", "GEDAD", "GRANEDAD", "ETAEDAD", "DFUNC", "TDFUNC", "ESCOLA",
        "ANALF", "ANALF_DIG", "CONDACT", "CONDACT1", "GRUPO1", "RAMA1",
        "NBI", "IMP_VOPA", "IMP_NN"
    },
    "vivienda": {"AUR", "TOTFALL", "TOTEMI", "TOTPER", "DEF_HAB", "IMP_VOPA"},
    "hogar": {"AUR", "HAC", "NBI", "TIPO_HOGAR", "IMP_VOPA"},
    "emigracion": {"AUR"},
    "mortalidad": {"AUR"},
}
PREFIX = {
    "poblacion": "P", "vivienda": "V", "hogar": "H",
    "emigracion": "E", "mortalidad": "M"
}
EXCLUDE = {"P00", "P03", "E00", "M00"}
BATCH = 8


def quote(path: Path) -> str:
    return path.as_posix().replace("'", "''")


def field_sets(connection: duckdb.DuckDBPyConnection, table: str) -> tuple[list[str], list[str]]:
    fields = [
        row[0] for row in connection.execute(f"DESCRIBE SELECT * FROM {table}_units").fetchall()
    ]
    selected = [
        field for field in fields
        if (re.fullmatch(rf"{PREFIX[table]}[0-9][A-Z0-9_]*", field)
            or field in DERIVED[table])
        and field not in EXCLUDE
    ]
    fine = [field for field in selected if field not in HIGH_CARDINALITY]
    coarse = [field for field in selected if field in HIGH_CARDINALITY]
    return fine, coarse


def build_fine(
    connection: duckdb.DuckDBPyConnection, field_catalog: dict[str, dict[str, list[str]]]
) -> None:
    provinces = [row[0] for row in connection.execute(
        "SELECT unit_key FROM counts_provincia ORDER BY unit_key"
    ).fetchall()]
    scratch = INTERIM / "category_parts"
    if scratch.exists():
        if not scratch.resolve().is_relative_to(INTERIM.resolve()):
            raise ValueError("Unsafe category scratch path")
        shutil.rmtree(scratch)
    for table in PREFIX:
        fields = field_catalog[table]["manzana"]
        for province in provinces:
            parts = scratch / table / province
            parts.mkdir(parents=True, exist_ok=True)
            for offset in range(0, len(fields), BATCH):
                batch = fields[offset : offset + BATCH]
                source_columns = ", ".join(batch)
                target = parts / f"{offset // BATCH:02d}.parquet"
                connection.execute(
                    f"""
                    COPY (
                      SELECT unit_key,
                        CASE WHEN LENGTH(unit_key) = 15 THEN 'manzana'
                             WHEN BOOL_OR(rural) THEN 'sector_disperso'
                             ELSE 'sector' END AS unit_level,
                        province_key, canton_key, parish_key, sector_key,
                        '{table}'::VARCHAR AS source_table,
                        variable::VARCHAR AS variable,
                        category::VARCHAR AS category,
                        COUNT(*)::BIGINT AS n,
                        '{GEOM_VERSION}'::VARCHAR AS geom_version
                      FROM (
                        SELECT unit_key, province_key, canton_key, parish_key,
                               sector_key, rural, {source_columns}
                        FROM {table}_units WHERE province_key = '{province}'
                      ) UNPIVOT (category FOR variable IN ({source_columns}))
                      GROUP BY unit_key, province_key, canton_key, parish_key,
                               sector_key, variable, category
                    ) TO '{quote(target)}' (FORMAT PARQUET, COMPRESSION ZSTD)
                    """
                )
            output = PUBLIC / "finest" / table
            output.mkdir(parents=True, exist_ok=True)
            target = output / f"{province}.parquet"
            connection.execute(
                f"COPY (SELECT * FROM read_parquet('{quote(parts / '*.parquet')}')) "
                f"TO '{quote(target)}' (FORMAT PARQUET, COMPRESSION ZSTD)"
            )
            print(f"categories {table} province {province}", flush=True)
    shutil.rmtree(scratch)


def build_coarse(
    connection: duckdb.DuckDBPyConnection, field_catalog: dict[str, dict[str, list[str]]]
) -> None:
    fields = field_catalog["poblacion"]["canton"]
    source_columns = ", ".join(fields)
    destination = PUBLIC / "canton_only"
    destination.mkdir(parents=True, exist_ok=True)
    for (province,) in connection.execute(
        "SELECT unit_key FROM counts_provincia ORDER BY unit_key"
    ).fetchall():
        target = destination / f"{province}.parquet"
        connection.execute(
            f"""
            COPY (
              SELECT canton_key AS unit_key, 'canton'::VARCHAR AS unit_level,
                province_key, canton_key, NULL::VARCHAR AS parish_key,
                NULL::VARCHAR AS sector_key,
                'poblacion'::VARCHAR AS source_table,
                variable::VARCHAR AS variable, category::VARCHAR AS category,
                COUNT(*)::BIGINT AS n,
                '{GEOM_VERSION}'::VARCHAR AS geom_version
              FROM (
                SELECT province_key, canton_key, {source_columns}
                FROM poblacion_units WHERE province_key = '{province}'
              ) UNPIVOT (category FOR variable IN ({source_columns}))
              GROUP BY canton_key, province_key, variable, category
            ) TO '{quote(target)}' (FORMAT PARQUET, COMPRESSION ZSTD)
            """
        )


def build_ethnicity(connection: duckdb.DuckDBPyConnection) -> None:
    if not SECTOR_ZIP.is_file():
        raise FileNotFoundError(SECTOR_ZIP)
    with ZipFile(SECTOR_ZIP) as archive:
        members = [name for name in archive.namelist() if "Pobl" in name and name.endswith(".csv")]
        if len(members) != 1:
            raise ValueError(f"Expected one official SECTOR population CSV: {members}")
        counts: Counter[tuple[str, str]] = Counter()
        total = 0
        with archive.open(members[0]) as stream:
            header = stream.readline().decode("utf-8-sig").strip().split(";")
            if header[:5] != ["I01", "I02", "I03", "I04", "I05"]:
                raise ValueError("Unexpected sector geography columns")
            index = header.index("P11R")
            for line in stream:
                fields = line.split(b";", index + 1)
                if len(fields) <= index:
                    raise ValueError("Malformed sector P11R row")
                sector_key = b"".join(fields[:5]).decode("ascii")
                category = fields[index].decode("utf-8").strip()
                counts[(sector_key, category)] += 1
                total += 1
    if total != 16_938_986:
        raise AssertionError(f"Official SECTOR population rows changed: {total}")
    interim_csv = INTERIM / "ethnicity_sector_counts.csv"
    with interim_csv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["sector_key", "category", "n"])
        writer.writerows((sector, category, n) for (sector, category), n in counts.items())
    target = PUBLIC / "sector_only" / "ethnicity.parquet"
    target.parent.mkdir(parents=True, exist_ok=True)
    connection.execute(
        f"""
        COPY (
          SELECT sector_key AS unit_key, 'sector'::VARCHAR AS unit_level,
            SUBSTR(sector_key,1,2) AS province_key,
            SUBSTR(sector_key,1,4) AS canton_key,
            SUBSTR(sector_key,1,6) AS parish_key,
            sector_key, 'poblacion_sector'::VARCHAR AS source_table,
            'P11R'::VARCHAR AS variable,
            NULLIF(category,'') AS category,
            n::BIGINT AS n, '{GEOM_VERSION}'::VARCHAR AS geom_version
          FROM read_csv('{quote(interim_csv)}', all_varchar=true)
        ) TO '{quote(target)}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )
    print(f"sector ethnicity: {len(counts)} aggregate rows, {total} persons", flush=True)


def rollup(connection: duckdb.DuckDBPyConnection) -> None:
    fine = quote(PUBLIC / "finest/**/*.parquet")
    ethnic = quote(PUBLIC / "sector_only/ethnicity.parquet")
    coarse = quote(PUBLIC / "canton_only/*.parquet")
    specs = {
        "sector": ("sector_key", [fine, ethnic]),
        "parroquia": ("parish_key", [fine, ethnic]),
        "canton": ("canton_key", [fine, ethnic, coarse]),
        "provincia": ("province_key", [fine, ethnic, coarse]),
        "nacion": ("'EC'", [fine, ethnic, coarse]),
    }
    for level, (key, sources) in specs.items():
        paths = ",".join(f"'{path}'" for path in sources)
        result = PUBLIC / level
        result.mkdir(parents=True, exist_ok=True)
        partition = (
            ", PARTITION_BY (province_key)"
            if level in {"sector", "parroquia", "canton"} else ""
        )
        target = result if partition else result / "data.parquet"
        connection.execute(
            f"""
            COPY (
              SELECT {key} AS unit_key, '{level}'::VARCHAR AS unit_level,
                CASE WHEN '{level}' = 'nacion' THEN NULL
                     ELSE MIN(province_key) END AS province_key,
                CASE WHEN '{level}' IN ('nacion','provincia') THEN NULL
                     ELSE MIN(canton_key) END AS canton_key,
                CASE WHEN '{level}' IN ('nacion','provincia','canton') THEN NULL
                     ELSE MIN(parish_key) END AS parish_key,
                CASE WHEN '{level}' = 'sector' THEN MIN(sector_key)
                     ELSE NULL END AS sector_key,
                source_table, variable, category, SUM(n)::BIGINT AS n,
                '{GEOM_VERSION}'::VARCHAR AS geom_version
              FROM read_parquet([{paths}], union_by_name=true,
                                hive_partitioning=false)
              WHERE {key} IS NOT NULL
              GROUP BY {key}, source_table, variable, category
            ) TO '{quote(target)}' (FORMAT PARQUET, COMPRESSION ZSTD{partition})
            """
        )
        print(f"categories {level}: {len(list(result.rglob('*.parquet')))} files", flush=True)


def build(connection: duckdb.DuckDBPyConnection) -> None:
    if PUBLIC.exists():
        if not PUBLIC.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("Unsafe public category output path")
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir(parents=True)
    catalog = {}
    for table in PREFIX:
        fine, coarse = field_sets(connection, table)
        catalog[table] = {"manzana": fine, "canton": coarse}
    build_fine(connection, catalog)
    build_coarse(connection, catalog)
    build_ethnicity(connection)
    rollup(connection)
    files = list(PUBLIC.rglob("*.parquet"))
    metadata = {
        "geom_version": GEOM_VERSION,
        "fields": catalog,
        "ethnicity": {"variable": "P11R", "min_level": "sector"},
        "bytes": sum(path.stat().st_size for path in files),
        "files": len(files),
    }
    (PUBLIC / "schema.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"category output: {metadata['files']} files, {metadata['bytes']} bytes", flush=True)
