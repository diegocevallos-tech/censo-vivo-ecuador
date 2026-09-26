"""Assign official INEC blocks to municipal urban parishes by block centroid.

Municipal boundaries are reference geography, never INEC census units. All
counts are sums of official block aggregates; blocks without geometry remain
at their official census sector and are not assigned to an urban parish.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pyogrio
import shapely
from place_names import title_name
from pyproj import Transformer
from shapely.geometry import mapping as geom_mapping
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/MUNICIPAL_SOURCES.json"
MARCO = ROOT / "data/raw/GEODATABASE_NACIONAL_2021/GEODATABASE_NACIONAL_2021.gpkg"
COUNTS = ROOT / "data/interim/exact_public/counts/v1b1"
OUT = ROOT / "data/interim/municipal_urban"
TO_WGS84 = Transformer.from_crs("EPSG:32717", "EPSG:4326", always_xy=True)

# The municipal services abbreviate or omit some accents. These full forms are
# corroborated by the municipality-name audit in docs/fuentes/parroquias_urbanas.md.
NAME_OVERRIDES = {
    ("quito", "ITCHIMBIA"): "Itchimbía",
    ("quito", "GUAMANI"): "Guamaní",
    ("guayaquil", "BOLIVAR"): "Bolívar",
    ("cuenca", "GIL RAMIREZ D."): "Gil Ramírez Dávalos",
    ("cuenca", "HUAYNA CAPAC"): "Huayna Cápac",
    ("cuenca", "EL BATAN"): "El Batán",
    ("cuenca", "MACHANGARA"): "Machángara",
    ("loja", "CARIGAN"): "Carigán",
    ("ambato", "LA PENINSULA"): "La Península",
    ("riobamba", "YARUQUIES"): "Yaruquíes",
}


def slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return re.sub(r"[^a-z0-9]+", "-", "".join(
        ch for ch in normalized.lower() if not unicodedata.combining(ch))).strip("-")


def source_shapes(city: str, spec: dict) -> gpd.GeoDataFrame:
    raw = (ROOT / spec["file"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != spec["sha256"]:
        raise ValueError(f"Municipal checksum mismatch: {city}")
    document = json.loads(raw)
    if len(document["features"]) != spec["features"]:
        raise ValueError(f"Municipal feature count changed: {city}")
    records = []
    for feature in document["features"]:
        prop = feature["properties"]
        code = str(prop.get(spec["code_field"]) or "") if spec["code_field"] else ""
        if city == "quito" and code not in {f"1701{n:02d}" for n in range(1, 33)}:
            continue
        source_name = str(prop[spec["name_field"]]).strip()
        display = NAME_OVERRIDES.get((city, source_name), title_name(source_name))
        geometry = shape(feature["geometry"])
        if not geometry.is_valid:
            geometry = shapely.make_valid(geometry)
        if geometry.is_empty or geometry.geom_type not in {"Polygon", "MultiPolygon"}:
            raise ValueError(f"Invalid municipal polygon: {city} {source_name}")
        records.append({"source_name": source_name, "name": display,
                        "source_code": code, "geometry": geometry})
    frame = gpd.GeoDataFrame(records, crs=spec["crs"]).to_crs("EPSG:32717")
    grouped = []
    for name, subset in frame.groupby("name", sort=True):
        codes = sorted(set(subset["source_code"]) - {""})
        if len(codes) > 1:
            raise ValueError(f"Conflicting municipal codes for {city} {name}: {codes}")
        code = codes[0] if codes else ""
        # Prefix makes this an explicit technical key, never an INEC parish code.
        urban_id = f"municipal:{city}:{code or slug(name)}"
        geometry = shapely.union_all(subset.geometry.to_numpy())
        grouped.append({"urban_id": urban_id, "city": spec["city"], "name": name,
                        "source_code": code, "geometry": geometry})
    result = gpd.GeoDataFrame(grouped, crs="EPSG:32717")
    if result["urban_id"].duplicated().any():
        raise ValueError(f"Duplicate urban IDs: {city}")
    return result


def census_blocks(spec: dict) -> tuple[gpd.GeoDataFrame, pd.DataFrame, int]:
    prefix = spec["census_parish"]
    geometry = pyogrio.read_dataframe(MARCO, layer="man_a", columns=["man"],
                                      where=f"man LIKE '{prefix}%'")
    if geometry.crs is None:
        raise ValueError("INEC man_a has no CRS")
    geometry = geometry.to_crs("EPSG:32717")
    geometry = geometry.rename(columns={"man": "manzana_key"})
    province = prefix[:2]
    table = pq.read_table(COUNTS / "finest" / f"{province}.parquet").to_pandas()
    table = table[table["unit_key"].str.startswith(prefix) & (table["unit_key"].str.len() == 15)]
    numbers = table.select_dtypes(include="number").columns.tolist()
    numbers.remove("unit_index")
    table = table[["unit_key", *numbers]].rename(columns={"unit_key": "manzana_key"})
    if table["manzana_key"].duplicated().any() or geometry["manzana_key"].duplicated().any():
        raise ValueError(f"Duplicate INEC block: {prefix}")
    official = pq.read_table(COUNTS / "parroquia" / "data.parquet",
                             columns=["unit_key", "population"]).to_pandas()
    official_population = int(official.loc[official["unit_key"] == prefix, "population"].sum())
    polygon_population = int(table.loc[table["manzana_key"].isin(geometry["manzana_key"]),
                                       "population"].sum())
    if polygon_population > official_population:
        raise ValueError(f"Matched blocks exceed official parish total: {prefix}")
    return geometry, table, official_population


def age_sum(row: pd.Series, first: int, last: int) -> int:
    result = 0
    for start in range(first, min(last, 99) + 1, 5):
        end = min(start + 4, 99)
        for sex in ("m", "f"):
            result += int(row.get(f"age_{start:02d}_{end:02d}_{sex}", 0))
    if last >= 100:
        result += int(row.get("age_100_120_m", 0)) + int(row.get("age_100_120_f", 0))
    return result


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if len(manifest["sources"]) != 6:
        raise ValueError("Expected all six official municipal sources")
    OUT.mkdir(parents=True, exist_ok=True)
    all_shapes = []
    assignments = []
    aggregated = []
    city_reports = []
    summaries = []
    for spec in manifest["sources"]:
        city = Path(spec["file"]).stem
        boundaries = source_shapes(city, spec)
        blocks, block_counts, official_population = census_blocks(spec)
        centroids = gpd.GeoDataFrame(blocks[["manzana_key"]].copy(),
                                     geometry=blocks.geometry.centroid, crs=blocks.crs)
        joined = gpd.sjoin(centroids, boundaries[["urban_id", "geometry"]],
                           how="left", predicate="within")
        duplicate = joined.loc[joined["manzana_key"].duplicated(False), "manzana_key"].unique()
        if len(duplicate):
            raise ValueError(
                f"Overlapping municipal boundaries for {city}: {len(duplicate)} blocks"
            )
        mapping = joined[["manzana_key", "urban_id"]].dropna(subset=["urban_id"])
        assigned = block_counts.merge(mapping, on="manzana_key", how="inner")
        if len(assigned) > len(mapping):
            raise ValueError(f"Duplicated count for mapped block: {city}")
        numeric = assigned.select_dtypes(include="number").columns.tolist()
        totals = assigned.groupby("urban_id", as_index=False)[numeric].sum()
        if len(totals) != len(boundaries):
            missing = set(boundaries["urban_id"]) - set(totals["urban_id"])
            raise ValueError(f"Municipal polygons without census blocks: {city} {missing}")
        mapped_population = int(assigned["population"].sum())
        polygon_population = int(block_counts.loc[
            block_counts["manzana_key"].isin(blocks["manzana_key"]), "population"].sum())
        outside_population = polygon_population - mapped_population
        no_polygon_population = official_population - polygon_population
        if mapped_population + outside_population + no_polygon_population != official_population:
            raise ValueError(f"Population QA failed: {city}")
        counts = Counter(mapping["urban_id"])
        for _, row in totals.iterrows():
            urban_id = row["urban_id"]
            younger = age_sum(row, 0, 14)
            older = age_sum(row, 65, 120)
            summary = {
                "urban_id": urban_id, "city": spec["city"],
                "name": boundaries.loc[boundaries["urban_id"] == urban_id, "name"].iloc[0],
                "source_code": boundaries.loc[boundaries["urban_id"] == urban_id,
                                              "source_code"].iloc[0],
                "population": int(row["population"]), "dwellings": int(row["dwellings"]),
                "households": int(row["households"]), "blocks": counts[urban_id],
                "age_0_14": younger, "age_65_plus": older,
                "aging_index": round(100 * older / younger, 9) if younger else None,
                "boundary_type": "municipal, no censal",
                "assignment": "centroide de manzana del Marco 2021",
            }
            summaries.append(summary)
        city_reports.append({"city": spec["city"], "municipal_parishes": len(boundaries),
                             "census_parish": spec["census_parish"],
                             "blocks_with_geometry": len(blocks),
                             "blocks_with_geometry_and_counts": int(blocks["manzana_key"].isin(
                                 block_counts["manzana_key"]).sum()),
                             "blocks_assigned": len(mapping),
                             "blocks_assigned_with_counts": len(assigned),
                             "blocks_outside": len(blocks) - len(mapping),
                             "mapped_population": mapped_population,
                             "outside_population": outside_population,
                             "no_polygon_population": no_polygon_population,
                             "official_census_parish_population": official_population})
        mapping.insert(0, "city", spec["city"])
        assignments.append(mapping)
        totals.insert(0, "city", spec["city"])
        aggregated.append(totals)
        all_shapes.append(boundaries)
        print(f"{spec['city']}: {len(boundaries)} parishes; "
              f"{len(mapping)}/{len(blocks)} blocks assigned; "
              f"{mapped_population}/{official_population} people", flush=True)
    pq.write_table(pa.Table.from_pandas(pd.concat(assignments, ignore_index=True),
                                         preserve_index=False),
                   OUT / "manzana_to_urban.parquet", compression="zstd")
    pq.write_table(pa.Table.from_pandas(pd.concat(aggregated, ignore_index=True),
                                         preserve_index=False),
                   OUT / "urban_counts.parquet", compression="zstd")
    features = []
    for boundaries in all_shapes:
        for _, row in boundaries.iterrows():
            simplified = shapely.simplify(row.geometry, 8, preserve_topology=True)
            wgs = shapely.transform(simplified, TO_WGS84.transform, interleaved=False)
            features.append({"type": "Feature", "geometry": geom_mapping(wgs), "properties": {
                "urban_id": row["urban_id"], "name": row["name"], "city": row["city"],
                "source_code": row["source_code"], "boundary_type": "municipal, no censal",
            }})
    (OUT / "boundaries.geojson").write_text(json.dumps({"type": "FeatureCollection",
        "features": features}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / "summary.json").write_text(json.dumps({"geom_version": "marco-2021",
        "boundary_version": "fuentes-municipales-2022-2025", "source_manifest":
        "data/MUNICIPAL_SOURCES.json", "parishes": summaries, "cities": city_reports},
        ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Iñaquito: {next(x for x in summaries if x['source_code'] == '170112')}", flush=True)


if __name__ == "__main__":
    main()
