"""Build a small named-place search index from INEC DPA 2022 and Marco 2021."""

from __future__ import annotations

import json
from pathlib import Path

from place_names import SOURCE, official_catalog
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parents[1]
SHAPES = ROOT / "data/interim/tiles_v1b/source"
OUTPUT = ROOT / "web/src/generated/places.json"
SOURCE_URL = "https://www.censoecuador.gob.ec/informacion-geografica/"


def build() -> None:
    names = official_catalog(SOURCE)
    places = []
    missing = []
    for level in ("provincia", "canton", "parroquia"):
        with (SHAPES / f"{level}.geojsonl").open(encoding="utf-8") as stream:
            for line in stream:
                feature = json.loads(line)
                key = feature["properties"]["unit_key"]
                if key not in names:
                    missing.append(key)
                    continue
                geometry = shape(feature["geometry"])
                bounds = [round(value, 5) for value in geometry.bounds]
                places.append(
                    {
                        "key": key,
                        "name": names[key]["name"],
                        "official_name": names[key]["official_name"],
                        "level": level,
                        "parent": names.get(key[:4] if level == "parroquia" else key[:2],
                                            {"name": "Ecuador"})["name"],
                        "bbox": bounds,
                    }
                )
    if missing:
        raise ValueError(f"Missing official names ({len(missing)}): {missing}")
    places.sort(key=lambda item: (len(item["key"]), item["key"]))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {"geom_version": "marco-2021", "source": SOURCE_URL, "places": places},
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    print(f"Wrote {len(places)} official places, {OUTPUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    build()
