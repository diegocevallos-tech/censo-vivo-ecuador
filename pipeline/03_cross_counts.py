"""Build additive cross counts from private CPV records, publish only official-unit sums.

The input database has views over ignored person-level Parquet. The output has one
row per official census unit and only numeric sums, never an ID_PER or ID_HOG.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data/interim/counts_v1a.duckdb"
OUTPUT = ROOT / "data/interim/cross_counts_v1b2"
LEVELS = ("finest", "sector", "parroquia", "canton", "provincia", "nacion")
NUMERATORS = {
    "female_heads": "P01='1' AND P02='2'",
    "all_heads": "P01='1'",
    "solitary_65": "P01='1' AND age BETWEEN 65 AND 120 AND single_home",
    "all_65": "age BETWEEN 65 AND 120",
    "school_years_25": "age>=25 AND school BETWEEN 0 AND 25",
    "school_n_25": "age>=25 AND school BETWEEN 0 AND 25",
    "school_low_25": "age>=25 AND school BETWEEN 0 AND 9",
    "school_high_25": "age>=25 AND school BETWEEN 13 AND 25",
    "school_years_25_34": "age BETWEEN 25 AND 34 AND school BETWEEN 0 AND 25",
    "school_n_25_34": "age BETWEEN 25 AND 34 AND school BETWEEN 0 AND 25",
    "school_years_55_64": "age BETWEEN 55 AND 64 AND school BETWEEN 0 AND 25",
    "school_n_55_64": "age BETWEEN 55 AND 64 AND school BETWEEN 0 AND 25",
    "school_lag": "age BETWEEN 8 AND 17 AND school BETWEEN 0 AND 25 AND school<=age-8",
    "school_lag_n": "age BETWEEN 8 AND 17 AND school BETWEEN 0 AND 25",
    "digital_male_yes": "P02='1' AND age>=5 AND P2102='1'",
    "digital_male_n": "P02='1' AND age>=5 AND P2102 IN ('1','2')",
    "digital_female_yes": "P02='2' AND age>=5 AND P2102='1'",
    "digital_female_n": "P02='2' AND age>=5 AND P2102 IN ('1','2')",
    "digital_youth_yes": "age BETWEEN 5 AND 29 AND P2102='1'",
    "digital_youth_n": "age BETWEEN 5 AND 29 AND P2102 IN ('1','2')",
    "digital_senior_yes": "age>=65 AND P2102='1'",
    "digital_senior_n": "age>=65 AND P2102 IN ('1','2')",
    "digital_male_score": "P02='1' AND age>=5 AND digital_valid",
    "digital_male_max": "P02='1' AND age>=5 AND digital_valid",
    "digital_female_score": "P02='2' AND age>=5 AND digital_valid",
    "digital_female_max": "P02='2' AND age>=5 AND digital_valid",
    "digital_youth_score": "age BETWEEN 5 AND 29 AND digital_valid",
    "digital_youth_max": "age BETWEEN 5 AND 29 AND digital_valid",
    "digital_senior_score": "age>=65 AND digital_valid",
    "digital_senior_max": "age>=65 AND digital_valid",
    "labour_male_employed": "P02='1' AND CONDACT1='2'",
    "labour_male_force": "P02='1' AND CONDACT1 IN ('2','3')",
    "labour_female_employed": "P02='2' AND CONDACT1='2'",
    "labour_female_force": "P02='2' AND CONDACT1 IN ('2','3')",
    "adolescent_mothers": "P02='2' AND age BETWEEN 15 AND 19 AND children BETWEEN 1 AND 20",
    "adolescent_women": "P02='2' AND age BETWEEN 15 AND 19 AND children BETWEEN 0 AND 20",
    "indigenous_language": "P1001='1'",
    "language_eligible": "age>=5",
    "illiterate_15": "age>=15 AND ANALF='1'",
    "literacy_response_15": "age>=15 AND ANALF IN ('1','2')",
    "internet_person_5": "age>=5 AND P2102='1'",
    "internet_response_5": "age>=5 AND P2102 IN ('1','2')",
    "children_born_15_49": "P02='2' AND age BETWEEN 15 AND 49 AND children BETWEEN 0 AND 20",
    "women_children_response_15_49": (
        "P02='2' AND age BETWEEN 15 AND 49 AND children BETWEEN 0 AND 20"
    ),
    "birth_other_canton": "P08='2' AND LENGTH(P08C)=4 AND P08C<>canton_key",
    "residence_other_canton_5": "P09='2' AND LENGTH(P09C)=4 AND P09C<>canton_key",
}
SUM_FIELDS = {
    "school_years_25", "school_years_25_34", "school_years_55_64", "children_born_15_49"
}


def sqlpath(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def build(db_path: Path, output: Path) -> None:
    if not output.resolve().is_relative_to((ROOT / "data/interim").resolve()):
        raise ValueError("Output must remain under ignored data/interim")
    output.mkdir(parents=True, exist_ok=True)
    db = duckdb.connect(str(db_path), read_only=True)
    fields = list(NUMERATORS)
    def amount(name: str) -> str:
        if name in SUM_FIELDS:
            return "children" if name == "children_born_15_49" else "school"
        if name.endswith("_score"):
            return "digital_score"
        if name.endswith("_max"):
            return "3"
        return "1"

    metrics = ",\n".join(
        f"SUM(CASE WHEN {predicate} THEN "
        f"{amount(name)} "
        f"ELSE 0 END)::UINTEGER AS {name}"
        for name, predicate in NUMERATORS.items()
    )
    for province in (f"{number:02d}" for number in range(1, 25)):
        dest = output / "finest" / f"{province}.parquet"
        dest.parent.mkdir(parents=True, exist_ok=True)
        db.execute(f"""
        COPY (
          WITH person AS (
            SELECT p.unit_key, p.province_key, p.canton_key, p.parish_key,
              p.sector_key, p.P01, p.P02, p.P08, p.P08C, p.P09, p.P09C,
              p.P1001, p.P2102, p.P2103, p.ANALF_DIG, p.CONDACT1, p.ANALF,
              (p.ANALF_DIG IN ('1','2') AND p.P2102 IN ('1','2')
                AND p.P2103 IN ('1','2')) AS digital_valid,
              ((p.ANALF_DIG='2')::INTEGER + (p.P2102='1')::INTEGER
                + (p.P2103='1')::INTEGER) AS digital_score,
              TRY_CAST(p.P03 AS INTEGER) AS age,
              TRY_CAST(p.ESCOLA AS INTEGER) AS school,
              TRY_CAST(p.P3203 AS INTEGER) AS children,
              h.ID_HOG IS NOT NULL AS single_home
            FROM poblacion_units p
            LEFT JOIN (
              SELECT DISTINCT ID_HOG FROM hogar_units
              WHERE province_key='{province}' AND TIPO_HOGAR='1'
            ) h USING (ID_HOG)
            WHERE p.province_key='{province}'
          ), rollup AS (
            SELECT unit_key, {metrics}
            FROM person GROUP BY unit_key
          )
          SELECT c.unit_key,c.province_key,c.canton_key,c.parish_key,c.sector_key,
            'marco-2021'::VARCHAR AS geom_version,
            {','.join(f'COALESCE(r.{field},0)::UINTEGER AS {field}' for field in fields)}
          FROM counts_finest c LEFT JOIN rollup r USING(unit_key)
          WHERE c.province_key='{province}' ORDER BY c.unit_key
        ) TO '{sqlpath(dest)}' (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
        """)
        print(f"Cross counts {province}: {dest.stat().st_size:,} bytes", flush=True)
    fine = sqlpath(output / "finest" / "*.parquet")
    for level in LEVELS[1:]:
        destination = output / level / "data.parquet"
        destination.parent.mkdir(parents=True, exist_ok=True)
        if level == "sector":
            key = "sector_key"
        elif level == "parroquia":
            key = "parish_key"
        elif level == "canton":
            key = "canton_key"
        elif level == "provincia":
            key = "province_key"
        else:
            key = "'EC'"
        db.execute(f"""
        COPY (
          SELECT {key} AS unit_key, 'marco-2021'::VARCHAR AS geom_version,
            {','.join(f'SUM({field})::UINTEGER AS {field}' for field in fields)}
          FROM read_parquet('{fine}') GROUP BY {key} ORDER BY unit_key
        ) TO '{sqlpath(destination)}' (FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)
        """)
    print("Cross counts complete; no person or household identifiers exported", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=DATABASE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    build(args.db, args.output)


if __name__ == "__main__":
    main()
