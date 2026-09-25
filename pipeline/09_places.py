"""Build a small official-place search index from INEC DPA 2022 and Marco 2021.

The INEC workbook has replacement glyphs in some names; these are preserved
instead of guessing missing accents. Geometry supplies only map bounds.
"""

from __future__ import annotations

import json
from pathlib import Path

import openpyxl
from shapely.geometry import shape

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/CODIFICACIÓN_2022.xlsx"
SHAPES = ROOT / "data/interim/tiles_v1b/source"
OUTPUT = ROOT / "web/src/generated/places.json"
SOURCE_URL = "https://www.censoecuador.gob.ec/informacion-geografica/"


def text(value: object) -> str:
    return str(value or "").strip().title()


def name_catalog() -> dict[str, str]:
    workbook = openpyxl.load_workbook(SOURCE, read_only=True, data_only=True)
    names = {}
    for row in list(workbook["PROVINCIAS"].values)[2:]:
        if row[1] and row[2]:
            names[str(row[1]).zfill(2)] = text(row[2])
    for row in list(workbook["CANTONES"].values)[2:]:
        if row[3] and row[4]:
            names[str(row[3]).zfill(4)] = text(row[4])
    for row in list(workbook["PARROQUIAS"].values)[2:]:
        if row[5] and row[6]:
            names[str(row[5]).zfill(6)] = text(row[6])
    return names


def build() -> None:
    names = name_catalog()
    places = []
    for level in ("provincia", "canton", "parroquia"):
        with (SHAPES / f"{level}.geojsonl").open(encoding="utf-8") as stream:
            for line in stream:
                feature = json.loads(line)
                key = feature["properties"]["unit_key"]
                geometry = shape(feature["geometry"])
                bounds = [round(value, 5) for value in geometry.bounds]
                places.append(
                    {
                        "key": key,
                        "name": names.get(key, key),
                        "level": level,
                        "parent": names.get(
                            key[:4] if level == "parroquia" else key[:2], "Ecuador"
                        ),
                        "bbox": bounds,
                    }
                )
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
