"""Roll up exact official sector aggregates to census zone I04.

Only sector aggregate Parquet files are read. No census person, household or
dwelling record enters this process. The nine-digit key is I01..I04.
"""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pyarrow.parquet as pq
from counts_schema import NUMERIC_FIELDS

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "data/interim/exact_public/counts/v1b1"
CROSS = ROOT / "data/interim/cross_counts_v1b2"
FULL = ROOT / "data/interim/full_aggregate_v1a/counts/v1a/categories"
PUBLIC = ROOT / "web/public/data"
GEOM_VERSION = "marco-2021"


def quoted(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def count_type(maximum: int) -> str:
    if maximum <= 255:
        return "UTINYINT"
    if maximum <= 65_535:
        return "USMALLINT"
    if maximum <= 4_294_967_295:
        return "UINTEGER"
    raise ValueError(f"Count exceeds uint32: {maximum}")


def build() -> dict:
    sector_core = quoted(CORE / "sector/*.parquet")
    sector_cross = quoted(CROSS / "sector/data.parquet")
    sector_categories = quoted(FULL / "sector/province_key=*/*.parquet")
    connection = duckdb.connect()
    connection.execute(f"CREATE VIEW sector AS SELECT * FROM read_parquet('{sector_core}')")
    sums = ",".join(f"SUM({field})::BIGINT AS {field}" for field in NUMERIC_FIELDS)
    connection.execute(f"""
        CREATE TABLE zone_core AS
        SELECT zone_key AS unit_key, 'zona' AS unit_level,
          LEFT(zone_key,2) AS province_key, LEFT(zone_key,4) AS canton_key,
          LEFT(zone_key,6) AS parish_key, NULL::VARCHAR AS sector_key,
          BOOL_OR(asignado_a_sector) AS asignado_a_sector,
          BOOL_OR(sector_disperso) AS sector_disperso,
          BOOL_OR(geografia_oculta) AS geografia_oculta,
          '{GEOM_VERSION}' AS geom_version,{sums}
        FROM (SELECT LEFT(unit_key,9) AS zone_key,* FROM sector)
        GROUP BY zone_key
    """)
    fields = {name: count_type(connection.execute(
        f"SELECT MAX({name}) FROM zone_core").fetchone()[0] or 0)
        for name in NUMERIC_FIELDS}
    numeric = ",".join(f"z.{name}::{kind} AS {name}" for name, kind in fields.items())
    target = CORE / "zona/data.parquet"
    target.parent.mkdir(parents=True, exist_ok=True)
    connection.execute(f"""
        COPY (SELECT (ROW_NUMBER() OVER (ORDER BY unit_key)-1)::USMALLINT AS unit_index,
          z.unit_key,z.unit_level,z.province_key,z.canton_key,z.parish_key,
          z.sector_key,z.asignado_a_sector,z.sector_disperso,z.geografia_oculta,
          z.geom_version,{numeric} FROM zone_core z ORDER BY z.unit_key)
        TO '{quoted(target)}' (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
    """)
    cross_schema = pq.read_schema(CROSS / "sector/data.parquet")
    cross_fields = [name for name in cross_schema.names if name not in
                    {"unit_key", "geom_version"}]
    cross_sums = ",".join(f"SUM({name})::BIGINT AS {name}" for name in cross_fields)
    connection.execute(f"""
        CREATE TABLE zone_cross AS SELECT LEFT(unit_key,9) AS unit_key,
          '{GEOM_VERSION}' AS geom_version,{cross_sums}
        FROM read_parquet('{sector_cross}') GROUP BY LEFT(unit_key,9)
    """)
    cross_kinds = {name: count_type(connection.execute(
        f"SELECT MAX({name}) FROM zone_cross").fetchone()[0] or 0)
        for name in cross_fields}
    cross_casts = ",".join(f"{name}::{kind} AS {name}"
                           for name, kind in cross_kinds.items())
    cross_target = CROSS / "zona/data.parquet"
    cross_target.parent.mkdir(parents=True, exist_ok=True)
    connection.execute(f"""
        COPY (SELECT unit_key,geom_version,{cross_casts} FROM zone_cross
          ORDER BY unit_key) TO '{quoted(cross_target)}'
          (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
    """)
    connection.execute(f"""
        CREATE TABLE zone_categories AS
        SELECT zone_key AS unit_key, 'zona' AS unit_level,
          LEFT(zone_key,4) AS canton_key, LEFT(zone_key,6) AS parish_key,
          NULL::VARCHAR AS sector_key, source_table,variable,category,
          SUM(n)::BIGINT AS n, '{GEOM_VERSION}' AS geom_version
        FROM (SELECT LEFT(unit_key,9) AS zone_key,* FROM
          read_parquet('{sector_categories}', hive_partitioning=false))
        GROUP BY zone_key,source_table,variable,category
    """)
    raw_category = FULL / "zona/data.parquet"
    raw_category.parent.mkdir(parents=True, exist_ok=True)
    connection.execute(f"""
        COPY (SELECT * FROM zone_categories ORDER BY unit_key,source_table,
          variable,category) TO '{quoted(raw_category)}'
          (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
    """)
    codebook = quoted(CORE / "categories/codebook.parquet")
    connection.execute(f"""
        CREATE VIEW category_ids AS SELECT z.unit_index,z.unit_key,b.variable_id,
          b.category_id,c.n,z.geom_version
        FROM zone_categories c JOIN read_parquet('{quoted(target)}') z USING(unit_key)
        JOIN read_parquet('{codebook}') b
          ON c.source_table=b.source_table AND c.variable=b.variable
         AND c.category IS NOT DISTINCT FROM b.category
    """)
    category_max = connection.execute("SELECT MAX(n) FROM category_ids").fetchone()[0] or 0
    category_target = CORE / "categories/zona/data.parquet"
    category_target.parent.mkdir(parents=True, exist_ok=True)
    connection.execute(f"""
        COPY (SELECT unit_index,variable_id,category_id,
          n::{count_type(category_max)} AS n,geom_version FROM category_ids
          ORDER BY unit_index,variable_id,category_id)
        TO '{quoted(category_target)}'
        (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
    """)
    population = connection.execute("SELECT SUM(population) FROM zone_core").fetchone()[0]
    sector_population = connection.execute("SELECT SUM(population) FROM sector").fetchone()[0]
    if population != sector_population:
        raise AssertionError("Zone population differs from sector population")
    for field in NUMERIC_FIELDS:
        zone = connection.execute(f"SELECT SUM({field}) FROM zone_core").fetchone()[0]
        sector = connection.execute(f"SELECT SUM({field}) FROM sector").fetchone()[0]
        if zone != sector:
            raise AssertionError(f"Zone roll-up differs for {field}: {zone} != {sector}")
    raw = connection.execute("SELECT SUM(n) FROM zone_categories").fetchone()[0]
    packed = connection.execute("SELECT SUM(n) FROM category_ids").fetchone()[0]
    if raw != packed:
        raise AssertionError(f"Zone category codebook join lost cells: {raw} != {packed}")
    schema_path = CORE / "schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema["numeric_types"]["zona"] = fields
    schema["category_count_types"]["zona"] = count_type(category_max)
    schema_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    result = {"zones": connection.execute("SELECT COUNT(*) FROM zone_core").fetchone()[0],
              "population": population, "category_rows": connection.execute(
                  "SELECT COUNT(*) FROM zone_categories").fetchone()[0],
              "bytes": {name: path.stat().st_size for name, path in {
                  "core": target, "cross": cross_target,
                  "categories": category_target}.items()}}
    print(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == "__main__":
    build()
