"""Build additive geographic counts without publishing individual records.

The verified 2021 match list controls the only geometry-dependent decision:
real census manzanas lacking a polygon are carried in their matching sector.
Changing the displayed geometry later does not change any source count.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import duckdb
from category_counts import build as build_categories
from counts_schema import AGE_LABELS, GEOM_VERSION, NUMERIC_FIELDS

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data/interim"
FILTERED = INTERIM / "filtered"
PUBLIC = ROOT / "web/public/data/counts/v1a"
UNMATCHED = ROOT / "docs/qa/manzanas_sin_match.csv"
DB = INTERIM / "counts_v1a.duckdb"
TABLES = ("poblacion", "vivienda", "hogar", "emigracion", "mortalidad")
EVENT_FIELDS = {
    "poblacion": ("population", "assigned_population"),
    "vivienda": ("dwellings", "assigned_dwellings"),
    "hogar": ("households", "assigned_households"),
    "emigracion": ("emigrants", "assigned_emigrants"),
    "mortalidad": ("deaths", "assigned_deaths"),
}


def safe_reset(path: Path) -> None:
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT.resolve()) or resolved in {
        ROOT.resolve(), INTERIM.resolve()
    }:
        raise ValueError(f"Unsafe output path: {resolved}")
    if resolved.is_dir():
        shutil.rmtree(resolved)
    elif resolved.exists():
        resolved.unlink()


def make_unit_view(connection: duckdb.DuckDBPyConnection, table: str) -> None:
    pattern = (FILTERED / table / "**/*.parquet").as_posix().replace("'", "''")
    connection.execute(
        f"""
        CREATE OR REPLACE VIEW {table}_units AS
        WITH source AS (
          SELECT *, I01 || I02 || I03 || I04 || I05 AS sector_key,
                 I01 || I02 || I03 || I04 || I05 || I06 AS manzana_key
          FROM read_parquet('{pattern}', hive_partitioning=true,
                            hive_types={{'I01':'VARCHAR'}})
        ), assigned AS (
          SELECT source.*, u.clave_manzana IS NOT NULL AS assigned,
                 I06 IS NULL OR I06 = '' AS rural,
                 COALESCE(I04 = '888', false) OR COALESCE(I05 = '888', false)
                   OR COALESCE(I06 = '888', false) AS masked,
                 I06 IS NOT NULL AND I06 <> '' AND I06 <> '888'
                   AND COALESCE(I04 <> '888', false)
                   AND COALESCE(I05 <> '888', false)
                   AND u.clave_manzana IS NULL AS has_polygon
          FROM source
          LEFT JOIN unmatched u ON source.manzana_key = u.clave_manzana
        )
        SELECT assigned.*,
          CASE WHEN has_polygon THEN manzana_key ELSE sector_key END AS unit_key,
          I01 AS province_key, I01 || I02 AS canton_key,
          I01 || I02 || I03 AS parish_key,
          {"TRY_CAST(P03 AS INTEGER) AS age, P02 AS sex," if table == 'poblacion' else ''}
          '{GEOM_VERSION}'::VARCHAR AS source_geom_version
        FROM assigned
        """
    )


def source_aggregate_sql(table: str) -> str:
    event_field, assigned_field = EVENT_FIELDS[table]
    expressions: dict[str, str] = {
        event_field: "COUNT(*)::BIGINT",
        assigned_field: "COUNT(*) FILTER (WHERE assigned)::BIGINT",
    }
    if table == "poblacion":
        expressions.update(
            {
                "rural_population": "COUNT(*) FILTER (WHERE rural)::BIGINT",
                "masked_population": "COUNT(*) FILTER (WHERE masked)::BIGINT",
                "sex_male": "COUNT(*) FILTER (WHERE sex = '1')::BIGINT",
                "sex_female": "COUNT(*) FILTER (WHERE sex = '2')::BIGINT",
                "sex_unknown": (
                    "COUNT(*) FILTER (WHERE sex NOT IN ('1','2') "
                    "OR sex IS NULL)::BIGINT"
                ),
                "age_sex_unknown": (
                    "COUNT(*) FILTER (WHERE age NOT BETWEEN 0 AND 120 OR age IS NULL "
                    "OR sex NOT IN ('1','2') OR sex IS NULL)::BIGINT"
                ),
            }
        )
        for index, label in enumerate(AGE_LABELS):
            condition = f"age BETWEEN {index * 5} AND {index * 5 + 4}"
            if index == 20:
                condition = "age BETWEEN 100 AND 120"
            for sex_code, suffix in (("1", "m"), ("2", "f")):
                expressions[f"age_{label}_{suffix}"] = (
                    f"COUNT(*) FILTER (WHERE {condition} AND sex = '{sex_code}')::BIGINT"
                )
    values = ",\n          ".join(
        f"{expressions.get(field, '0::BIGINT')} AS {field}" for field in NUMERIC_FIELDS
    )
    return f"""
      SELECT unit_key, province_key, canton_key, parish_key, sector_key,
             BOOL_OR(assigned) AS assigned_flag,
             BOOL_OR(rural) AS rural_flag,
             BOOL_OR(masked) AS masked_flag,
             {values}
      FROM {table}_units
      GROUP BY ALL
    """


def assignment_sql() -> str:
    values = ",\n          ".join(
        f"{'1::BIGINT' if field == 'assigned_manzanas' else '0::BIGINT'} AS {field}"
        for field in NUMERIC_FIELDS
    )
    return f"""
      SELECT clave_sector AS unit_key, SUBSTR(clave_sector,1,2) AS province_key,
             SUBSTR(clave_sector,1,4) AS canton_key,
             SUBSTR(clave_sector,1,6) AS parish_key,
             clave_sector AS sector_key, true AS assigned_flag,
             false AS rural_flag, false AS masked_flag,
             {values}
      FROM unmatched
    """


def create_counts(connection: duckdb.DuckDBPyConnection) -> None:
    queries = [source_aggregate_sql(table) for table in TABLES]
    queries.append(assignment_sql())
    union = "\nUNION ALL\n".join(queries)
    sums = ",\n          ".join(f"SUM({field})::BIGINT AS {field}" for field in NUMERIC_FIELDS)
    connection.execute(
        f"""
        CREATE OR REPLACE TABLE counts_finest AS
        SELECT unit_key,
          CASE WHEN LENGTH(unit_key) = 15 THEN 'manzana'
               WHEN BOOL_OR(rural_flag) THEN 'sector_disperso'
               ELSE 'sector' END AS unit_level,
          MIN(province_key) AS province_key,
          MIN(canton_key) AS canton_key,
          MIN(parish_key) AS parish_key,
          MIN(sector_key) AS sector_key,
          BOOL_OR(assigned_flag) AS asignado_a_sector,
          BOOL_OR(rural_flag) AS sector_disperso,
          BOOL_OR(masked_flag) AS geografia_oculta,
          '{GEOM_VERSION}'::VARCHAR AS geom_version,
          {sums}
        FROM ({union})
        GROUP BY unit_key
        """
    )
    level_specs = {
        "sector": ("sector_key", "sector"),
        "parroquia": ("parish_key", "parroquia"),
        "canton": ("canton_key", "canton"),
        "provincia": ("province_key", "provincia"),
        "nacion": ("'EC'", "nacion"),
    }
    for table, (key, level) in level_specs.items():
        sums = ",\n          ".join(f"SUM({field})::BIGINT AS {field}" for field in NUMERIC_FIELDS)
        connection.execute(
            f"""
            CREATE OR REPLACE TABLE counts_{table} AS
            SELECT {key} AS unit_key, '{level}'::VARCHAR AS unit_level,
              CASE WHEN '{level}' = 'nacion' THEN NULL ELSE MIN(province_key) END
                AS province_key,
              CASE WHEN '{level}' IN ('nacion','provincia') THEN NULL
                   ELSE MIN(canton_key) END AS canton_key,
              CASE WHEN '{level}' IN ('nacion','provincia','canton') THEN NULL
                   ELSE MIN(parish_key) END AS parish_key,
              CASE WHEN '{level}' = 'sector' THEN MIN(sector_key)
                   ELSE NULL END AS sector_key,
              BOOL_OR(asignado_a_sector) AS asignado_a_sector,
              BOOL_OR(sector_disperso) AS sector_disperso,
              BOOL_OR(geografia_oculta) AS geografia_oculta,
              '{GEOM_VERSION}'::VARCHAR AS geom_version,
              {sums}
            FROM counts_finest
            GROUP BY {key}
            """
        )


def publish(connection: duckdb.DuckDBPyConnection) -> None:
    safe_reset(PUBLIC)
    PUBLIC.mkdir(parents=True)
    levels = ("finest", "sector", "parroquia", "canton", "provincia", "nacion")
    manifest = {"geom_version": GEOM_VERSION, "levels": {}}
    for level in levels:
        table = f"counts_{level}"
        destination = PUBLIC / level
        destination.mkdir()
        partition = ", PARTITION_BY (province_key)" if level in {"finest", "sector"} else ""
        target = destination if partition else destination / "data.parquet"
        connection.execute(
            f"COPY {table} TO '{target.as_posix()}' "
            f"(FORMAT PARQUET, COMPRESSION ZSTD{partition})"
        )
        files = list(destination.rglob("*.parquet"))
        rows = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        manifest["levels"][level] = {
            "rows": rows,
            "files": len(files),
            "bytes": sum(path.stat().st_size for path in files),
        }
        print(f"{level}: {rows} units, {len(files)} files", flush=True)
    (PUBLIC / "schema.json").write_text(
        json.dumps(
            {
                "geom_version": GEOM_VERSION,
                "numeric_count_fields": NUMERIC_FIELDS,
                "age_groups": AGE_LABELS,
                "levels": manifest["levels"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (INTERIM / "counts_v1a_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    if not UNMATCHED.is_file():
        raise FileNotFoundError(UNMATCHED)
    for table in TABLES:
        if not list((FILTERED / table).rglob("*.parquet")):
            raise FileNotFoundError(f"Run 01_filter_to_parquet.py first: {table}")
    if DB.exists():
        safe_reset(DB)
    connection = duckdb.connect(str(DB))
    connection.execute("SET memory_limit = '4GB'")
    connection.execute(f"SET temp_directory = '{(INTERIM / 'duckdb_temp').as_posix()}'")
    connection.execute(
        f"CREATE OR REPLACE TABLE unmatched AS SELECT * FROM read_csv("
        f"'{UNMATCHED.as_posix()}', all_varchar=true)"
    )
    assert connection.execute("SELECT COUNT(*) FROM unmatched").fetchone()[0] == 1_852
    for table in TABLES:
        make_unit_view(connection, table)
    create_counts(connection)
    publish(connection)
    build_categories(connection)
    connection.close()


if __name__ == "__main__":
    main()
