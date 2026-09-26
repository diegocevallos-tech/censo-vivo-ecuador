"""Reject raw records and oversized files before promoting Pages data."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

from counts_schema import NUMERIC_FIELDS

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "web/public/data"
ALLOWED = {".json", ".geojson", ".bin", ".pmtiles", ".parquet"}
FORBIDDEN_FIELDS = {"id_per", "id_hog", "id_viv", "i10", "p00"}
MAX_FILE = 95_000_000
MAX_SITE_DATA = 1_000_000_000
GEOGRAPHY_FIELDS = {
    "unit_key",
    "unit_level",
    "province_key",
    "canton_key",
    "parish_key",
    "sector_key",
    "geom_version",
}
EXACT_CORE_FIELDS = (
    GEOGRAPHY_FIELDS
    | set(NUMERIC_FIELDS)
    | {"asignado_a_sector", "sector_disperso", "geografia_oculta", "unit_index"}
)
CATEGORY_FIELDS = {"unit_index", "variable_id", "category_id", "n", "geom_version"}
CODEBOOK_FIELDS = {
    "variable_id",
    "category_id",
    "source_table",
    "variable",
    "category",
    "geom_version",
}
EXTRA_PARQUET = {
    "mobility/v1b2/canton_net.parquet": {
        "unit_key",
        "internal_arrivals",
        "internal_departures",
        "internal_net",
        "geom_version",
    },
    "mobility/v1b2/canton_origin_destination.parquet": {
        "origin_canton",
        "destination_canton",
        "people",
        "geom_version",
    },
    "mobility/v1b2/death_profile_canton.parquet": {
        "unit_key",
        "sex",
        "age_at_death",
        "death_year",
        "deaths",
        "geom_version",
    },
    "mobility/v1b2/emigrant_profile_parroquia.parquet": {
        "unit_key",
        "destination_country",
        "departure_year",
        "sex",
        "age_at_departure",
        "emigrants",
        "geom_version",
    },
    "mobility/v1b2/emigrant_profile_canton.parquet": {
        "unit_key", "sex", "age_at_departure", "destination_country",
        "emigrants", "geom_version",
    },
    "geodemographics/v1b2/sector_clusters.parquet": {
        "unit_key",
        "geom_version",
        "supergroup",
        "group",
        "population",
        "rank_eligible",
        "sovi_pca",
    },
    "spatial/v1b2/dissimilarity_canton.parquet": {
        "unit_key",
        "dissimilarity_education",
        "sectors",
        "geom_version",
    },
    "spatial/v1b2/moran_canton.parquet": {
        "unit_key",
        "indicator",
        "sectors",
        "moran_i",
        "permutation_p",
        "geom_version",
    },
}


def check_fields(value: object, path: Path) -> None:
    if isinstance(value, dict):
        bad = FORBIDDEN_FIELDS.intersection(key.lower() for key in value)
        if bad:
            raise ValueError(f"Possible record identifier in {path}: {sorted(bad)}")
        for item in value.values():
            check_fields(item, path)
    elif isinstance(value, list):
        for item in value:
            check_fields(item, path)


def verify(root: Path) -> None:
    root = root.resolve()
    cross_source = ast.parse((ROOT / "pipeline/03_cross_counts.py").read_text(encoding="utf-8"))
    cross_fields = set()
    for statement in cross_source.body:
        if isinstance(statement, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "NUMERATORS"
            for target in statement.targets
        ):
            cross_fields = set(ast.literal_eval(statement.value))
            break
    if not cross_fields:
        raise ValueError("Cross-count schema was not found")
    files = [path for path in root.rglob("*") if path.is_file() and path.name != ".gitkeep"]
    total = 0
    for path in files:
        if path.suffix.lower() not in ALLOWED:
            raise ValueError(f"Unapproved browser asset type: {path}")
        size = path.stat().st_size
        if size > MAX_FILE:
            raise ValueError(f"Browser asset exceeds 95 MB: {path} ({size})")
        total += size
        if path.suffix.lower() in {".json", ".geojson"}:
            check_fields(json.loads(path.read_text(encoding="utf-8")), path)
        elif path.suffix.lower() == ".pmtiles":
            if path.open("rb").read(7) != b"PMTiles":
                raise ValueError(f"Invalid PMTiles header: {path}")
        elif path.suffix.lower() == ".bin":
            if path.open("rb").read(5) not in {b"CVEB1", b"CVEP1", b"CVEL1", b"CVEI1"}:
                raise ValueError(f"Invalid binary chunk header: {path}")
            if "indicator-maps" in path.parts:
                import struct

                schema = json.loads(
                    (root / "indicator-maps/v2a/schema.json").read_text(encoding="utf-8")
                )
                relative = path.relative_to(root / "indicator-maps/v2a").as_posix()
                info = schema["files"].get(relative)
                with path.open("rb") as stream:
                    header = stream.read(11)
                rows, width = struct.unpack("<IH", header[5:])
                if (not info or header[:5] != b"CVEI1" or
                        width != len(schema["indicators"]) or rows != info["rows"] or
                        size != 11 + rows * schema["stride"]):
                    raise ValueError(f"Invalid indicator index schema or length: {path}")
        elif path.suffix.lower() == ".parquet":
            import pyarrow.parquet as parquet

            relative = path.relative_to(root).as_posix()
            columns = {name.lower() for name in parquet.read_schema(path).names}
            bad = columns & FORBIDDEN_FIELDS
            if bad:
                raise ValueError(f"Possible record identifier in {path}: {sorted(bad)}")
            if "counts" in path.parts and "v1b1" in path.parts:
                if "categories" in path.parts:
                    if path.name == "codebook.parquet":
                        allowed = required = CODEBOOK_FIELDS
                    else:
                        allowed = required = CATEGORY_FIELDS
                else:
                    allowed = EXACT_CORE_FIELDS
                    required = {
                        "unit_index",
                        "unit_key",
                        "population",
                        "dwellings",
                        "households",
                        "geom_version",
                    }
                if not required <= columns or not columns <= allowed:
                    raise ValueError(
                        f"Unexpected count Parquet schema in {path}: {sorted(columns)}"
                    )
            elif relative.startswith("cross/v1b2/"):
                required = {"unit_key", "geom_version"}
                allowed = required | GEOGRAPHY_FIELDS | cross_fields
                if not required <= columns or not columns <= allowed:
                    raise ValueError(f"Unexpected cross-count columns: {relative}")
            elif relative.startswith("geodemographics/v1b2/twin_profiles_"):
                if (not {"unit_key", "geom_version", "rank_eligible"} <= columns
                        or len([name for name in columns if name.startswith("z_")]) != 40
                        or len(columns) != 43):
                    raise ValueError(f"Unexpected twin profile schema: {relative}")
            elif relative == "spatial/v1b2/moran_canton.parquet":
                extra = {"regularized_sectors", "queen_islands_connected"}
                if not EXTRA_PARQUET[relative] <= columns or not columns <= (
                    EXTRA_PARQUET[relative] | extra
                ):
                    raise ValueError(f"Unexpected Moran schema: {relative}")
            elif relative in EXTRA_PARQUET:
                if columns != EXTRA_PARQUET[relative]:
                    raise ValueError(f"Unexpected aggregate schema: {relative}")
            elif "sample" not in path.parts:
                raise ValueError(f"Unexpected Parquet: {relative}")
    if total > MAX_SITE_DATA:
        raise ValueError(f"Pages data exceeds 1 GB: {total}")
    print(f"Verified {len(files)} public aggregate assets, {total} bytes")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=PUBLIC)
    args = parser.parse_args()
    verify(args.root)


if __name__ == "__main__":
    main()
