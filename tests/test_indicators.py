"""Catalog-generated cross-language cases and small-n policy."""

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
from aggregation import Aggregate  # noqa: E402
from generate_indicators import generate, load  # noqa: E402
from indicators import CantonPrior, evaluate, fit_canton_prior  # noqa: E402


def test_generated_catalog_current() -> None:
    generate(check=True)
    assert len(load()["indicators"]) == 45


def test_shared_indicator_cases() -> None:
    definitions = {item["id"]: item for item in load()["indicators"]}
    cases = json.loads((ROOT / "tests/indicator_cases.json").read_text(encoding="utf-8"))
    assert len(cases) >= 100
    for case in cases:
        prior = CantonPrior(**case["prior"]) if case["prior"] else None
        result = evaluate(
            definitions[case["id"]], Aggregate(**case["aggregate"]),
            level=case["level"], smoothing=case["smoothing"], canton_prior=prior,
        )
        expected = case["expected"]
        assert result.small_n == expected["small_n"]
        assert result.rank_eligible == expected["rank_eligible"]
        assert result.unavailable_reason == expected["unavailable_reason"]
        if expected["value"] is None:
            assert result.value is None
        else:
            assert math.isclose(result.value, expected["value"], abs_tol=1e-9)


def test_small_n_not_ranked_and_smoothing_off_by_default() -> None:
    indicator = next(i for i in load()["indicators"] if i["id"] == "female_share")
    counts = {"core:sex_female": 4, "core:sex_male": 5}
    result = evaluate(indicator, Aggregate(counts, "exacto", 0))
    assert result.small_n and not result.rank_eligible
    assert result.uncertainty is None
    assert result.value == 100 * 4 / 9
    prior = fit_canton_prior([(4, 9), (30, 100), (8, 14)])
    assert prior is not None
    smoothed = evaluate(
        indicator, Aggregate(counts, "exacto", 0),
        smoothing=True, canton_prior=prior,
    )
    assert smoothed.uncertainty is not None
    assert smoothed.small_n and not smoothed.rank_eligible


def test_dispersed_sector_uses_sector_availability() -> None:
    indicator = next(i for i in load()["indicators"] if i["id"] == "ethnic_diversity_shannon")
    result = evaluate(indicator, Aggregate({}, "exacto", 0), level="sector_disperso")
    assert result.unavailable_reason is None
