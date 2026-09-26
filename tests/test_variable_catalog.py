"""Metadata checks that run without access to private raw census records."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "web/public/meta/variables.json"


def test_dictionary_catalog_is_complete_and_bilingual() -> None:
    values = json.loads(CATALOG.read_text(encoding="utf-8"))["variables"]
    ids = [item["id"] for item in values]
    assert len(values) == 136
    assert len(ids) == len(set(ids))
    assert {item["table"] for item in values} == {
        "vivienda", "hogar", "poblacion", "emigracion", "mortalidad"
    }
    assert sum(item["available"] for item in values) == 126
    for item in values:
        assert item["theme"] and item["question"]["es"]
        assert item["name"]["es"] and item["name"]["en"] != item["id"]
        assert item["universe"]["es"] and item["universe"]["en"]
        assert item["min_level"] in {"manzana", "sector", "parroquia", "canton"}
        assert item["type"] in {"categorical", "numeric"}
        for category in item["categories"]:
            assert category["label"]["es"] and category["label"]["en"]


def test_known_dictionary_variables_and_source_level() -> None:
    values = {item["id"]: item for item in json.loads(
        CATALOG.read_text(encoding="utf-8"))["variables"]}
    assert values["V03"]["name"]["es"] == "Material predominante del techo o cubierta"
    assert values["V03"]["categories"][0]["label"] == {
        "es": "Hormigón (losa, cemento)", "en": "Concrete slab or cement"
    }
    assert values["P11R"]["min_level"] == "sector"
    assert values["P08P"]["min_level"] == "canton"
    assert values["P03"]["type"] == "numeric"
    assert len(values["P03"]["categories"]) == 21
