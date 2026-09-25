"""Convert verified MANLOC CSV tables to private, province-partitioned Parquet.

These files still contain individual records. They remain under gitignored
``data/interim`` and must never be copied to ``web/public/data``.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from zipfile import ZipFile

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw"
INTERIM = ROOT / "data/interim"
ARCHIVE = RAW / "BDD_CPV2022_MANLOC_CSV.zip"
PREFIX = "1.3 BDD_CPV_2022_MANLOC_CSV"
TABLES = {
    "poblacion": "CPV_2022_Poblacion_Manloc.csv",
    "vivienda": "CPV_2022_Vivienda_Manloc.csv",
    "hogar": "CPV_2022_Hogar_Manloc.csv",
    "emigracion": "CPV_2022_Emigracion_Manloc.csv",
    "mortalidad": "CPV_2022_Mortalidad_Manloc.csv",
}
GEOM_VERSION = "marco-2021"


def source_csv(filename: str) -> Path:
    target = RAW / PREFIX / filename
    if target.is_file():
        return target
    if not ARCHIVE.is_file():
        raise FileNotFoundError(f"Restore the verified private Release first: {ARCHIVE}")
    target.parent.mkdir(parents=True, exist_ok=True)
    member = f"{PREFIX}/{filename}"
    partial = target.with_suffix(".partial")
    with ZipFile(ARCHIVE) as archive, archive.open(member) as source:
        with partial.open("wb") as destination:
            shutil.copyfileobj(source, destination, length=8 * 1024 * 1024)
    partial.replace(target)
    return target


def safe_remove_directory(path: Path) -> None:
    resolved = path.resolve()
    if not resolved.is_relative_to(INTERIM.resolve()) or resolved == INTERIM.resolve():
        raise ValueError(f"Refusing to remove directory outside data/interim: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


def main() -> None:
    output_root = INTERIM / "filtered"
    output_root.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect()
    result = {"geom_version": GEOM_VERSION, "tables": {}}
    for name, filename in TABLES.items():
        csv_path = source_csv(filename).as_posix().replace("'", "''")
        output = output_root / name
        safe_remove_directory(output)
        connection.execute(
            f"""
            COPY (
              SELECT *, '{GEOM_VERSION}'::VARCHAR AS geom_version
              FROM read_csv('{csv_path}', delim=';', header=true,
                            all_varchar=true, ignore_errors=false)
            ) TO '{output.as_posix()}'
            (FORMAT PARQUET, COMPRESSION ZSTD, PARTITION_BY (I01))
            """
        )
        files = sorted(output.rglob("*.parquet"))
        if not files:
            raise ValueError(f"No Parquet partitions written for {name}")
        parquet_glob = (output / "**/*.parquet").as_posix().replace("'", "''")
        rows, provinces = connection.execute(
            f"SELECT COUNT(*), COUNT(DISTINCT I01) FROM read_parquet('{parquet_glob}')"
        ).fetchone()
        if provinces != 24:
            raise ValueError(f"Expected 24 provinces in {name}, found {provinces}")
        result["tables"][name] = {"rows": rows, "files": len(files)}
        print(f"{name}: {rows} rows, {len(files)} private Parquet files", flush=True)
    if result["tables"]["poblacion"]["rows"] != 16_938_986:
        raise ValueError("Population row count differs from the official national total")
    if result["tables"]["vivienda"]["rows"] != 6_611_555:
        raise ValueError("Dwelling row count differs from the official national total")
    (INTERIM / "filtered_manifest.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
