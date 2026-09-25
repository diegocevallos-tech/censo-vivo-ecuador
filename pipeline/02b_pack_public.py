"""Publish compact geographic aggregates with primary and secondary suppression.

The complete, additive inputs remain local until every packed file passes QA.
Only this script's compact output is promoted to the public Release.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import duckdb
from counts_schema import GEOM_VERSION, NUMERIC_FIELDS

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data/interim"
DB = INTERIM / "counts_v1a.duckdb"
FULL = ROOT / "web/public/data/counts/v1a"
PACKED = INTERIM / "packed_public/counts/v1a"
DETAIL_FIELDS = [
    field for field in NUMERIC_FIELDS
    if field not in {"population", "dwellings", "households"}
]
LEVELS = ("finest", "sector", "parroquia", "canton", "provincia", "nacion")
PROVINCES = tuple(f"{n:02d}" for n in range(1, 25))
MAX_COUNTS_BYTES = 150_000_000
MAX_FILE_BYTES = 95_000_000


def sqlpath(path: Path) -> str:
    return path.as_posix().replace("'", "''")


def safe_remove(path: Path, parent: Path) -> None:
    resolved = path.resolve()
    boundary = parent.resolve()
    if not resolved.is_relative_to(boundary) or resolved == boundary:
        raise ValueError(f"Unsafe directory removal: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


def count_type(maximum: int) -> str:
    if maximum <= 255:
        return "UTINYINT"
    if maximum <= 65_535:
        return "USMALLINT"
    if maximum <= 4_294_967_295:
        return "UINTEGER"
    raise ValueError(f"Count exceeds uint32: {maximum}")


def prepare(connection: duckdb.DuckDBPyConnection) -> tuple[dict[str, str], dict[str, str]]:
    connection.execute(
        """
        CREATE OR REPLACE TABLE privacy_units AS
        WITH occupied AS (
          SELECT unit_key,
            COUNT(*) FILTER (WHERE V0201 IN ('1','2') OR V0202='1')::BIGINT
              AS occupied_dwellings
          FROM vivienda_units GROUP BY unit_key
        )
        SELECT f.unit_key, f.sector_key, f.province_key, f.unit_level,
          f.population, f.dwellings, f.households,
          COALESCE(o.occupied_dwellings,0)::BIGINT AS occupied_dwellings,
          f.unit_level = 'manzana' AND
            (f.population < 10 OR COALESCE(o.occupied_dwellings,0) < 3)
            AS full_suppression
        FROM counts_finest f LEFT JOIN occupied o USING (unit_key)
        """
    )
    national = sqlpath(FULL / "categories/nacion/data.parquet")
    connection.execute(
        f"""
        CREATE OR REPLACE TABLE publication_codebook AS
        SELECT source_table, variable, category,
          (DENSE_RANK() OVER (ORDER BY source_table, variable)-1)::UTINYINT
            AS variable_id,
          (ROW_NUMBER() OVER (PARTITION BY source_table, variable
                              ORDER BY category)-1)::USMALLINT AS category_id
        FROM read_parquet('{national}')
        """
    )
    number, max_category = connection.execute(
        "SELECT COUNT(DISTINCT variable_id), MAX(category_id) FROM publication_codebook"
    ).fetchone()
    if number > 256 or max_category > 65_535:
        raise ValueError("Category codebook exceeds uint8/uint16 range")
    target = PACKED / "categories/codebook.parquet"
    target.parent.mkdir(parents=True, exist_ok=True)
    connection.execute(
        f"""
        COPY (
          SELECT variable_id, category_id, source_table, variable, category,
            '{GEOM_VERSION}'::VARCHAR AS geom_version
          FROM publication_codebook ORDER BY variable_id, category_id
        ) TO '{sqlpath(target)}' (FORMAT PARQUET, COMPRESSION ZSTD)
        """
    )
    unit_types = {}
    category_count_types = {}
    for level in LEVELS:
        partition = "PARTITION BY province_key" if level not in {"provincia", "nacion"} else ""
        connection.execute(
            f"""
            CREATE OR REPLACE TABLE publication_ids_{level} AS
            SELECT unit_key, province_key,
              (ROW_NUMBER() OVER ({partition} ORDER BY unit_key)-1)::USMALLINT
                AS unit_index
            FROM counts_{level}
            """
        )
        maximum = connection.execute(
            f"SELECT MAX(unit_index) FROM publication_ids_{level}"
        ).fetchone()[0]
        if maximum > 65_535:
            raise ValueError(f"{level} unit index exceeds uint16")
        unit_types[level] = count_type(maximum)
        category_path = sqlpath(FULL / "categories" / level / "**/*.parquet")
        category_max = connection.execute(
            f"SELECT MAX(n) FROM read_parquet('{category_path}', "
            "hive_partitioning=false)"
        ).fetchone()[0]
        category_count_types[level] = count_type(category_max)
    connection.execute(
        "CREATE OR REPLACE TABLE publication_category_affected "
        "(unit_key VARCHAR PRIMARY KEY)"
    )
    return unit_types, category_count_types


def build_core_masks(connection: duckdb.DuckDBPyConnection) -> dict[str, int]:
    fields = ", ".join(DETAIL_FIELDS)
    connection.execute(
        f"""
        CREATE OR REPLACE TABLE publication_core_positive AS
        SELECT unit_key, sector_key, field, value,
          (full_suppression OR value < 3) AS is_primary
        FROM (
          SELECT f.unit_key, f.sector_key, p.full_suppression, {fields}
          FROM counts_finest f JOIN privacy_units p USING (unit_key)
          WHERE f.unit_level='manzana'
        ) UNPIVOT (value FOR field IN ({fields}))
        WHERE value > 0
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE publication_core_secondary AS
        WITH groups AS (
          SELECT sector_key, field,
            COUNT(*) FILTER (WHERE is_primary) AS primary_count
          FROM publication_core_positive GROUP BY sector_key, field
        ), candidates AS (
          SELECT p.unit_key, p.field,
            ROW_NUMBER() OVER (
              PARTITION BY p.sector_key, p.field
              ORDER BY p.value, p.unit_key
            ) AS rank_in_group
          FROM publication_core_positive p JOIN groups g
            USING (sector_key, field)
          WHERE g.primary_count=1 AND NOT p.is_primary
        )
        SELECT unit_key, field FROM candidates WHERE rank_in_group=1
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE publication_core_mask AS
        SELECT unit_key, field FROM publication_core_positive WHERE is_primary
        UNION ALL SELECT unit_key, field FROM publication_core_secondary
        """
    )
    cases = ",\n".join(
        f"BOOL_OR(field='{field}') AS mask_{field}" for field in DETAIL_FIELDS
    )
    connection.execute(
        f"""
        CREATE OR REPLACE TABLE publication_core_mask_wide AS
        SELECT unit_key, {cases} FROM publication_core_mask GROUP BY unit_key
        """
    )
    primary, secondary = connection.execute(
        "SELECT (SELECT COUNT(*) FROM publication_core_positive WHERE is_primary), "
        "(SELECT COUNT(*) FROM publication_core_secondary)"
    ).fetchone()
    return {"primary_cells": primary, "secondary_cells": secondary}


def pack_fine_categories(
    connection: duckdb.DuckDBPyConnection,
    unit_types: dict[str, str],
    category_count_types: dict[str, str],
) -> dict[str, int]:
    output = PACKED / "categories/finest"
    output.mkdir(parents=True, exist_ok=True)
    primary_total = 0
    secondary_total = 0
    for province in PROVINCES:
        paths = sorted((FULL / "categories/finest").glob(f"*/{province}.parquet"))
        if len(paths) != 5:
            raise ValueError(f"Expected five fine category sources in {province}")
        source = ",".join(f"'{sqlpath(path)}'" for path in paths)
        connection.execute(
            f"""
            INSERT INTO publication_category_affected
            SELECT DISTINCT a.unit_key
            FROM read_parquet([{source}], hive_partitioning=false) a
            JOIN privacy_units p USING (unit_key)
            WHERE p.unit_level='manzana' AND (p.full_suppression OR a.n<3)
            ON CONFLICT DO NOTHING
            """
        )
        ranked = f"""
          WITH marked AS (
            SELECT a.unit_key, a.sector_key, a.source_table, a.variable,
              a.category, a.n, i.unit_index,
              (p.unit_level='manzana' AND
                (p.full_suppression OR a.n<3)) AS is_primary
            FROM read_parquet([{source}], hive_partitioning=false) a
            JOIN privacy_units p USING (unit_key)
            JOIN publication_ids_finest i USING (unit_key)
            WHERE p.unit_level IN ('manzana','sector_disperso')
          ), ranked AS (
            SELECT *,
              SUM(is_primary::INT) OVER (
                PARTITION BY sector_key,source_table,variable,category
              ) AS primary_count,
              ROW_NUMBER() OVER (
                PARTITION BY sector_key,source_table,variable,category
                ORDER BY is_primary ASC,n,unit_key
              ) AS candidate_rank
            FROM marked
          )
        """
        target = output / f"{province}.parquet"
        connection.execute(
            f"""
            COPY (
              {ranked}
              SELECT r.unit_index::{unit_types['finest']} AS unit_index,
                b.variable_id::UTINYINT AS variable_id,
                b.category_id::USMALLINT AS category_id,
                r.n::{category_count_types['finest']} AS n,
                '{GEOM_VERSION}'::VARCHAR AS geom_version
              FROM ranked r JOIN publication_codebook b
                ON r.source_table=b.source_table AND r.variable=b.variable
                AND r.category IS NOT DISTINCT FROM b.category
              WHERE NOT r.is_primary
                AND NOT (r.primary_count=1 AND r.candidate_rank=1)
              ORDER BY unit_index,variable_id,category_id
            ) TO '{sqlpath(target)}'
            (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
            """
        )
        # The same ranked decision counts primary and complementary cells.
        primary, secondary = connection.execute(
            f"""
            {ranked}
            SELECT COUNT(*) FILTER (WHERE is_primary),
              COUNT(*) FILTER (WHERE NOT is_primary
                AND primary_count=1 AND candidate_rank=1)
            FROM ranked
            """
        ).fetchone()
        primary_total += primary
        secondary_total += secondary
        print(
            f"packed fine categories {province}: {target.stat().st_size} bytes",
            flush=True,
        )
    return {"primary_cells": primary_total, "secondary_cells": secondary_total}


def pack_upper_categories(
    connection: duckdb.DuckDBPyConnection,
    unit_types: dict[str, str],
    category_count_types: dict[str, str],
) -> None:
    for level in LEVELS[1:]:
        output = PACKED / "categories" / level
        output.mkdir(parents=True, exist_ok=True)
        for province in PROVINCES if level in {"sector", "parroquia", "canton"} else (None,):
            if province:
                source = FULL / "categories" / level / f"province_key={province}/data_0.parquet"
                target = output / f"{province}.parquet"
                condition = f"WHERE i.province_key='{province}'"
            else:
                source = FULL / "categories" / level / "data.parquet"
                target = output / "data.parquet"
                condition = ""
            kind = category_count_types[level]
            connection.execute(
                f"""
                COPY (
                  SELECT i.unit_index::{unit_types[level]} AS unit_index,
                    b.variable_id::UTINYINT AS variable_id,
                    b.category_id::USMALLINT AS category_id,
                    a.n::{kind} AS n,
                    '{GEOM_VERSION}'::VARCHAR AS geom_version
                  FROM read_parquet('{sqlpath(source)}', hive_partitioning=false) a
                  JOIN publication_ids_{level} i USING (unit_key)
                  JOIN publication_codebook b
                    ON a.source_table=b.source_table AND a.variable=b.variable
                    AND a.category IS NOT DISTINCT FROM b.category
                  {condition}
                  ORDER BY unit_index,variable_id,category_id
                ) TO '{sqlpath(target)}'
                (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
                """
            )
        print(f"packed {level} categories", flush=True)


def pack_core(
    connection: duckdb.DuckDBPyConnection,
    unit_types: dict[str, str],
) -> dict[str, dict[str, str]]:
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
        output = PACKED / level
        output.mkdir(parents=True, exist_ok=True)
        fine = level == "finest"
        for province in PROVINCES if level in {"finest", "sector"} else (None,):
            if province:
                target = output / f"{province}.parquet"
                condition = f"WHERE f.province_key='{province}'"
            else:
                target = output / "data.parquet"
                condition = ""
            values = []
            for field in NUMERIC_FIELDS:
                if fine and field in DETAIL_FIELDS:
                    expression = (
                        f"CASE WHEN p.full_suppression OR "
                        f"COALESCE(m.mask_{field},false) THEN NULL "
                        f"ELSE f.{field} END"
                    )
                else:
                    expression = f"f.{field}"
                values.append(f"({expression})::{kinds[field]} AS {field}")
            numbers = ",\n".join(values)
            privacy_join = (
                "LEFT JOIN privacy_units p USING (unit_key) "
                "LEFT JOIN publication_core_mask_wide m USING (unit_key) "
                "LEFT JOIN publication_category_affected a USING (unit_key)"
                if fine else ""
            )
            privacy_flag = (
                ", COALESCE(p.full_suppression,false) AS detalle_en_sector, "
                "(m.unit_key IS NOT NULL OR a.unit_key IS NOT NULL) "
                "AS celdas_suprimidas"
                if fine else ""
            )
            connection.execute(
                f"""
                COPY (
                  SELECT i.unit_index::{unit_types[level]} AS unit_index,
                    f.unit_key, f.unit_level,
                    f.province_key, f.canton_key, f.parish_key, f.sector_key,
                    f.asignado_a_sector, f.sector_disperso,
                    f.geografia_oculta, f.geom_version{privacy_flag},
                    {numbers}
                  FROM counts_{level} f
                  JOIN publication_ids_{level} i USING (unit_key)
                  {privacy_join}
                  {condition}
                  ORDER BY i.unit_index
                ) TO '{sqlpath(target)}'
                (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
                """
            )
        print(f"packed core {level}", flush=True)
    return types


def report_suppression(connection: duckdb.DuckDBPyConnection) -> list[dict[str, int | str]]:
    rows = connection.execute(
        """
        SELECT province_key,
          COUNT(*) FILTER (WHERE unit_level='manzana') AS manzanas,
          COUNT(*) FILTER (WHERE full_suppression) AS manzanas_sin_detalle,
          SUM(population) FILTER (WHERE full_suppression) AS poblacion_sin_detalle,
          SUM(dwellings) FILTER (WHERE full_suppression) AS viviendas_sin_detalle
        FROM privacy_units GROUP BY province_key ORDER BY province_key
        """
    ).fetchall()
    return [
        dict(zip(
            ("province_key", "manzanas", "manzanas_sin_detalle",
             "poblacion_sin_detalle", "viviendas_sin_detalle"),
            row, strict=True,
        ))
        for row in rows
    ]


def validate_packed(connection: duckdb.DuckDBPyConnection) -> None:
    # Publication can hide fine cells; all higher-level sums remain exact.
    for level in LEVELS[1:]:
        pattern = sqlpath(PACKED / level / "*.parquet")
        fields = ",".join(
            f"SUM({field})::BIGINT" for field in NUMERIC_FIELDS
        )
        packed = connection.execute(
            f"SELECT COUNT(*),{fields} FROM read_parquet('{pattern}')"
        ).fetchone()
        original = connection.execute(
            f"SELECT COUNT(*),{fields} FROM counts_{level}"
        ).fetchone()
        if packed != original:
            raise AssertionError(f"Packed core {level} differs from full counts")
        full_path = sqlpath(FULL / "categories" / level / "**/*.parquet")
        packed_path = sqlpath(PACKED / "categories" / level / "*.parquet")
        left = connection.execute(
            f"SELECT COUNT(*),SUM(n)::BIGINT FROM read_parquet('{full_path}', "
            "hive_partitioning=false)"
        ).fetchone()
        right = connection.execute(
            f"SELECT COUNT(*),SUM(n)::BIGINT FROM read_parquet('{packed_path}')"
        ).fetchone()
        if left != right:
            raise AssertionError(f"Packed categories {level} differ from full counts")
    fine = sqlpath(PACKED / "finest/*.parquet")
    hidden = connection.execute(
        f"""
        SELECT COUNT(*) FROM read_parquet('{fine}') a
        JOIN privacy_units p USING (unit_key)
        WHERE p.full_suppression AND (
          {" OR ".join(f'a.{field} IS NOT NULL' for field in DETAIL_FIELDS)}
        )
        """
    ).fetchone()[0]
    if hidden:
        raise AssertionError(f"{hidden} small manzanas leaked detailed counts")
    bad_flags = connection.execute(
        f"""
        SELECT COUNT(*) FROM read_parquet('{fine}') a
        JOIN privacy_units p USING (unit_key)
        WHERE a.detalle_en_sector IS DISTINCT FROM p.full_suppression
        """
    ).fetchone()[0]
    if bad_flags:
        raise AssertionError(f"{bad_flags} incorrect small-manzana flags")
    small_core_cells = connection.execute(
        f"""
        SELECT COUNT(*) FROM read_parquet('{fine}')
        WHERE unit_level='manzana' AND (
          {" OR ".join(f'{field} IN (1,2)' for field in DETAIL_FIELDS)}
        )
        """
    ).fetchone()[0]
    if small_core_cells:
        raise AssertionError(f"{small_core_cells} fine detail cells below 3")
    for province in PROVINCES:
        file = sqlpath(PACKED / f"categories/finest/{province}.parquet")
        leaked, small, rural_rows, rural_sum = connection.execute(
            f"""
            SELECT
              COUNT(*) FILTER (WHERE p.full_suppression),
              COUNT(*) FILTER (WHERE p.unit_level='manzana' AND a.n<3),
              COUNT(*) FILTER (WHERE p.unit_level='sector_disperso'),
              SUM(a.n) FILTER (WHERE p.unit_level='sector_disperso')
            FROM read_parquet('{file}') a
            JOIN publication_ids_finest i
              ON a.unit_index=i.unit_index AND i.province_key='{province}'
            JOIN privacy_units p USING (unit_key)
            """
        ).fetchone()
        if leaked or small:
            raise AssertionError(
                f"{province}: {leaked} small-manzana categories or {small} cells below 3"
            )
        sources = sorted((FULL / "categories/finest").glob(f"*/{province}.parquet"))
        source = ",".join(f"'{sqlpath(path)}'" for path in sources)
        expected = connection.execute(
            f"""
            SELECT COUNT(*), SUM(a.n)
            FROM read_parquet([{source}], hive_partitioning=false) a
            JOIN privacy_units p USING (unit_key)
            WHERE p.unit_level='sector_disperso'
            """
        ).fetchone()
        if (rural_rows, rural_sum) != expected:
            raise AssertionError(
                f"{province}: sector-disperso categories missing: "
                f"{(rural_rows, rural_sum)} != {expected}"
            )


def main() -> None:
    if not DB.is_file() or not (FULL / "qa.json").is_file():
        raise FileNotFoundError("Run 02_counts_by_unit.py and 07_qa.py first")
    safe_remove(PACKED.parent.parent, INTERIM)
    PACKED.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(DB))
    connection.execute("SET memory_limit='4GB'")
    connection.execute(f"SET temp_directory='{sqlpath(INTERIM / 'pack_temp')}'")
    unit_types, category_count_types = prepare(connection)
    core_mask = build_core_masks(connection)
    category_mask = pack_fine_categories(connection, unit_types, category_count_types)
    pack_upper_categories(connection, unit_types, category_count_types)
    numeric_types = pack_core(connection, unit_types)
    provinces = report_suppression(connection)
    validate_packed(connection)
    qa = json.loads((FULL / "qa.json").read_text(encoding="utf-8"))
    qa["suppression"] = {
        "population_threshold": 10,
        "occupied_dwellings_threshold": 3,
        "category_cell_threshold": 3,
        "core": core_mask,
        "categories": category_mask,
        "by_province": provinces,
    }
    (PACKED / "qa.json").write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    metadata = {
        "schema_version": 2,
        "geom_version": GEOM_VERSION,
        "category_codebook": "categories/codebook.parquet",
        "numeric_types": numeric_types,
        "unit_index_types": unit_types,
        "category_count_types": category_count_types,
        "suppression": "See qa.json and docs/metodologia.md",
    }
    (PACKED / "schema.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    files = [path for path in PACKED.rglob("*") if path.is_file()]
    total = sum(path.stat().st_size for path in files)
    largest = max(path.stat().st_size for path in files)
    print(f"packed counts: {len(files)} files, {total} bytes, max {largest}")
    if total > MAX_COUNTS_BYTES or largest > MAX_FILE_BYTES:
        raise ValueError("Packed Phase 1A output exceeds the Pages size budget")
    connection.close()
    safe_remove(FULL, ROOT / "web/public/data")
    destination = FULL.resolve()
    source = PACKED.resolve()
    if (
        not destination.is_relative_to(ROOT.resolve())
        or not source.is_relative_to(INTERIM.resolve())
    ):
        raise ValueError("Unsafe packed output move")
    shutil.move(str(source), str(destination))


if __name__ == "__main__":
    main()
