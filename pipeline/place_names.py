"""Display names from the official INEC 2022 geographic classifier."""

from __future__ import annotations

import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/CODIFICACIÓN_2022.xlsx"
PARTICLES = {"de", "del", "la", "las", "los", "y"}
# The classifier's legal canton label is retained as official_name in the index.
# The shorter display name is the place name requested for map navigation.
DISPLAY_ALIASES = {"1701": "Quito"}


def title_name(value: object) -> str:
    original = unicodedata.normalize("NFC", str(value or "").strip())
    if not original or any(mark in original for mark in ("\ufffd", "Ã", "Â")):
        raise ValueError(f"Invalid geographic name: {original!r}")
    words = original.lower().title().split()
    return " ".join(word.lower() if index and word.lower() in PARTICLES else word
                    for index, word in enumerate(words))


def official_catalog(source: Path = SOURCE) -> dict[str, dict[str, str]]:
    import openpyxl

    workbook = openpyxl.load_workbook(source, read_only=True, data_only=True)
    names: dict[str, dict[str, str]] = {}
    for sheet, key_column, name_column, width in (
        ("PROVINCIAS", 1, 2, 2),
        ("CANTONES", 3, 4, 4),
        ("PARROQUIAS", 5, 6, 6),
    ):
        for row in list(workbook[sheet].values)[2:]:
            if not row[key_column] or not row[name_column]:
                continue
            key = str(row[key_column]).zfill(width)
            legal = title_name(row[name_column])
            display = DISPLAY_ALIASES.get(key, legal)
            if key in names and names[key]["official_name"] != legal:
                raise ValueError(f"Conflicting INEC name for {key}")
            names[key] = {"name": display, "official_name": legal}
    return names
