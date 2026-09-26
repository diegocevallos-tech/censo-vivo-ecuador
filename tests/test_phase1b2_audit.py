"""Regression tests for the fixed census topology and reliable-rate handling."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
spatial = importlib.import_module("05_spatial_stats")


def test_queen_and_island_connection() -> None:
    units = gpd.GeoDataFrame(
        {"unit_key": ["a", "b", "c", "d"]},
        geometry=[box(0, 0, 1, 1), box(1, 0, 2, 1),
                  box(5, 0, 6, 1), box(6, 0, 7, 1)],
        crs="EPSG:32717",
    )
    weights, islands = spatial.queen_with_islands(units)
    assert islands == 0
    assert set(weights.neighbors[0]) == {1}
    assert set(weights.neighbors[2]) == {3}
    units.loc[3, "geometry"] = box(12, 0, 13, 1)
    weights, islands = spatial.queen_with_islands(units)
    assert islands == 2
    assert 3 in weights.neighbors[2] or 2 in weights.neighbors[3]


def test_regularization_preserves_every_polygon() -> None:
    rates = pd.Series([1.0, 99.0, np.nan, 3.0])
    denominators = pd.Series([100, 2, 0, 100])
    prepared = spatial.regularize(rates, denominators)
    assert prepared is not None
    values, replaced = prepared
    assert replaced == 2
    assert len(values) == 4
    assert np.allclose(values, [1, 2, 2, 3])
    assert spatial.PERMUTATIONS == 999
