"""Join official-unit counts to Marco 2021 and build bounded PMTiles.

The geometry can be replaced without recomputing the census counts. Source
GeoJSON sequences and PMTiles live in ignored directories until Release upload.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from collections import defaultdict
from pathlib import Path

import pyarrow.parquet as pq
import pyogrio
import shapely
from pyproj import Transformer
from shapely.geometry import mapping

ROOT = Path(__file__).resolve().parents[1]
GEOMETRY = ROOT / "data/raw/GEODATABASE_NACIONAL_2021/GEODATABASE_NACIONAL_2021.gpkg"
UNMATCHED_REPORT = ROOT / "docs/qa/manzanas_sin_match.csv"
COUNTS = ROOT / "data/interim/exact_public/counts/v1b1"
SOURCE = ROOT / "data/interim/tiles_v1b/source"
PUBLIC = ROOT / "web/public/data/tiles/v1b"
GEOM_VERSION = "marco-2021"
PROVINCES = tuple(f"{number:02d}" for number in range(1, 25))
TO_WGS84 = Transformer.from_crs("EPSG:32717", "EPSG:4326", always_xy=True)
TO_EQUAL_AREA = Transformer.from_crs("EPSG:32717", "EPSG:6933", always_xy=True)
LEVELS = {
    "nacion": (0, 4, 250),
    "provincia": (3, 7, 100),
    "canton": (6, 10, 35),
    "parroquia": (8, 12, 12),
    "sector": (10, 14, 5),
    "manzana": (13, 16, 1),
}


def count_lookup(level: str) -> dict[str, tuple[int, int]]:
    root = COUNTS / ("finest" if level == "manzana" else level)
    paths = (
        sorted(root.glob("*.parquet"))
        if level in {"manzana", "sector"}
        else [root / "data.parquet"]
    )
    result: dict[str, tuple[int, int]] = {}
    for path in paths:
        table = pq.read_table(path, columns=["unit_key", "population", "assigned_population"])
        for key, population, assigned in zip(
            table["unit_key"].to_pylist(),
            table["population"].to_pylist(),
            table["assigned_population"].to_pylist(),
            strict=True,
        ):
            result[key] = (population, assigned)
    return result


def project(geometry: shapely.Geometry, transformer: Transformer) -> shapely.Geometry:
    return shapely.transform(geometry, transformer.transform, interleaved=False)


def area_km2(geometry: shapely.Geometry) -> float:
    return float(project(geometry, TO_EQUAL_AREA).area) / 1_000_000


def feature(
    key: str,
    geometry: shapely.Geometry,
    area: float,
    count: tuple[int, int] | None,
    tolerance: float,
) -> dict:
    shape = shapely.simplify(geometry, tolerance, preserve_topology=True)
    if shape.is_empty:
        shape = geometry
    population, assigned = count if count is not None else (None, 0)
    return {
        "type": "Feature",
        "properties": {
            "unit_key": key,
            "population": population,
            "assigned_population": assigned,
            "area_km2": round(area, 5),
            "density": round(population / area, 2) if population is not None and area > 0 else None,
            "geom_version": GEOM_VERSION,
        },
        "geometry": mapping(project(shape, TO_WGS84)),
    }


def write_feature(stream, item: dict) -> None:
    stream.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")


def prepare() -> dict:
    if not GEOMETRY.is_file() or not (COUNTS / "schema.json").is_file():
        raise FileNotFoundError("Verified Marco 2021 and exact official-unit counts are required")
    SOURCE.mkdir(parents=True, exist_ok=True)
    lookups = {level: count_lookup(level) for level in LEVELS}
    sector_groups: dict[str, list[shapely.Geometry]] = defaultdict(list)
    area_sums: dict[str, float] = defaultdict(float)
    province_bounds: dict[str, list[float]] = {}
    matched: dict[str, int] = defaultdict(int)
    # Streaming batches bound peak memory for the 4.5 GB GeoPackage.
    sector_streams = {
        province: (SOURCE / f"sector_{province}.geojsonl").open("w", encoding="utf-8")
        for province in PROVINCES
    }
    try:
        total = pyogrio.read_info(GEOMETRY, layer="sec_a")["features"]
        for start in range(0, total, 2_000):
            frame = pyogrio.read_dataframe(
                GEOMETRY,
                layer="sec_a",
                columns=["sec"],
                skip_features=start,
                max_features=2_000,
            )
            for key, geometry in zip(frame["sec"], frame.geometry, strict=True):
                if (
                    not isinstance(key, str)
                    or len(key) != 12
                    or geometry is None
                    or geometry.is_empty
                ):
                    continue
                province = key[:2]
                if province not in sector_streams:
                    continue
                area = area_km2(geometry)
                for group in (province, key[:4], key[:6]):
                    sector_groups[group].append(geometry)
                    area_sums[group] += area
                count = lookups["sector"].get(key)
                matched["sector"] += count is not None
                item = feature(key, geometry, area, count, LEVELS["sector"][2])
                write_feature(sector_streams[province], item)
                # Bounds use the transformed polygon, independent of any counts.
                extent = shapely.bounds(project(geometry, TO_WGS84))
                old = province_bounds.setdefault(
                    province, [float("inf"), float("inf"), float("-inf"), float("-inf")]
                )
                old[0] = min(old[0], extent[0])
                old[1] = min(old[1], extent[1])
                old[2] = max(old[2], extent[2])
                old[3] = max(old[3], extent[3])
            print(f"Sector geometry {min(start + 2_000, total)}/{total}", flush=True)
    finally:
        for stream in sector_streams.values():
            stream.close()

    province_geometries = []
    for level, key_length in (("provincia", 2), ("canton", 4), ("parroquia", 6), ("nacion", 0)):
        with (SOURCE / f"{level}.geojsonl").open("w", encoding="utf-8") as stream:
            keys = (
                ["EC"]
                if level == "nacion"
                else sorted(key for key in sector_groups if len(key) == key_length)
            )
            for key in keys:
                geometries = province_geometries if level == "nacion" else sector_groups[key]
                try:
                    geometry = shapely.union_all(geometries)
                except shapely.GEOSException:
                    geometry = shapely.union_all(
                        [shapely.make_valid(value) for value in geometries]
                    )
                if level == "provincia":
                    province_geometries.append(geometry)
                count = lookups[level].get(key)
                matched[level] += count is not None
                area = (
                    sum(area_sums[province] for province in PROVINCES)
                    if level == "nacion"
                    else area_sums[key]
                )
                write_feature(stream, feature(key, geometry, area, count, LEVELS[level][2]))
        print(f"Prepared {level}: {len(keys)} polygons", flush=True)
    sector_groups.clear()

    manzana_streams = {
        province: (SOURCE / f"manzana_{province}.geojsonl").open("w", encoding="utf-8")
        for province in PROVINCES
    }
    try:
        total = pyogrio.read_info(GEOMETRY, layer="man_a")["features"]
        for start in range(0, total, 5_000):
            frame = pyogrio.read_dataframe(
                GEOMETRY,
                layer="man_a",
                columns=["man"],
                skip_features=start,
                max_features=5_000,
            )
            for key, geometry in zip(frame["man"], frame.geometry, strict=True):
                if (
                    not isinstance(key, str)
                    or len(key) != 15
                    or geometry is None
                    or geometry.is_empty
                ):
                    continue
                province = key[:2]
                if province not in manzana_streams:
                    continue
                count = lookups["manzana"].get(key)
                matched["manzana"] += count is not None
                write_feature(
                    manzana_streams[province],
                    feature(key, geometry, area_km2(geometry), count, LEVELS["manzana"][2]),
                )
            print(f"Manzana geometry {min(start + 5_000, total)}/{total}", flush=True)
    finally:
        for stream in manzana_streams.values():
            stream.close()

    with UNMATCHED_REPORT.open(encoding="utf-8", newline="") as stream:
        assigned_manzanas = len(list(csv.DictReader(stream)))
    catalog = {
        "geom_version": GEOM_VERSION,
        "levels": {
            level: {"minzoom": low, "maxzoom": high} for level, (low, high, _) in LEVELS.items()
        },
        "province_bounds": province_bounds,
        "matched_geometries": matched,
        "census_units": {level: len(lookup) for level, lookup in lookups.items()},
        "assigned_manzanas_without_polygon": assigned_manzanas,
    }
    (SOURCE / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"matched": matched, "census": catalog["census_units"]}), flush=True)
    return catalog


def tile() -> None:
    catalog = json.loads((SOURCE / "catalog.json").read_text(encoding="utf-8"))
    PUBLIC.mkdir(parents=True, exist_ok=True)
    catalog["tile_files"] = {}
    for level, (minimum, maximum, _) in LEVELS.items():
        provinces = PROVINCES if level in {"sector", "manzana"} else (None,)
        catalog["tile_files"][level] = []
        for province in provinces:
            suffix = f"_{province}" if province else ""
            source = SOURCE / f"{level}{suffix}.geojsonl"
            if source.stat().st_size == 0:
                continue
            destination = PUBLIC / level / f"{province or 'data'}.pmtiles"
            destination.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [
                    "tippecanoe",
                    "-Q",
                    "-f",
                    "-P",
                    "-o",
                    str(destination),
                    "-l",
                    level,
                    "-Z",
                    str(minimum),
                    "-z",
                    str(maximum),
                    "--no-feature-limit",
                    "--no-tile-size-limit",
                    "-A",
                    "INEC CPV 2022; geometría Marco 2021",
                    str(source),
                ],
                check=True,
            )
            if destination.stat().st_size > 90_000_000:
                raise ValueError(f"Tile exceeds 90 MB; split level/province: {destination}")
            catalog["tile_files"][level].append(province or "data")
            print(f"{destination.relative_to(ROOT)}: {destination.stat().st_size}", flush=True)
    (PUBLIC / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--tile", action="store_true")
    args = parser.parse_args()
    if not (args.prepare or args.tile):
        parser.error("Choose --prepare and/or --tile")
    if args.prepare:
        prepare()
    if args.tile:
        tile()


if __name__ == "__main__":
    main()
