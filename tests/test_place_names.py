"""Official-place typography does not guess or corrupt accented names."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
from place_names import title_name  # noqa: E402


def test_title_case_with_particles_and_accents() -> None:
    assert title_name("IÑAQUITO") == "Iñaquito"
    assert title_name("SAN MIGUEL DE LOS BANCOS") == "San Miguel de los Bancos"
    assert title_name("CALDERÓN") == "Calderón"
    assert title_name("RÍO VERDE Y LA UNIÓN") == "Río Verde y la Unión"


def test_generated_catalog_has_no_missing_or_corrupt_names() -> None:
    places = json.loads((ROOT / "web/src/generated/places.json").read_text(
        encoding="utf-8"
    ))["places"]
    expected = {"provincia": 24, "canton": 221, "parroquia": 1_042}
    for level, count in expected.items():
        entries = [place for place in places if place["level"] == level]
        assert len(entries) == count
        missing = [place["key"] for place in entries if not place["name"]
                   or place["name"] == place["key"]]
        assert not missing, f"{level}: missing names for {missing}"
        invalid = [place["key"] for place in entries if place["name"].isupper()
                   or any(mark in place["name"] for mark in ("\ufffd", "Ã", "Â"))]
        assert not invalid, f"{level}: invalid typography for {invalid}"
