"""Add official display names to the three administrative GeoJSONL tile sources."""

from __future__ import annotations

import json
from pathlib import Path

from place_names import official_catalog

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/interim/tiles_v1b/source"
LEVELS = ("provincia", "canton", "parroquia")


def add_names(source: Path = SOURCE) -> dict[str, int]:
    catalog = official_catalog()
    counts = {}
    missing = []
    for level in LEVELS:
        path = source / f"{level}.geojsonl"
        temporary = path.with_suffix(".named.tmp")
        count = 0
        with path.open(encoding="utf-8") as original, temporary.open(
            "w", encoding="utf-8", newline="\n"
        ) as named:
            for line in original:
                item = json.loads(line)
                key = item["properties"]["unit_key"]
                if key not in catalog:
                    missing.append(key)
                    continue
                item["properties"]["name"] = catalog[key]["name"]
                named.write(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n")
                count += 1
        if missing:
            temporary.unlink()
            raise ValueError(f"Missing INEC names: {missing}")
        temporary.replace(path)
        counts[level] = count
    return counts


if __name__ == "__main__":
    print(add_names())
