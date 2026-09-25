"""Evaluate indicators from additive official-unit counts."""

from __future__ import annotations

import math
from dataclasses import dataclass

from aggregation import Aggregate

LEVELS = ("manzana", "sector", "parroquia", "canton", "provincia", "nacion")


@dataclass(frozen=True)
class CantonPrior:
    mean: float
    strength: float


@dataclass(frozen=True)
class IndicatorResult:
    value: float | None
    denominator: float
    quality: str
    estimated_percent: float
    small_n: bool
    rank_eligible: bool
    uncertainty: dict[str, float] | None
    unavailable_reason: str | None


def count_terms(counts: dict[str, float], keys: list[str]) -> float:
    return sum(counts.get(key, 0.0) for key in keys)


def fit_canton_prior(peers: list[tuple[float, float]]) -> CantonPrior | None:
    """Moment estimate for a beta prior centred on the pooled canton rate."""
    valid = [(success, total) for success, total in peers if total > 0]
    if len(valid) < 2 or any(success < 0 or success > total for success, total in valid):
        return None
    total_success = sum(success for success, _ in valid)
    total_trials = sum(total for _, total in valid)
    mean = total_success / total_trials
    observed = sum((success / total - mean) ** 2 for success, total in valid) / len(valid)
    sampling = sum(mean * (1 - mean) / total for _, total in valid) / len(valid)
    between = max(0.0, observed - sampling)
    strength = (
        min(1_000_000.0, max(0.0, mean * (1 - mean) / between - 1))
        if between > 0 else 1_000_000.0
    )
    return CantonPrior(mean, strength)


def empirical_bayes(
    numerator: float, denominator: float, prior: CantonPrior, factor: float
) -> tuple[float, dict[str, float]]:
    if denominator <= 0 or not 0 <= numerator <= denominator:
        raise ValueError("Empirical Bayes requires a valid binomial rate")
    alpha = numerator + prior.mean * prior.strength
    beta = denominator - numerator + (1 - prior.mean) * prior.strength
    mean = alpha / (alpha + beta)
    variance = alpha * beta / ((alpha + beta) ** 2 * (alpha + beta + 1))
    sd = math.sqrt(variance)
    uncertainty = {
        "lower": factor * max(0.0, mean - 1.96 * sd),
        "upper": factor * min(1.0, mean + 1.96 * sd),
        "sd": factor * sd,
        "prior_strength": prior.strength,
    }
    return factor * mean, uncertainty


def evaluate(
    definition: dict,
    aggregate: Aggregate,
    *,
    level: str = "manzana",
    smoothing: bool = False,
    canton_prior: CantonPrior | None = None,
) -> IndicatorResult:
    if level not in LEVELS or definition["min_level"] not in LEVELS:
        raise ValueError("Unknown census level")
    if LEVELS.index(level) < LEVELS.index(definition["min_level"]):
        return IndicatorResult(
            None, 0.0, aggregate.quality, aggregate.estimated_percent,
            False, False, None,
            f"Disponible desde {definition['min_level']}",
        )
    counts = aggregate.counts
    kind = definition["kind"]
    numerator = 0.0
    if kind == "ratio":
        numerator = count_terms(counts, definition["numerator"])
        denominator = count_terms(counts, definition["denominator"])
        value = numerator / denominator * definition.get("factor", 1) if denominator else None
    elif kind in {"shannon", "median_grouped"}:
        groups = definition["categories" if kind == "shannon" else "age_groups"]
        values = [count_terms(counts, group) for group in groups]
        denominator = sum(values)
        if not denominator:
            value = None
        elif kind == "shannon":
            value = -sum(
                probability * math.log(probability)
                for count in values if (probability := count / denominator) > 0
            ) / math.log(len(values))
        else:
            middle = denominator / 2
            running = 0.0
            value = None
            for index, count in enumerate(values):
                if count and running + count >= middle:
                    lower = index * 5
                    width = 21 if index == 20 else 5
                    value = lower + width * (middle - running) / count
                    break
                running += count
    elif kind == "weighted_mean":
        stem = f"cat:{definition['source_table']}:{definition['source_variable']}:"
        weighted = [
            (category, counts.get(stem + str(category), 0.0))
            for category in range(definition["valid_min"], definition["valid_max"] + 1)
        ]
        denominator = sum(count for _, count in weighted)
        value = (
            sum(category * count for category, count in weighted) / denominator
            if denominator else None
        )
    else:
        raise ValueError(f"Unsupported indicator kind: {kind}")
    uncertainty = None
    if (
        smoothing and definition.get("bayesian") and canton_prior
        and denominator > 0 and kind == "ratio"
    ):
        value, uncertainty = empirical_bayes(
            numerator, denominator, canton_prior, definition.get("factor", 1)
        )
    small_n = denominator < definition["min_n"]
    return IndicatorResult(
        value, denominator, aggregate.quality, aggregate.estimated_percent,
        small_n, not small_n and aggregate.quality == "exacto", uncertainty, None,
    )
