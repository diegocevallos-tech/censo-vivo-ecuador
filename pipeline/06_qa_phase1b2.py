"""End-to-end QA of phase 1B-2 aggregate products and the published SoVI formula."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import duckdb
import yaml
from aggregation import Aggregate
from indicators import evaluate

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data/interim"


def path(name: str) -> str:
    return (INTERIM / name).as_posix().replace("'", "''")


def check() -> None:
    db = duckdb.connect()
    source = path("exact_public/counts/v1b1")
    cross = path("cross_counts_v1b2")
    mobility = path("mobility_v1b2")
    geo = path("geodemographics_v1b2")
    spatial = path("spatial_v1b2")
    root = ROOT / "data/interim"
    sys.path.insert(0, str(ROOT / "pipeline"))
    from importlib import import_module

    import_module("03d_qa").check(root / "cross_counts_v1b2")
    base_pop, base_emigrants, base_deaths = db.execute(
        f"SELECT population,emigrants,deaths FROM read_parquet('{source}/nacion/data.parquet')"
    ).fetchone()
    emigrants = db.execute(
        f"SELECT SUM(emigrants) FROM read_parquet('{mobility}/emigrant_profile_parroquia.parquet')"
    ).fetchone()[0]
    deaths = db.execute(
        f"SELECT SUM(deaths) FROM read_parquet('{mobility}/death_profile_canton.parquet')"
    ).fetchone()[0]
    if (emigrants, deaths) != (base_emigrants, base_deaths):
        raise AssertionError("Event profile totals differ from exact national aggregates")
    flows, net = db.execute(
        f"SELECT SUM(internal_arrivals),SUM(internal_net) "
        f"FROM read_parquet('{mobility}/canton_net.parquet')"
    ).fetchone()
    flow_sum = db.execute(
        f"SELECT SUM(people) FROM read_parquet('{mobility}/canton_origin_destination.parquet')"
    ).fetchone()[0]
    if net != 0 or flows != flow_sum:
        raise AssertionError("Internal flow conservation failed")
    catalog = yaml.safe_load((ROOT / "indicators.yaml").read_text(encoding="utf-8"))
    sovi = next(item for item in catalog["indicators"] if item["id"] == "sovi_pca")
    metadata = json.loads((INTERIM / "geodemographics_v1b2/clusters.json").read_text(
        encoding="utf-8"
    ))
    population, groups, sectors = db.execute(f"""
        SELECT SUM(population), COUNT(DISTINCT "group"), COUNT(*)
        FROM read_parquet('{geo}/sector_clusters.parquet')
    """).fetchone()
    if (population, groups, sectors) != (base_pop, 8, 53_513):
        raise AssertionError("Cluster assignments are missing or duplicated")
    profiles = db.execute(
        f"SELECT COUNT(*) FROM read_parquet('{geo}/twin_profiles.parquet')"
    ).fetchone()[0]
    if profiles != sectors or len(metadata["features"]) != 40:
        raise AssertionError("Twin vectors or feature metadata are incomplete")
    sample = db.execute(f"""
        SELECT unit_key,sovi_pca FROM read_parquet('{geo}/sector_clusters.parquet')
        WHERE population>=500 AND rank_eligible ORDER BY hash(unit_key) LIMIT 10
    """).fetchall()
    full_categories = path("full_aggregate_v1a/counts/v1a/categories/sector/**/*.parquet")
    for key, saved in sample:
        core = db.execute(f"""
            SELECT * FROM read_parquet('{source}/sector/*.parquet') WHERE unit_key=?
        """, [key])
        base_counts = dict(zip((column[0] for column in core.description),
                               core.fetchone(), strict=True))
        counts = {f"core:{name}": value for name, value in base_counts.items()
                  if isinstance(value, (int, float))}
        row = db.execute(
            f"SELECT * FROM read_parquet('{cross}/sector/data.parquet') WHERE unit_key=?",
            [key],
        )
        counts.update({f"cross:{name}": value for name, value in zip(
            (column[0] for column in row.description), row.fetchone(), strict=True
        ) if isinstance(value, (int, float))})
        for table, variable, category, n in db.execute(f"""
            SELECT source_table,variable,category,n
            FROM read_parquet('{full_categories}')
            WHERE unit_key=? AND source_table='hogar' AND variable='HAC'
        """, [key]).fetchall():
            counts[f"cat:{table}:{variable}:{category}"] = n
        evaluated = evaluate(sovi, Aggregate(counts, "exacto", 0), level="sector")
        if evaluated.value is None or not math.isclose(
            evaluated.value, saved, abs_tol=1e-5
        ):
            parts = []
            for item in sovi["components"]:
                first = sum(counts.get(term, 0) for term in item["numerator"])
                first_d = sum(counts.get(term, 0) for term in item["denominator"])
                raw = first / first_d if first_d else None
                if "second_numerator" in item:
                    second = sum(counts.get(term, 0) for term in item["second_numerator"])
                    second_d = sum(counts.get(term, 0) for term in item["second_denominator"])
                    raw -= second / second_d if second_d else 0
                profile = db.execute(
                    f"SELECT z_{item['feature']} FROM read_parquet('{geo}/twin_profiles.parquet') "
                    "WHERE unit_key=?", [key],
                ).fetchone()[0]
                parts.append((item["feature"], raw, profile))
            raise AssertionError(
                f"Published SoVI differs from additive catalog: {key} "
                f"{evaluated.value} vs {saved}; {parts}"
            )
    matches = db.execute(f"""
        SELECT COUNT(DISTINCT unit_key) FROM read_parquet('{spatial}/lisa_sector.parquet')
    """).fetchone()[0]
    moran = db.execute(
        f"SELECT COUNT(*) FROM read_parquet('{spatial}/moran_canton.parquet')"
    ).fetchone()[0]
    dissim = db.execute(
        f"SELECT COUNT(*) FROM read_parquet('{spatial}/dissimilarity_canton.parquet')"
    ).fetchone()[0]
    if matches < .95 * sectors or moran != 221 * 6 or dissim != 221:
        raise AssertionError("Spatial outputs do not cover expected geography")
    forbidden = {"id_per", "id_hog", "id_viv"}
    for folder in ("cross_counts_v1b2", "mobility_v1b2", "geodemographics_v1b2",
                   "spatial_v1b2"):
        for file in (INTERIM / folder).rglob("*.parquet"):
            columns = {column[0].lower() for column in db.execute(
                f"DESCRIBE SELECT * FROM read_parquet('{file.as_posix()}')"
            ).fetchall()}
            if columns & forbidden:
                raise AssertionError(f"Personal identifier in aggregate: {file}")
    print(f"1B-2 QA passed: {sectors:,} sectors, {matches:,} mapped LISA sectors, "
          f"{flows:,} canton movements, {emigrants:,} emigrants, {deaths:,} deaths")


if __name__ == "__main__":
    check()
