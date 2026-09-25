"""Pack complete CPV 2022 counts by official census unit without modification.

Input is the ignored complete Phase 1A aggregate artifact, never person rows.
Only the packed Parquet files in OUTPUT are eligible for public release.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import duckdb
from counts_schema import GEOM_VERSION, NUMERIC_FIELDS

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/interim/counts_v1a.duckdb"
FULL = ROOT / "data/interim/full_aggregate_v1a/counts/v1a"
OUTPUT = ROOT / "data/interim/exact_public/counts/v1b1"
PROVINCES = tuple(f"{index:02d}" for index in range(1, 25))
LEVELS = ("finest", "sector", "parroquia", "canton", "provincia", "nacion")
PER_PROVINCE = {"finest", "sector"}
MAX_COUNTS_BYTES = 150_000_000
MAX_FILE_BYTES = 95_000_000


def sqlpath(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def count_type(maximum: int) -> str:
    if maximum <= 255:
        return "UTINYINT"
    if maximum <= 65_535:
        return "USMALLINT"
    if maximum <= 4_294_967_295:
        return "UINTEGER"
    raise ValueError(f"Count exceeds uint32: {maximum}")


def codebook(connection: duckdb.DuckDBPyConnection) -> None:
    destination = OUTPUT / "categories/codebook.parquet"
    destination.parent.mkdir(parents=True, exist_ok=True)
    connection.execute(
        f"""
        COPY (
          SELECT variable_id::UTINYINT AS variable_id,
            category_id::USMALLINT AS category_id,
            source_table,variable,category,
            '{GEOM_VERSION}'::VARCHAR AS geom_version
          FROM publication_codebook
          ORDER BY variable_id,category_id
        ) TO '{sqlpath(destination)}'
        (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
        """
    )


def pack_core(connection: duckdb.DuckDBPyConnection) -> dict[str, dict[str, str]]:
    types = {}
    for level in LEVELS:
        maxima = connection.execute(
            "SELECT " + ",".join(f"MAX({field})" for field in NUMERIC_FIELDS)
            + f" FROM counts_{level}"
        ).fetchone()
        kinds = {
            field: count_type(maximum or 0)
            for field, maximum in zip(NUMERIC_FIELDS, maxima, strict=True)
        }
        types[level] = kinds
        numeric = ",".join(
            f"f.{field}::{kinds[field]} AS {field}" for field in NUMERIC_FIELDS
        )
        for province in PROVINCES if level in PER_PROVINCE else (None,):
            destination = OUTPUT / level / (f"{province}.parquet" if province else "data.parquet")
            destination.parent.mkdir(parents=True, exist_ok=True)
            where = f"WHERE f.province_key='{province}'" if province else ""
            connection.execute(
                f"""
                COPY (
                  SELECT i.unit_index::USMALLINT AS unit_index,
                    f.unit_key,f.unit_level,f.province_key,f.canton_key,
                    f.parish_key,f.sector_key,f.asignado_a_sector,
                    f.sector_disperso,f.geografia_oculta,f.geom_version,
                    {numeric}
                  FROM counts_{level} f
                  JOIN publication_ids_{level} i USING (unit_key)
                  {where}
                  ORDER BY i.unit_index
                ) TO '{sqlpath(destination)}'
                (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
                """
            )
        print(f"exact core {level}", flush=True)
    return types


def category_sources(level: str, province: str | None) -> list[Path]:
    if level == "finest":
        paths = sorted((FULL / "categories/finest").glob(f"*/{province}.parquet"))
        if len(paths) != 5:
            raise FileNotFoundError(f"Five complete fine category sources required: {province}")
        return paths
    if level in {"sector", "parroquia", "canton"}:
        return [FULL / "categories" / level / f"province_key={province}/data_0.parquet"]
    return [FULL / "categories" / level / "data.parquet"]


def pack_categories(connection: duckdb.DuckDBPyConnection) -> dict[str, str]:
    count_types = {}
    for level in LEVELS:
        source_pattern = sqlpath(FULL / "categories" / level / "**/*.parquet")
        maximum = connection.execute(
            f"SELECT MAX(n) FROM read_parquet('{source_pattern}', hive_partitioning=false)"
        ).fetchone()[0]
        kind = count_type(maximum or 0)
        count_types[level] = kind
        provinces = (
            PROVINCES if level in {"finest", "sector", "parroquia", "canton"}
            else (None,)
        )
        for province in provinces:
            destination = OUTPUT / "categories" / level / (
                f"{province}.parquet" if province else "data.parquet"
            )
            destination.parent.mkdir(parents=True, exist_ok=True)
            sources = category_sources(level, province)
            source_sql = ",".join(f"'{sqlpath(path)}'" for path in sources)
            where = f"WHERE i.province_key='{province}'" if province else ""
            connection.execute(
                f"""
                COPY (
                  SELECT i.unit_index::USMALLINT AS unit_index,
                    b.variable_id::UTINYINT AS variable_id,
                    b.category_id::USMALLINT AS category_id,
                    a.n::{kind} AS n,
                    '{GEOM_VERSION}'::VARCHAR AS geom_version
                  FROM read_parquet([{source_sql}], hive_partitioning=false) a
                  JOIN publication_ids_{level} i USING (unit_key)
                  JOIN publication_codebook b
                    ON a.source_table=b.source_table AND a.variable=b.variable
                   AND a.category IS NOT DISTINCT FROM b.category
                  {where}
                  ORDER BY unit_index,variable_id,category_id
                ) TO '{sqlpath(destination)}'
                (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
                """
            )
        print(f"exact categories {level}", flush=True)
    return count_types


def qa(connection: duckdb.DuckDBPyConnection) -> None:
    for level in LEVELS:
        pattern = sqlpath(OUTPUT / level / "*.parquet")
        columns = ",".join(f"SUM({field})::BIGINT" for field in NUMERIC_FIELDS)
        packed = connection.execute(
            f"SELECT COUNT(*),{columns} FROM read_parquet('{pattern}')"
        ).fetchone()
        full = connection.execute(
            f"SELECT COUNT(*),{columns} FROM counts_{level}"
        ).fetchone()
        if packed != full:
            raise AssertionError(f"Core count mismatch at {level}")
        original = sqlpath(FULL / "categories" / level / "**/*.parquet")
        derived = sqlpath(OUTPUT / "categories" / level / "*.parquet")
        before = connection.execute(
            f"SELECT COUNT(*),SUM(n)::BIGINT FROM read_parquet('{original}', "
            "hive_partitioning=false)"
        ).fetchone()
        after = connection.execute(
            f"SELECT COUNT(*),SUM(n)::BIGINT FROM read_parquet('{derived}')"
        ).fetchone()
        if before != after:
            raise AssertionError(f"Category count mismatch at {level}: {before} != {after}")
    print("Exact aggregate QA passed for every level", flush=True)


def deduplicate_sector_categories(connection: duckdb.DuckDBPyConnection) -> None:
    """Keep sector-only variables; other sector counts equal fine roll-ups."""
    schema = json.loads((FULL / "categories/schema.json").read_text(encoding="utf-8"))
    sector_only = connection.execute(
        "SELECT DISTINCT source_table,variable FROM publication_codebook "
        "WHERE source_table='poblacion_sector'"
    ).fetchall()
    if sector_only != [("poblacion_sector", "P11R")]:
        raise ValueError(f"Unexpected sector-only variables: {sector_only}")
    if any("sector" in levels for levels in schema["fields"].values()):
        raise ValueError("Additional sector-only variables need explicit storage")
    for province in PROVINCES:
        source = sqlpath(OUTPUT / "categories/sector" / f"{province}.parquet")
        destination = OUTPUT / "categories/sector_only" / f"{province}.parquet"
        destination.parent.mkdir(parents=True, exist_ok=True)
        connection.execute(
            f"""
            COPY (
              SELECT c.unit_index,c.variable_id,c.category_id,c.n,c.geom_version
              FROM read_parquet('{source}') c
              JOIN publication_codebook b
                ON c.variable_id=b.variable_id AND c.category_id=b.category_id
              WHERE b.source_table='poblacion_sector'
              ORDER BY c.unit_index,c.variable_id,c.category_id
            ) TO '{sqlpath(destination)}'
            (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
            """
        )
    target = (OUTPUT / "categories/sector").resolve()
    if not target.is_relative_to((ROOT / "data/interim").resolve()):
        raise ValueError("Unsafe sector deduplication target")
    shutil.rmtree(target)


def main() -> None:
    if not DB.is_file() or not (FULL / "qa.json").is_file():
        raise FileNotFoundError("Restore complete Phase 1A aggregates first")
    if OUTPUT.exists():
        resolved = OUTPUT.resolve()
        if not resolved.is_relative_to((ROOT / "data/interim").resolve()):
            raise ValueError("Unsafe exact output path")
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)
    connection = duckdb.connect(str(DB), read_only=True)
    connection.execute("SET memory_limit='4GB'")
    temp = ROOT / "data/interim/exact_pack_temp"
    temp.mkdir(parents=True, exist_ok=True)
    connection.execute(f"SET temp_directory='{sqlpath(temp)}'")
    codebook(connection)
    types = pack_core(connection)
    category_types = pack_categories(connection)
    qa(connection)
    deduplicate_sector_categories(connection)
    connection.close()
    metadata = {
        "schema_version": 3,
        "geom_version": GEOM_VERSION,
        "publication": "exact official INEC census units",
        "numeric_types": types,
        "category_count_types": category_types,
        "sector_categories": "exact roll-up from finest, plus categories/sector_only/P11R",
        "small_area_policy": "warning only; no suppression or perturbation",
    }
    (OUTPUT / "schema.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    shutil.copy2(FULL / "qa.json", OUTPUT / "qa.json")
    files = [path for path in OUTPUT.rglob("*") if path.is_file()]
    total = sum(path.stat().st_size for path in files)
    maximum = max(path.stat().st_size for path in files)
    print(f"Exact package: {len(files)} files, {total} bytes, max {maximum}")
    if total > MAX_COUNTS_BYTES or maximum > MAX_FILE_BYTES:
        raise ValueError("Exact package exceeds 150 MB or 95 MB file budget")


if __name__ == "__main__":
    main()
