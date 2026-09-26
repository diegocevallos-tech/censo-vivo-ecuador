"""Publish Marco 2021 zon_a polygons joined to exact I04 aggregate keys."""

from __future__ import annotations

import argparse
import json
import subprocess
from importlib import import_module
from pathlib import Path

import pyarrow.parquet as pq
import pyogrio

tiles = import_module("06_tiles")
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/interim/tiles_v1b/source/zona.geojsonl"
CATALOG = ROOT / "web/public/data/tiles/v1b/catalog.json"
DESTINATION = ROOT / "web/public/data/tiles/v1b/zona/data.pmtiles"
COUNTS = ROOT / "data/interim/exact_public/counts/v1b1/zona/data.parquet"
MIN_ZOOM, MAX_ZOOM, TOLERANCE = 9, 12, 8


def prepare() -> dict:
    if not CATALOG.is_file() or not COUNTS.is_file() or not tiles.GEOMETRY.is_file():
        raise FileNotFoundError("Restore verified Marco 2021, zone counts and tile catalog")
    rows = pq.read_table(COUNTS, columns=["unit_key", "population", "assigned_population"])
    lookup = {key: (population, assigned) for key, population, assigned in zip(
        rows["unit_key"].to_pylist(), rows["population"].to_pylist(),
        rows["assigned_population"].to_pylist(), strict=True)}
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    geometry_keys: set[str] = set()
    matched = 0
    with SOURCE.open("w", encoding="utf-8", newline="\n") as stream:
        total = pyogrio.read_info(tiles.GEOMETRY, layer="zon_a")["features"]
        for offset in range(0, total, 250):
            frame = pyogrio.read_dataframe(tiles.GEOMETRY, layer="zon_a",
                                          columns=["zon"], skip_features=offset,
                                          max_features=250)
            for key, geometry in zip(frame["zon"], frame.geometry, strict=True):
                if (not isinstance(key, str) or len(key) != 9
                        or geometry is None or geometry.is_empty):
                    continue
                if key in geometry_keys:
                    raise AssertionError(f"Duplicate Marco 2021 zone polygon: {key}")
                geometry_keys.add(key)
                count = lookup.get(key)
                if count:
                    matched += 1
                tiles.write_feature(stream, tiles.feature(
                    key, geometry, tiles.area_km2(geometry), count, TOLERANCE))
    missing = sorted(set(lookup) - geometry_keys)
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    catalog["levels"]["zona"] = {"minzoom": MIN_ZOOM, "maxzoom": MAX_ZOOM}
    catalog["matched_geometries"]["zona"] = matched
    catalog["census_units"]["zona"] = len(lookup)
    catalog["tile_files"]["zona"] = ["data"]
    catalog["unmapped_zone_keys"] = len(missing)
    CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, separators=(",", ":")) + "\n",
                       encoding="utf-8")
    report = {"census_zones": len(lookup), "polygons": len(geometry_keys),
              "matched": matched, "without_polygon": len(missing),
              "without_polygon_keys": missing, "source_bytes": SOURCE.stat().st_size}
    print(json.dumps(report, ensure_ascii=False))
    return report


def tile() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["tippecanoe", "-Q", "-f", "-P", "-o", str(DESTINATION),
                    "-l", "zona", "-Z", str(MIN_ZOOM), "-z", str(MAX_ZOOM),
                    "--no-feature-limit", "--no-tile-size-limit", "-A",
                    "INEC CPV 2022; geometría Marco 2021", str(SOURCE)], check=True)
    if DESTINATION.stat().st_size > 90_000_000:
        raise ValueError("Zone PMTiles exceeds 90 MB")
    print(f"{DESTINATION.relative_to(ROOT)}: {DESTINATION.stat().st_size} bytes")


if __name__ == "__main__":
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
