"""Build aggregate census geography counts and compare with the official sector GPKG.

Only geography identifiers and aggregate counts are stored. No person records
leave the local gitignored data directory.
"""

from __future__ import annotations

import csv
from pathlib import Path

import duckdb
import pyogrio

ROOT = Path(__file__).resolve().parents[1]
POPULATION = (
    ROOT
    / "data/raw/1.3 BDD_CPV_2022_MANLOC_CSV"
    / "CPV_2022_Poblacion_Manloc.csv"
)
GPKG = ROOT / "data/raw/sectores_anonimizados.gpkg"
GPKG_BACKUP = ROOT / "data/raw/GEODATABASE_NACIONAL_2021/GEODATABASE_NACIONAL_2021.gpkg"
DB = ROOT / "data/interim/fase0.duckdb"
SECTOR_RESULT = ROOT / "data/interim/sector_match.csv"
MANZANA_RESULT = ROOT / "data/interim/manzana_match.csv"


def main() -> None:
    DB.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(DB))
    escaped_path = POPULATION.as_posix().replace("'", "''")
    source = f"read_csv('{escaped_path}', delim=';', header=true, all_varchar=true)"
    connection.execute(
        f"""
        CREATE OR REPLACE TABLE census_units AS
        SELECT
            I01 AS province,
            I01 || I02 || I03 || I04 || I05 AS sector_key,
            I06 AS manzana,
            I07 AS localidad,
            COUNT(*)::BIGINT AS population
        FROM {source}
        GROUP BY ALL
        """
    )
    connection.execute(
        """
        CREATE OR REPLACE TABLE census_sectors AS
        SELECT province, sector_key, SUM(population)::BIGINT AS population
        FROM census_units
        GROUP BY ALL
        """
    )
    geo = pyogrio.read_dataframe(
        GPKG, columns=["sec_anm", "provincia"], read_geometry=False
    )
    geo = geo.rename(columns={"sec_anm": "sector_key", "provincia": "province"})
    connection.register("geometry_source", geo)
    connection.execute(
        """
        CREATE OR REPLACE TABLE geometry_sectors AS
        SELECT DISTINCT province::VARCHAR AS province, sector_key::VARCHAR AS sector_key
        FROM geometry_source
        WHERE sector_key IS NOT NULL
        """
    )
    sector_result = connection.execute(
        """
        SELECT
            c.province,
            COUNT(*) FILTER (WHERE is_matchable)::INTEGER AS matchable_sectors,
            COUNT(g.sector_key) FILTER (WHERE is_matchable)::INTEGER AS matched_sectors,
            ROUND(100.0 * COUNT(g.sector_key) FILTER (WHERE is_matchable)
                / NULLIF(COUNT(*) FILTER (WHERE is_matchable), 0), 3)
                AS census_match_percent,
            COUNT(*) FILTER (WHERE NOT is_matchable)::INTEGER AS masked_sector_keys,
            SUM(c.population)::BIGINT AS population,
            SUM(CASE WHEN is_matchable AND g.sector_key IS NOT NULL
                THEN c.population ELSE 0 END)::BIGINT
                AS population_in_matched_sectors
        FROM (
            SELECT *,
                substr(sector_key, 7, 3) <> '888'
                AND substr(sector_key, 10, 3) <> '888' AS is_matchable
            FROM census_sectors
        ) c
        LEFT JOIN geometry_sectors g
            ON c.province = g.province AND c.sector_key = g.sector_key
        GROUP BY c.province
        ORDER BY c.province
        """
    ).fetchall()
    with SECTOR_RESULT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "province",
                "matchable_sectors",
                "matched_sectors",
                "census_match_percent",
                "masked_sector_keys",
                "population",
                "population_in_matched_sectors",
            ]
        )
        writer.writerows(sector_result)
    print("SECTOR: province,matchable,matched,match_percent,masked,population")
    for row in sector_result:
        print(",".join(map(str, row[:6])))

    manzanas = pyogrio.read_dataframe(
        GPKG_BACKUP, layer="man_a", columns=["man"], read_geometry=False
    )
    manzanas = manzanas.rename(columns={"man": "manzana_key"})
    manzanas["province"] = manzanas["manzana_key"].str[:2]
    connection.register("manzana_source", manzanas)
    connection.execute(
        """
        CREATE OR REPLACE TABLE geometry_manzanas AS
        SELECT DISTINCT province::VARCHAR AS province, manzana_key::VARCHAR AS manzana_key
        FROM manzana_source
        WHERE manzana_key IS NOT NULL
        """
    )
    manzana_result = connection.execute(
        """
        SELECT
            c.province,
            COUNT(*) FILTER (WHERE is_matchable)::INTEGER AS matchable_manzanas,
            COUNT(g.manzana_key) FILTER (WHERE is_matchable)::INTEGER AS matched_manzanas,
            ROUND(100.0 * COUNT(g.manzana_key) FILTER (WHERE is_matchable)
                / NULLIF(COUNT(*) FILTER (WHERE is_matchable), 0), 3)
                AS census_match_percent,
            COUNT(*) FILTER (WHERE NOT is_matchable)::INTEGER AS masked_manzana_keys,
            SUM(c.population)::BIGINT AS population,
            SUM(CASE WHEN is_matchable AND g.manzana_key IS NOT NULL
                THEN c.population ELSE 0 END)::BIGINT
                AS population_in_matched_manzanas
        FROM (
            SELECT province, sector_key || manzana AS manzana_key,
                substr(sector_key, 7, 3) <> '888'
                AND substr(sector_key, 10, 3) <> '888'
                AND manzana <> '888' AS is_matchable,
                SUM(population)::BIGINT AS population
            FROM census_units
            WHERE manzana IS NOT NULL
            GROUP BY ALL
        ) c
        LEFT JOIN geometry_manzanas g
            ON c.province = g.province AND c.manzana_key = g.manzana_key
        GROUP BY c.province
        ORDER BY c.province
        """
    ).fetchall()
    with MANZANA_RESULT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "province",
                "matchable_manzanas",
                "matched_manzanas",
                "census_match_percent",
                "masked_manzana_keys",
                "population",
                "population_in_matched_manzanas",
            ]
        )
        writer.writerows(manzana_result)
    print("MANZANA: province,matchable,matched,match_percent,masked,population")
    for row in manzana_result:
        print(",".join(map(str, row[:6])))


if __name__ == "__main__":
    main()
