"""Add published census-unit counts, weighting only boundary-cut manzanas."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SelectedUnit:
    key: str
    counts: dict[str, float]
    coverage: float = 1.0


@dataclass(frozen=True)
class Aggregate:
    counts: dict[str, float]
    quality: str
    estimated_percent: float


def aggregate(units: list[SelectedUnit]) -> Aggregate:
    """Sum complete units exactly; use area share for units cut by a boundary."""
    values: dict[str, float] = {}
    estimated_population = 0.0
    for unit in units:
        if not 0 <= unit.coverage <= 1:
            raise ValueError(f"Invalid area coverage for {unit.key}")
        for name, count in unit.counts.items():
            if count < 0:
                raise ValueError(f"Negative census count for {unit.key}.{name}")
            values[name] = values.get(name, 0.0) + count * unit.coverage
        if 0 < unit.coverage < 1:
            estimated_population += unit.counts.get("population", 0.0) * unit.coverage
    population = values.get("population", 0.0)
    partial = any(0 < unit.coverage < 1 for unit in units)
    return Aggregate(
        values,
        "estimado" if partial else "exacto",
        100 * estimated_population / population if population > 0 else 0.0,
    )
