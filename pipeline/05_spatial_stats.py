"""Sector-based Moran, LISA and educational dissimilarity for every canton."""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import geopandas as gpd
import numpy as np
import pandas as pd
import pyogrio
from counts_schema import AGE_LABELS
from esda.moran import Moran, Moran_Local
from libpysal.weights import Queen, W
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
GPKG = ROOT / "data/raw/GEODATABASE_NACIONAL_2021/GEODATABASE_NACIONAL_2021.gpkg"
DEFAULT_OUTPUT = ROOT / "data/interim/spatial_v1b2"
INDICES = (
    "aging_index", "higher_education_25_plus", "without_fixed_internet",
    "overcrowding", "vacant_private_dwellings", "potential_solitude_65",
)
MIN_CASES = 30
PERMUTATIONS = 999
SEED = 2022


def quote(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def read_sectors(path: Path) -> gpd.GeoDataFrame:
    geometry = pyogrio.read_dataframe(path, layer="sec_a", columns=["sec"])
    if geometry.crs is None or not geometry.crs.is_projected:
        raise ValueError("Sector geometry needs a projected CRS for island distances")
    sector = geometry.rename(columns={"sec": "unit_key"})[
        ["unit_key", "geometry"]
    ].drop_duplicates("unit_key")
    if sector.unit_key.isna().any() or sector.unit_key.duplicated().any():
        raise AssertionError("Sector geometry keys are missing or duplicated")
    return sector


def queen_with_islands(units: gpd.GeoDataFrame) -> tuple[W, int]:
    """One polygon topology per canton; connect only Queen islands to nearest polygon."""
    queen = Queen.from_dataframe(units, use_index=False, silence_warnings=True)
    neighbors = {int(key): list(value) for key, value in queen.neighbors.items()}
    islands = tuple(queen.islands)
    if islands:
        centers = units.geometry.centroid
        points = np.column_stack((centers.x.to_numpy(), centers.y.to_numpy()))
        tree = cKDTree(points)
        for island in islands:
            _, near = tree.query(points[island], k=min(2, len(points)))
            candidates = np.atleast_1d(near)
            neighbor = next((int(value) for value in candidates if value != island), None)
            if neighbor is None:
                raise AssertionError("An island has no other polygon in its canton")
            neighbors[island].append(neighbor)
            neighbors[neighbor].append(island)
    weights = W(neighbors, id_order=list(range(len(units))), silence_warnings=True)
    weights.transform = "R"
    return weights, len(islands)


def regularize(values: pd.Series, denominators: pd.Series) -> tuple[np.ndarray, int] | None:
    """Keep topology fixed; replace unreliable rates with the valid canton mean."""
    rate = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
    n = pd.to_numeric(denominators, errors="coerce").to_numpy(dtype=float)
    reliable = np.isfinite(rate) & np.isfinite(n) & (n >= MIN_CASES)
    if not reliable.any():
        return None
    reference = float(np.average(rate[reliable], weights=n[reliable]))
    rate[~reliable] = reference
    return rate, int((~reliable).sum())


def load_rates(counts: Path, cross: Path, categories: Path) -> pd.DataFrame:
    from importlib import import_module

    # Reuse the same verified sector and category load as the national typology.
    demography = import_module("04_geodemographics")
    frame = demography.load_aggregate(counts, cross, categories)
    def denominator(field: str) -> pd.Series:
        return frame[field].replace(0, np.nan)
    all_0_14 = sum(
        frame[f"age_{label}_{sex}"] for label in AGE_LABELS[:3] for sex in ("m", "f")
    )
    all_65 = sum(
        frame[f"age_{label}_{sex}"] for label in AGE_LABELS[13:] for sex in ("m", "f")
    )
    rates = pd.DataFrame({
        "unit_key": frame.unit_key, "canton_key": frame.canton_key,
        "population": frame.population,
        "low_school_25": frame.school_low_25,
        "high_school_25": frame.school_high_25,
        "overcrowding": frame.overcrowded / denominator("crowding_valid") * 100,
        "vacant_private_dwellings": frame.vacant / denominator("dwellings_valid") * 100,
        "higher_education_25_plus": frame.school_high_25 / denominator("school_n_25") * 100,
        "without_fixed_internet": frame.no_fixed_internet /
            (frame.fixed_internet + frame.no_fixed_internet).replace(0, np.nan) * 100,
        "potential_solitude_65": frame.solitary_65 / denominator("all_65") * 100,
        "aging_index": all_65 / all_0_14.replace(0, np.nan) * 100,
        "n_overcrowding": frame.crowding_valid,
        "n_vacant_private_dwellings": frame.dwellings_valid,
        "n_higher_education_25_plus": frame.school_n_25,
        "n_without_fixed_internet": frame.fixed_internet + frame.no_fixed_internet,
        "n_potential_solitude_65": frame.all_65,
        "n_aging_index": all_0_14,
    })
    return rates


def dissimilarity(part: pd.DataFrame) -> float | None:
    low = float(part.low_school_25.sum())
    high = float(part.high_school_25.sum())
    if low == 0 or high == 0:
        return None
    return float(.5 * np.abs(part.low_school_25 / low - part.high_school_25 / high).sum())


def build(geometry: Path, counts: Path, cross: Path, categories: Path,
          output: Path, permutations: int = PERMUTATIONS) -> dict:
    if not output.resolve().is_relative_to((ROOT / "data/interim").resolve()):
        raise ValueError("Output must remain under ignored data/interim")
    output.mkdir(parents=True, exist_ok=True)
    sectors = read_sectors(geometry)
    rates = load_rates(counts, cross, categories)
    matched = gpd.GeoDataFrame(rates.merge(
        sectors, on="unit_key", how="left", validate="one_to_one"
    ), geometry="geometry", crs=sectors.crs)
    matched_count = int(matched.geometry.notna().sum())
    if matched_count / len(rates) < .95:
        raise AssertionError("Fewer than 95% of sector units match Marco 2021 geometry")
    global_rows = []
    local_rows = []
    dissimilarity_rows = []
    for canton, all_units in matched.groupby("canton_key", sort=True):
        dissimilarity_rows.append({
            "unit_key": canton, "dissimilarity_education": dissimilarity(all_units),
            "sectors": len(all_units), "geom_version": "marco-2021",
        })
        units = all_units.loc[all_units.geometry.notna()].reset_index(drop=True)
        weights, islands = queen_with_islands(units) if len(units) >= 4 else (None, 0)
        for index in INDICES:
            prepared = regularize(units[index], units[f"n_{index}"])
            if len(units) < 4 or prepared is None or np.unique(prepared[0]).size < 2:
                global_rows.append({
                    "unit_key": canton, "indicator": index, "sectors": len(units),
                    "moran_i": None, "permutation_p": None,
                    "regularized_sectors": None if prepared is None else prepared[1],
                    "queen_islands_connected": islands,
                    "geom_version": "marco-2021",
                })
                continue
            values, regularized = prepared
            np.random.seed(SEED)
            global_moran = Moran(values, weights, permutations=permutations)
            local_moran = Moran_Local(
                values, weights, permutations=permutations, seed=SEED, n_jobs=1
            )
            global_rows.append({
                "unit_key": canton, "indicator": index, "sectors": len(units),
                "moran_i": float(global_moran.I),
                "permutation_p": float(global_moran.p_sim),
                "regularized_sectors": regularized,
                "queen_islands_connected": islands,
                "geom_version": "marco-2021",
            })
            quadrant = {1: "alto-alto", 2: "bajo-alto", 3: "bajo-bajo", 4: "alto-bajo"}
            for number, row in units.iterrows():
                p = float(local_moran.p_sim[number])
                local_rows.append({
                    "unit_key": row.unit_key, "canton_key": canton, "indicator": index,
                    "value": float(values[number]), "local_i": float(local_moran.Is[number]),
                    "permutation_p": p,
                    "regularized": bool(units[f"n_{index}"].iloc[number] < MIN_CASES),
                    "cluster": quadrant[int(local_moran.q[number])] if p < .05 else "sin señal",
                    "geom_version": "marco-2021",
                })
        print(f"Spatial statistics: canton {canton}", flush=True)
    db = duckdb.connect()
    outputs = {
        "moran_canton.parquet": pd.DataFrame(global_rows),
        "lisa_sector.parquet": pd.DataFrame(local_rows),
        "dissimilarity_canton.parquet": pd.DataFrame(dissimilarity_rows),
    }
    for name, data in outputs.items():
        db.register("result", data)
        db.execute(f"COPY result TO '{quote(output / name)}' "
                   "(FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)")
        db.unregister("result")
    report = {
        "sector_units": len(rates), "geometry_matches": matched_count,
        "geometry_match_percent": round(100 * matched_count / len(rates), 3),
        "cantons": len(dissimilarity_rows), "indicators": list(INDICES),
        "permutations": permutations, "topology": "Queen with nearest-centroid island links",
        "significant_lisa": int(sum(row["cluster"] != "sin señal" for row in local_rows)),
    }
    if not all(0 <= row["dissimilarity_education"] <= 1 for row in dissimilarity_rows
               if row["dissimilarity_education"] is not None):
        raise AssertionError("Education dissimilarity must lie in [0,1]")
    return report


def main() -> None:
    from importlib import import_module

    demography = import_module("04_geodemographics")
    parser = argparse.ArgumentParser()
    parser.add_argument("--geometry", type=Path, default=GPKG)
    parser.add_argument("--counts", type=Path, default=demography.DEFAULT_COUNTS)
    parser.add_argument("--cross", type=Path, default=demography.DEFAULT_CROSS)
    parser.add_argument("--categories", type=Path, default=demography.DEFAULT_CATEGORIES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--permutations", type=int, default=PERMUTATIONS)
    args = parser.parse_args()
    print(build(args.geometry, args.counts, args.cross, args.categories,
                args.output, args.permutations))


if __name__ == "__main__":
    main()
