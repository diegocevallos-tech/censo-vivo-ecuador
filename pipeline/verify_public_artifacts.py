"""Reject raw records and oversized files before promoting Pages data."""

from __future__ import annotations

import argparse
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
    "unit_key", "unit_level", "province_key", "canton_key", "parish_key",
    "sector_key", "geom_version"
}
CORE_FIELDS = GEOGRAPHY_FIELDS | set(NUMERIC_FIELDS) | {
    "asignado_a_sector", "sector_disperso", "geografia_oculta",
    "detalle_en_sector", "celdas_suprimidas", "unit_index"
}
CATEGORY_FIELDS = {
    "unit_index", "variable_id", "category_id", "n", "geom_version"
}
CODEBOOK_FIELDS = {
    "variable_id", "category_id", "source_table", "variable",
    "category", "geom_version"
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=PUBLIC)
    args = parser.parse_args()
    root = args.root.resolve()
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
        elif path.suffix.lower() == ".parquet":
            import pyarrow.parquet as parquet

            columns = {name.lower() for name in parquet.read_schema(path).names}
            bad = columns & FORBIDDEN_FIELDS
            if bad:
                raise ValueError(f"Possible record identifier in {path}: {sorted(bad)}")
            if "counts" in path.parts and "v1a" in path.parts:
                if "categories" in path.parts:
                    if path.name == "codebook.parquet":
                        allowed = required = CODEBOOK_FIELDS
                    else:
                        allowed = required = CATEGORY_FIELDS
                else:
                    allowed = CORE_FIELDS
                    required = {
                        "unit_index", "unit_key", "population", "dwellings",
                        "households", "geom_version"
                    }
                if not required <= columns or not columns <= allowed:
                    raise ValueError(
                        f"Unexpected count Parquet schema in {path}: {sorted(columns)}"
                    )
    if total > MAX_SITE_DATA:
        raise ValueError(f"Pages data exceeds 1 GB: {total}")
    print(f"Verified {len(files)} public aggregate assets, {total} bytes")


if __name__ == "__main__":
    main()
