"""Aggregate five-year inter-canton flows and diaspora/death profiles from private views."""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data/interim/counts_v1a.duckdb"
DEFAULT_OUTPUT = ROOT / "data/interim/mobility_v1b2"


def quote(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def build(database: Path, output: Path) -> None:
    if not output.resolve().is_relative_to((ROOT / "data/interim").resolve()):
        raise ValueError("Output must remain under ignored data/interim")
    output.mkdir(parents=True, exist_ok=True)
    db = duckdb.connect(str(database), read_only=True)
    db.execute(f"""
        COPY (
          SELECT p.P09C AS origin_canton, p.canton_key AS destination_canton,
            COUNT(*)::UINTEGER AS people, 'marco-2021'::VARCHAR AS geom_version
          FROM poblacion_units p
          JOIN counts_canton origin ON p.P09C=origin.unit_key
          WHERE p.P09='2' AND p.P09C<>p.canton_key
          GROUP BY 1,2 ORDER BY 1,2
        ) TO '{quote(output / 'canton_origin_destination.parquet')}'
        (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
    """)
    flows = quote(output / "canton_origin_destination.parquet")
    db.execute(f"""
        COPY (
          WITH arrivals AS (
            SELECT destination_canton AS unit_key, SUM(people)::BIGINT AS arrivals
            FROM read_parquet('{flows}') GROUP BY 1
          ), departures AS (
            SELECT origin_canton AS unit_key, SUM(people)::BIGINT AS departures
            FROM read_parquet('{flows}') GROUP BY 1
          )
          SELECT c.unit_key, COALESCE(a.arrivals,0)::UINTEGER AS internal_arrivals,
            COALESCE(d.departures,0)::UINTEGER AS internal_departures,
            (COALESCE(a.arrivals,0)-COALESCE(d.departures,0))::INTEGER AS internal_net,
            'marco-2021'::VARCHAR AS geom_version
          FROM counts_canton c LEFT JOIN arrivals a USING(unit_key)
          LEFT JOIN departures d USING(unit_key) ORDER BY c.unit_key
        ) TO '{quote(output / 'canton_net.parquet')}'
        (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
    """)
    # Raw event fields are collapsed to geography × public demographic dimensions.
    db.execute(f"""
        COPY (
          SELECT parish_key AS unit_key, E04 AS destination_country,
            TRY_CAST(E01 AS INTEGER)::USMALLINT AS departure_year,
            E02 AS sex, TRY_CAST(E03 AS INTEGER)::USMALLINT AS age_at_departure,
            COUNT(*)::UINTEGER AS emigrants,
            'marco-2021'::VARCHAR AS geom_version
          FROM emigracion_units
          GROUP BY 1,2,3,4,5 ORDER BY 1,2,3,4,5
        ) TO '{quote(output / 'emigrant_profile_parroquia.parquet')}'
        (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
    """)
    db.execute(f"""
        COPY (
          SELECT canton_key AS unit_key, M04 AS sex,
            TRY_CAST(M03 AS INTEGER)::USMALLINT AS age_at_death,
            TRY_CAST(M0202 AS INTEGER)::USMALLINT AS death_year,
            COUNT(*)::UINTEGER AS deaths,
            'marco-2021'::VARCHAR AS geom_version
          FROM mortalidad_units
          GROUP BY 1,2,3,4 ORDER BY 1,2,3,4
        ) TO '{quote(output / 'death_profile_canton.parquet')}'
        (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
    """)
    for file in output.glob("*.parquet"):
        rows = db.execute(f"SELECT COUNT(*) FROM read_parquet('{quote(file)}')").fetchone()[0]
        print(f"{file.name}: {rows:,} aggregated rows, {file.stat().st_size:,} bytes")
    balance = db.execute(
        f"SELECT SUM(internal_net) FROM read_parquet('{quote(output / 'canton_net.parquet')}')"
    ).fetchone()[0]
    if balance != 0:
        raise AssertionError(f"National internal net migration must sum to zero: {balance}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.db, args.output)


if __name__ == "__main__":
    main()
