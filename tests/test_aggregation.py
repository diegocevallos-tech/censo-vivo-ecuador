"""Shared aggregation cases for exact and boundary-weighted selections."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
from aggregation import SelectedUnit, aggregate  # noqa: E402


def test_shared_cases() -> None:
    cases = json.loads((ROOT / "tests/aggregation_cases.json").read_text())
    for case in cases:
        result = aggregate([SelectedUnit(**unit) for unit in case["units"]])
        for field, expected in case["counts"].items():
            assert abs(result.counts[field] - expected) < 1e-9
        assert result.quality == case["quality"]
        assert abs(result.estimated_percent - case["estimated_percent"]) < 1e-9
