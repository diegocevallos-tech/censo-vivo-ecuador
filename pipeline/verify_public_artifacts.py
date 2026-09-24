"""Reject raw records and oversized files before promoting Pages data."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "web/public/data"
ALLOWED = {".json", ".geojson", ".bin", ".pmtiles", ".parquet"}
FORBIDDEN_FIELDS = {"id_per", "id_hog", "id_viv", "i10", "p00"}
MAX_FILE = 100_000_000
MAX_SITE_DATA = 900_000_000


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
    files = [path for path in PUBLIC.rglob("*") if path.is_file() and path.name != ".gitkeep"]
    total = 0
    for path in files:
        if path.suffix.lower() not in ALLOWED:
            raise ValueError(f"Unapproved browser asset type: {path}")
        size = path.stat().st_size
        if size >= MAX_FILE:
            raise ValueError(f"Browser asset exceeds 100 MB: {path} ({size})")
        total += size
        if path.suffix.lower() in {".json", ".geojson"}:
            check_fields(json.loads(path.read_text(encoding="utf-8")), path)
        elif path.suffix.lower() == ".parquet":
            import pyarrow.parquet as parquet

            columns = {name.lower() for name in parquet.read_schema(path).names}
            bad = columns & FORBIDDEN_FIELDS
            if bad:
                raise ValueError(f"Possible record identifier in {path}: {sorted(bad)}")
    if total > MAX_SITE_DATA:
        raise ValueError(f"Pages data exceeds 900 MB: {total}")
    print(f"Verified {len(files)} public aggregate assets, {total} bytes")


if __name__ == "__main__":
    main()
