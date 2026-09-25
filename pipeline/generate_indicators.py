"""Validate the single indicator catalog and generate browser metadata and documentation."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import yaml
from aggregation import Aggregate
from indicators import LEVELS, CantonPrior, evaluate

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "indicators.yaml"
TYPESCRIPT = ROOT / "web/src/generated/indicators.json"
METHODOLOGY = ROOT / "docs/metodologia.md"
FIXTURES = ROOT / "tests/indicator_cases.json"
START = "<!-- INDICATOR_CATALOG_START -->"
END = "<!-- INDICATOR_CATALOG_END -->"
REQUIRED = {
    "id", "name", "theme", "kind", "formula", "population_reference",
    "source_variables", "min_level", "min_n", "direction", "palette",
    "methodological_note", "bibliography",
}


def load() -> dict:
    catalog = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    ids = set()
    for indicator in catalog["indicators"]:
        missing = REQUIRED - indicator.keys()
        if missing:
            raise ValueError(f"Missing catalog fields: {indicator.get('id')}: {missing}")
        if indicator["id"] in ids:
            raise ValueError(f"Duplicate indicator: {indicator['id']}")
        ids.add(indicator["id"])
        if indicator["min_level"] not in LEVELS or indicator["min_n"] < 1:
            raise ValueError(f"Invalid level/threshold: {indicator['id']}")
        if set(indicator["name"]) != {"es", "en"}:
            raise ValueError(f"Missing translation: {indicator['id']}")
        if indicator["kind"] == "ratio":
            if not indicator.get("numerator") or not indicator.get("denominator"):
                raise ValueError(f"Missing ratio terms: {indicator['id']}")
        elif indicator["kind"] == "shannon":
            if len(indicator.get("categories", [])) < 2:
                raise ValueError(f"Missing Shannon categories: {indicator['id']}")
        elif indicator["kind"] == "median_grouped":
            if len(indicator.get("age_groups", [])) != 21:
                raise ValueError(f"Expected 21 age groups: {indicator['id']}")
        elif indicator["kind"] == "weighted_mean":
            if not all(key in indicator for key in (
                "source_table", "source_variable", "valid_min", "valid_max"
            )):
                raise ValueError(f"Missing mean fields: {indicator['id']}")
        else:
            raise ValueError(f"Unsupported kind: {indicator['kind']}")
    return catalog


def render_documentation(catalog: dict) -> str:
    lines = [START, "## Catálogo de indicadores", "",
             "Generado desde [`indicators.yaml`](../indicators.yaml). `min_n` es el "
             "denominador mínimo para rankings, percentiles y gemelos.", "",
             "| Indicador (ES / EN) | Fórmula | Nivel mínimo | `min_n` | Fuente |",
             "| --- | --- | --- | ---: | --- |"]
    for item in catalog["indicators"]:
        source = ", ".join(item["source_variables"])
        lines.append(
            f"| {item['name']['es']} / {item['name']['en']} | "
            f"{item['formula']} | {item['min_level']} | {item['min_n']} | {source} |"
        )
    lines += ["", "### Indicadores descartados o pendientes", ""]
    for key in ("discarded_indicators", "deferred_indicators"):
        for item in catalog.get(key, []):
            lines.append(f"- `{item['id']}`: {item['reason']}")
    lines += ["", END]
    return "\n".join(lines)


def render_fixtures(catalog: dict) -> str:
    cases = []
    for item in catalog["indicators"]:
        keys = set()
        if item["kind"] == "ratio":
            keys.update(item["numerator"] + item["denominator"])
        elif item["kind"] in {"shannon", "median_grouped"}:
            for group in item.get("categories", item.get("age_groups", [])):
                keys.update(group)
        else:
            stem = f"cat:{item['source_table']}:{item['source_variable']}:"
            keys.update(stem + str(i) for i in range(item["valid_min"], item["valid_max"] + 1))
        counts = {key: 100 for key in sorted(keys)}
        for key in ("core:population", "core:dwellings", "core:households"):
            if key in counts:
                counts[key] = 100_000
        for variant in ("exact", "estimated", "small", "smoothing", "below_level"):
            level = item["min_level"]
            if variant == "below_level":
                index = LEVELS.index(level)
                if index == 0:
                    continue
                level = LEVELS[index - 1]
            quality = "estimado" if variant == "estimated" else "exacto"
            values = {key: value * (0.001 if variant == "small" else 1)
                      for key, value in counts.items()}
            aggregate = Aggregate(values, quality, 15.0 if quality == "estimado" else 0.0)
            smoothing = variant == "smoothing"
            prior = CantonPrior(0.35, 100.0) if smoothing else None
            expected = evaluate(item, aggregate, level=level, smoothing=smoothing,
                                canton_prior=prior)
            cases.append({"id": item["id"], "variant": variant, "level": level,
                          "aggregate": asdict(aggregate), "smoothing": smoothing,
                          "prior": asdict(prior) if prior else None,
                          "expected": asdict(expected)})
    return json.dumps(cases, ensure_ascii=False, indent=2) + "\n"


def generate(*, check: bool = False) -> None:
    catalog = load()
    browser = json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"
    current = METHODOLOGY.read_text(encoding="utf-8")
    section = render_documentation(catalog)
    if START in current:
        document = (
            current[:current.index(START)] + section
            + current[current.index(END) + len(END):]
        )
    else:
        document = current.rstrip() + "\n\n" + section + "\n"
    fixtures = render_fixtures(catalog)
    if check:
        if (TYPESCRIPT.read_text(encoding="utf-8") != browser
                or current != document
                or FIXTURES.read_text(encoding="utf-8") != fixtures):
            raise ValueError("Generated indicator catalog or methodology is stale")
        return
    TYPESCRIPT.parent.mkdir(parents=True, exist_ok=True)
    TYPESCRIPT.write_text(browser, encoding="utf-8")
    FIXTURES.write_text(fixtures, encoding="utf-8")
    METHODOLOGY.write_text(document, encoding="utf-8")
    print(f"Generated {len(catalog['indicators'])} indicators")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    generate(check=parser.parse_args().check)
