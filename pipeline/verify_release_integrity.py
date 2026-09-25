"""Verify exact additivity using only the public, checksum-verified Release."""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
from category_counts import HIGH_CARDINALITY
from counts_schema import NUMERIC_FIELDS

ROOT = Path(__file__).resolve().parents[1]
PROVINCES = tuple(f"{index:02d}" for index in range(1, 25))
CORE_LEVELS = ("finest", "sector", "parroquia", "canton", "provincia", "nacion")


def sqlpath(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def assert_category_equal(
    connection: duckdb.DuckDBPyConnection,
    lower: str,
    upper: str,
    label: str,
) -> None:
    missing = connection.execute(
        f"""
        WITH a AS ({lower}), b AS ({upper})
        SELECT COUNT(*) FROM a FULL OUTER JOIN b
          USING (unit_key,variable_id,category_id)
        WHERE a.n IS DISTINCT FROM b.n
        """
    ).fetchone()[0]
    if missing:
        raise AssertionError(f"Category additivity failed at {label}: {missing} cells")


def core_views(connection: duckdb.DuckDBPyConnection, root: Path) -> None:
    for level in CORE_LEVELS:
        pattern = sqlpath(root / level / ("*.parquet" if level in {"finest", "sector"}
                                          else "data.parquet"))
        connection.execute(
            f"CREATE OR REPLACE TEMP VIEW core_{level} AS "
            f"SELECT * FROM read_parquet('{pattern}')"
        )


def check_core(connection: duckdb.DuckDBPyConnection) -> None:
    hierarchy = (
        ("finest", "sector", "sector_key"),
        ("sector", "parroquia", "parish_key"),
        ("parroquia", "canton", "canton_key"),
        ("canton", "provincia", "province_key"),
        ("provincia", "nacion", "'EC'"),
    )
    sums = ",".join(f"SUM({field})::BIGINT AS {field}" for field in NUMERIC_FIELDS)
    mismatch = " OR ".join(
        f"a.{field} IS DISTINCT FROM b.{field}" for field in NUMERIC_FIELDS
    )
    for lower, upper, key in hierarchy:
        missing = connection.execute(
            f"""
            WITH a AS (
              SELECT {key} AS unit_key,{sums} FROM core_{lower}
              GROUP BY {key}
            ), b AS (SELECT * FROM core_{upper})
            SELECT COUNT(*) FROM a FULL OUTER JOIN b USING (unit_key)
            WHERE a.unit_key IS NULL OR b.unit_key IS NULL OR {mismatch}
            """
        ).fetchone()[0]
        if missing:
            raise AssertionError(f"Core additivity {lower}->{upper}: {missing} units")
        print(f"Core {lower}->{upper}: zero difference", flush=True)
    population, dwellings = connection.execute(
        "SELECT population,dwellings FROM core_nacion"
    ).fetchone()
    if (population, dwellings) != (16_938_986, 6_611_555):
        raise AssertionError("Public national totals differ from official CPV 2022")


def check_province_categories(
    connection: duckdb.DuckDBPyConnection, root: Path, province: str
) -> None:
    fine = sqlpath(root / "finest" / f"{province}.parquet")
    fine_cat = sqlpath(root / "categories/finest" / f"{province}.parquet")
    sector = sqlpath(root / "sector" / f"{province}.parquet")
    only = sqlpath(root / "categories/sector_only" / f"{province}.parquet")
    parish = sqlpath(root / "parroquia/data.parquet")
    parish_cat = sqlpath(root / "categories/parroquia" / f"{province}.parquet")
    canton = sqlpath(root / "canton/data.parquet")
    canton_cat = sqlpath(root / "categories/canton" / f"{province}.parquet")
    high = ",".join(f"'{value}'" for value in sorted(HIGH_CARDINALITY))
    sector_to_parish = f"""
      WITH sector_categories AS (
        SELECT u.sector_key AS unit_key,c.variable_id,c.category_id,
          SUM(c.n)::BIGINT AS n
        FROM read_parquet('{fine_cat}') c
        JOIN read_parquet('{fine}') u USING (unit_index)
        GROUP BY u.sector_key,c.variable_id,c.category_id
        UNION ALL
        SELECT u.unit_key,c.variable_id,c.category_id,c.n::BIGINT
        FROM read_parquet('{only}') c
        JOIN read_parquet('{sector}') u USING (unit_index)
      )
      SELECT LEFT(unit_key,6) AS unit_key,variable_id,category_id,
        SUM(n)::BIGINT AS n
      FROM sector_categories GROUP BY LEFT(unit_key,6),variable_id,category_id
    """
    parish_values = f"""
      SELECT u.unit_key,c.variable_id,c.category_id,c.n::BIGINT AS n
      FROM read_parquet('{parish_cat}') c
      JOIN read_parquet('{parish}') u USING (unit_index)
      WHERE u.province_key='{province}'
    """
    assert_category_equal(
        connection, sector_to_parish, parish_values,
        f"finest+sector_only->parroquia {province}",
    )
    parish_to_canton = f"""
      SELECT u.canton_key AS unit_key,c.variable_id,c.category_id,
        SUM(c.n)::BIGINT AS n
      FROM read_parquet('{parish_cat}') c
      JOIN read_parquet('{parish}') u USING (unit_index)
      WHERE u.province_key='{province}'
      GROUP BY u.canton_key,c.variable_id,c.category_id
    """
    canton_values = f"""
      SELECT u.unit_key,c.variable_id,c.category_id,c.n::BIGINT AS n
      FROM read_parquet('{canton_cat}') c
      JOIN read_parquet('{canton}') u USING (unit_index)
      JOIN read_parquet('{sqlpath(root / 'categories/codebook.parquet')}') b
        USING (variable_id,category_id)
      WHERE u.province_key='{province}' AND b.variable NOT IN ({high})
    """
    assert_category_equal(
        connection, parish_to_canton, canton_values,
        f"parroquia->canton {province}",
    )
    print(f"Categories through canton {province}: zero difference", flush=True)


def check_upper_categories(connection: duckdb.DuckDBPyConnection, root: Path) -> None:
    canton = sqlpath(root / "canton/data.parquet")
    province = sqlpath(root / "provincia/data.parquet")
    nation = sqlpath(root / "nacion/data.parquet")
    canton_files = sqlpath(root / "categories/canton/*.parquet")
    province_file = sqlpath(root / "categories/provincia/data.parquet")
    nation_file = sqlpath(root / "categories/nacion/data.parquet")
    canton_values = f"""
      SELECT u.province_key AS unit_key,c.variable_id,c.category_id,
        SUM(c.n)::BIGINT AS n
      FROM (
        SELECT *,regexp_extract(filename,'([0-9]{{2}})\\.parquet$',1)
          AS province_key
        FROM read_parquet('{canton_files}',filename=true)
      ) c JOIN read_parquet('{canton}') u USING (province_key,unit_index)
      GROUP BY u.province_key,c.variable_id,c.category_id
    """
    province_values = f"""
      SELECT u.unit_key,c.variable_id,c.category_id,c.n::BIGINT AS n
      FROM read_parquet('{province_file}') c
      JOIN read_parquet('{province}') u USING (unit_index)
    """
    assert_category_equal(connection, canton_values, province_values, "canton->provincia")
    province_to_nation = f"""
      SELECT 'EC' AS unit_key,c.variable_id,c.category_id,
        SUM(c.n)::BIGINT AS n
      FROM read_parquet('{province_file}') c
      GROUP BY c.variable_id,c.category_id
    """
    nation_values = f"""
      SELECT u.unit_key,c.variable_id,c.category_id,c.n::BIGINT AS n
      FROM read_parquet('{nation_file}') c
      JOIN read_parquet('{nation}') u USING (unit_index)
    """
    assert_category_equal(connection, province_to_nation, nation_values, "provincia->nacion")
    print("Upper categories: zero difference", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--core-only", action="store_true")
    args = parser.parse_args()
    root = args.root / "counts/v1b1"
    if not (root / "schema.json").is_file():
        raise FileNotFoundError("Exact public Release was not restored")
    connection = duckdb.connect()
    connection.execute("SET memory_limit='4GB'")
    temp = ROOT / "data/interim/release_integrity_temp"
    temp.mkdir(parents=True, exist_ok=True)
    connection.execute(f"SET temp_directory='{sqlpath(temp)}'")
    core_views(connection, root)
    check_core(connection)
    if not args.core_only:
        for province in PROVINCES:
            check_province_categories(connection, root, province)
        check_upper_categories(connection, root)
    connection.close()
    print("Public Release has exact additive counts", flush=True)


if __name__ == "__main__":
    main()
