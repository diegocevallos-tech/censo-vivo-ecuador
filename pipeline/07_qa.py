"""Verify Phase 1A additivity and independent official canton/province totals."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

import duckdb
from category_counts import HIGH_CARDINALITY
from counts_schema import AGE_SEX_FIELDS, GEOM_VERSION, NUMERIC_FIELDS

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/interim/counts_v1a.duckdb"
CANTON_ZIP = ROOT / "data/raw/BDD_CPV2022_CANT_CSV.zip"
PUBLIC = ROOT / "web/public/data/counts/v1a"
EXPECTED_POPULATION = 16_938_986
EXPECTED_DWELLINGS = 6_611_555
FILTERED_MANIFEST = ROOT / "data/interim/filtered_manifest.json"


def category_view(connection: duckdb.DuckDBPyConnection, level: str) -> None:
    pattern = (PUBLIC / "categories" / level / "**/*.parquet").as_posix()
    connection.execute(
        f"CREATE OR REPLACE TEMP VIEW cat_{level} AS "
        f"SELECT * FROM read_parquet('{pattern}', union_by_name=true, "
        "hive_partitioning=false)"
    )


def assert_category_additive(
    connection: duckdb.DuckDBPyConnection,
    lower: str,
    upper: str,
    key: str,
) -> dict[str, int | str]:
    upper_filter = ""
    if lower == "finest":
        upper_filter = "WHERE NOT (source_table = 'poblacion_sector' AND variable = 'P11R')"
    elif lower == "parroquia":
        variables = ", ".join(f"'{field}'" for field in sorted(HIGH_CARDINALITY))
        upper_filter = f"WHERE variable NOT IN ({variables})"
    missing = connection.execute(
        f"""
        WITH c AS (
          SELECT {key} AS unit_key, source_table, variable, category,
                 SUM(n)::BIGINT AS n
          FROM cat_{lower}
          GROUP BY ALL
        ), p AS (
          SELECT unit_key, source_table, variable, category, n
          FROM cat_{upper} {upper_filter}
        )
        SELECT COUNT(*) FROM c FULL OUTER JOIN p
          ON c.unit_key = p.unit_key
          AND c.source_table = p.source_table
          AND c.variable = p.variable
          AND c.category IS NOT DISTINCT FROM p.category
        WHERE c.n IS DISTINCT FROM p.n
        """
    ).fetchone()[0]
    if missing:
        raise AssertionError(f"Category {lower} -> {upper}: {missing} mismatched rows")
    return {"lower": lower, "upper": upper, "mismatched_rows": missing}


def assert_category_source_totals(
    connection: duckdb.DuckDBPyConnection,
) -> dict[str, int]:
    source = json.loads(FILTERED_MANIFEST.read_text(encoding="utf-8"))["tables"]
    counts = {
        (table, variable): n
        for table, variable, n in connection.execute(
            "SELECT source_table, variable, SUM(n)::BIGINT "
            "FROM cat_nacion WHERE variable IN ('AUR', 'P02', 'P11R', 'V01') "
            "GROUP BY source_table, variable"
        ).fetchall()
    }
    for table, info in source.items():
        if counts.get((table, "AUR")) != info["rows"]:
            raise AssertionError(f"Incomplete {table} AUR category counts")
    population = source["poblacion"]["rows"]
    dwellings = source["vivienda"]["rows"]
    for key, expected in {
        ("poblacion", "P02"): population,
        ("poblacion_sector", "P11R"): population,
        ("vivienda", "V01"): dwellings,
    }.items():
        if counts.get(key) != expected:
            raise AssertionError(f"Incomplete {key} category counts")
    return {table: info["rows"] for table, info in source.items()}


def official_canton_counts(keyword: str) -> Counter[str]:
    if not CANTON_ZIP.is_file():
        raise FileNotFoundError(CANTON_ZIP)
    with ZipFile(CANTON_ZIP) as archive:
        members = [name for name in archive.namelist() if keyword in name and name.endswith(".csv")]
        if len(members) != 1:
            raise ValueError(f"Expected one official {keyword} CSV: {members}")
        counts: Counter[str] = Counter()
        with archive.open(members[0]) as source:
            header = source.readline().split(b";")
            if header[:2] != [b"I01", b"I02"]:
                raise ValueError(f"Unexpected geography columns in {members[0]}")
            for row in source:
                fields = row.split(b";", 2)
                if len(fields) < 3 or len(fields[0]) != 2 or len(fields[1]) != 2:
                    raise ValueError(f"Malformed canton key in {members[0]}")
                counts[(fields[0] + fields[1]).decode("ascii")] += 1
    if len(counts) != 221:
        raise ValueError(f"Expected 221 cantons, found {len(counts)}")
    return counts


def assert_additive(
    connection: duckdb.DuckDBPyConnection, lower: str, upper: str, key: str
) -> dict[str, int | str]:
    summed = ", ".join(f"SUM({field})::BIGINT AS {field}" for field in NUMERIC_FIELDS)
    difference = " OR ".join(
        f"p.{field} IS DISTINCT FROM c.{field}" for field in NUMERIC_FIELDS
    )
    missing = connection.execute(
        f"""
        WITH c AS (SELECT {key} AS unit_key, {summed}
                   FROM counts_{lower} GROUP BY {key})
        SELECT COUNT(*) FROM counts_{upper} p FULL OUTER JOIN c USING (unit_key)
        WHERE p.unit_key IS NULL OR c.unit_key IS NULL OR {difference}
        """
    ).fetchone()[0]
    if missing:
        raise AssertionError(f"{lower} -> {upper}: {missing} mismatched geographic units")
    return {"lower": lower, "upper": upper, "mismatched_units": missing}


def assert_official(
    connection: duckdb.DuckDBPyConnection, table: str, key: str,
    people: Counter[str], dwellings: Counter[str]
) -> dict[str, int | str]:
    rows = connection.execute(
        f"SELECT {key}, population, dwellings FROM counts_{table}"
    ).fetchall()
    seen = set()
    mismatches = []
    for code, population, homes in rows:
        seen.add(code)
        if population != people[code] or homes != dwellings[code]:
            mismatches.append((code, population, people[code], homes, dwellings[code]))
    if seen != set(people) or seen != set(dwellings) or mismatches:
        raise AssertionError(
            f"Official {table} mismatch: keys={len(seen)}, differences={mismatches[:5]}"
        )
    return {"level": table, "units": len(rows), "mismatched_units": 0}


def main() -> None:
    if not DB.is_file():
        raise FileNotFoundError(f"Run 02_counts_by_unit.py first: {DB}")
    connection = duckdb.connect(str(DB), read_only=True)
    hierarchy = [
        ("finest", "sector", "sector_key"),
        ("sector", "parroquia", "parish_key"),
        ("parroquia", "canton", "canton_key"),
        ("canton", "provincia", "province_key"),
        ("provincia", "nacion", "'EC'"),
    ]
    additivity = [assert_additive(connection, *item) for item in hierarchy]
    for level in ("finest", "sector", "parroquia", "canton", "provincia", "nacion"):
        category_view(connection, level)
    category_hierarchy = [
        ("finest", "sector", "sector_key"),
        ("sector", "parroquia", "parish_key"),
        ("parroquia", "canton", "canton_key"),
        ("canton", "provincia", "SUBSTR(unit_key,1,2)"),
        ("provincia", "nacion", "'EC'"),
    ]
    category_additivity = [
        assert_category_additive(connection, *item) for item in category_hierarchy
    ]
    category_source_totals = assert_category_source_totals(connection)
    official_people = official_canton_counts("Pobl")
    official_homes = official_canton_counts("Vivienda")
    if sum(official_people.values()) != EXPECTED_POPULATION:
        raise AssertionError("Official canton population does not sum to national total")
    if sum(official_homes.values()) != EXPECTED_DWELLINGS:
        raise AssertionError("Official canton dwellings do not sum to national total")
    province_people: Counter[str] = Counter()
    province_homes: Counter[str] = Counter()
    for code, count in official_people.items():
        province_people[code[:2]] += count
    for code, count in official_homes.items():
        province_homes[code[:2]] += count
    official = [
        assert_official(connection, "canton", "unit_key", official_people, official_homes),
        assert_official(connection, "provincia", "unit_key", province_people, province_homes),
    ]
    national = connection.execute(
        "SELECT population, dwellings, assigned_manzanas, assigned_population, "
        "assigned_dwellings FROM counts_nacion"
    ).fetchone()
    if national != (EXPECTED_POPULATION, EXPECTED_DWELLINGS, 1852, 36040, 18701):
        raise AssertionError(f"National or sector assignment totals changed: {national}")
    age_sum = " + ".join(AGE_SEX_FIELDS)
    bad_age = connection.execute(
        f"SELECT COUNT(*) FROM counts_finest "
        f"WHERE population <> age_sex_unknown + {age_sum} "
        "OR population <> sex_male + sex_female + sex_unknown"
    ).fetchone()[0]
    if bad_age:
        raise AssertionError(f"Age/sex pyramid differs from population in {bad_age} units")
    for table in ("finest", "sector", "parroquia", "canton", "provincia", "nacion"):
        versions = connection.execute(
            f"SELECT DISTINCT geom_version FROM counts_{table}"
        ).fetchall()
        if versions != [(GEOM_VERSION,)]:
            raise AssertionError(f"Unexpected geometry version in {table}: {versions}")
    result = {
        "geom_version": GEOM_VERSION,
        "official_source": "INEC CPV 2022 CANTON CSV, población y vivienda",
        "national": {
            "population": national[0], "dwellings": national[1],
            "assigned_manzanas": national[2],
            "assigned_population": national[3],
            "assigned_dwellings": national[4],
        },
        "additivity": additivity,
        "category_additivity": category_additivity,
        "category_source_totals": category_source_totals,
        "official_comparison": official,
        "pyramid_mismatched_units": bad_age,
    }
    PUBLIC.mkdir(parents=True, exist_ok=True)
    (PUBLIC / "qa.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    connection.close()


if __name__ == "__main__":
    main()
