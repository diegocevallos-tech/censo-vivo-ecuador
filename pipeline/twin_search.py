"""Nearest official-area profiles, with explicit geographic exclusion."""

from __future__ import annotations

from pathlib import Path

import duckdb
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data/interim/geodemographics_v1b2"


def nearest(unit_key: str, level: str, output: Path = DEFAULT_OUTPUT,
            count: int = 10, exclude_canton: bool = False) -> list[dict]:
    if level not in {"sector", "parroquia", "canton"}:
        raise ValueError(level)
    file = output / ("twin_profiles.parquet" if level == "sector"
                     else f"twin_profiles_{level}.parquet")
    frame = duckdb.read_parquet(str(file)).df()
    feature_columns = [column for column in frame if column.startswith("z_")]
    selected = frame.loc[frame.unit_key == unit_key]
    if len(selected) != 1:
        raise ValueError(f"Unknown {level}: {unit_key}")
    reference = selected[feature_columns].to_numpy(dtype=float)[0]
    eligible = frame.loc[frame.rank_eligible & (frame.unit_key != unit_key)].copy()
    if exclude_canton:
        eligible = eligible.loc[eligible.unit_key.str[:4] != unit_key[:4]]
    vectors = eligible[feature_columns].to_numpy(dtype=float)
    norm = np.linalg.norm(reference) * np.linalg.norm(vectors, axis=1)
    similarity = np.divide(vectors @ reference, norm, out=np.zeros(len(vectors)),
                           where=norm > 0)
    eligible["cosine_similarity"] = similarity
    return eligible.nlargest(count, "cosine_similarity")[
        ["unit_key", "cosine_similarity"]
    ].to_dict("records")
