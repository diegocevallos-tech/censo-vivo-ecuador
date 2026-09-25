"""Sector-based Moran, LISA and educational dissimilarity for every canton."""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import pyogrio
from counts_schema import AGE_LABELS
from esda.moran import Moran, Moran_Local
from libpysal.weights import KNN

ROOT = Path(__file__).resolve().parents[1]
GPKG = ROOT / "data/raw/GEODATABASE_NACIONAL_2021/GEODATABASE_NACIONAL_2021.gpkg"
DEFAULT_OUTPUT = ROOT / "data/interim/spatial_v1b2"
INDICES = (
    "overcrowding", "vacancy", "female_headship", "illiteracy_15_plus",
    "internet_use_5_plus", "aging_index",
)
MIN_CASES = 30
PERMUTATIONS = 99
SEED = 2022


def quote(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def read_sectors(path: Path) -> pd.DataFrame:
    geometry = pyogrio.read_dataframe(path, layer="sec_a", columns=["sec"])
    if geometry.crs is None or not geometry.crs.is_projected:
        raise ValueError("Sector geometry needs a projected CRS for kNN distances")
    centroids = geometry.geometry.centroid
    sector = pd.DataFrame({
        "unit_key": geometry["sec"], "x": centroids.x, "y": centroids.y,
    }).drop_duplicates("unit_key")
    if sector.unit_key.isna().any() or sector.unit_key.duplicated().any():
        raise AssertionError("Sector geometry keys are missing or duplicated")
    return sector


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
        "vacancy": frame.vacant / denominator("dwellings_valid") * 100,
        "female_headship": frame.female_heads / denominator("all_heads") * 100,
        "illiteracy_15_plus": frame.illiterate_15 / denominator("literacy_response_15") * 100,
        "internet_use_5_plus": frame.internet_person_5 / denominator("internet_response_5") * 100,
        "aging_index": all_65 / all_0_14.replace(0, np.nan) * 100,
        "n_overcrowding": frame.crowding_valid,
        "n_vacancy": frame.dwellings_valid,
        "n_female_headship": frame.all_heads,
        "n_illiteracy_15_plus": frame.literacy_response_15,
        "n_internet_use_5_plus": frame.internet_response_5,
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
    matched = rates.merge(sectors, on="unit_key", how="left", validate="one_to_one")
    matched_count = int(matched.x.notna().sum())
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
        for index in INDICES:
            units = all_units.loc[
                all_units.x.notna() & all_units[index].notna()
                & (all_units[f"n_{index}"] >= MIN_CASES)
            ].reset_index(drop=True)
            if len(units) < 4 or units[index].nunique() < 2:
                global_rows.append({
                    "unit_key": canton, "indicator": index, "sectors": len(units),
                    "moran_i": None, "permutation_p": None,
                    "geom_version": "marco-2021",
                })
                continue
            k = min(8, len(units) - 1)
            points = units[["x", "y"]].to_numpy()
            weights = KNN.from_array(points, k=k)
            weights.transform = "R"
            values = units[index].to_numpy(dtype=float)
            np.random.seed(SEED)
            global_moran = Moran(values, weights, permutations=permutations)
            local_moran = Moran_Local(
                values, weights, permutations=permutations, seed=SEED, n_jobs=1
            )
            global_rows.append({
                "unit_key": canton, "indicator": index, "sectors": len(units),
                "moran_i": float(global_moran.I),
                "permutation_p": float(global_moran.p_sim),
                "geom_version": "marco-2021",
            })
            quadrant = {1: "alto-alto", 2: "bajo-alto", 3: "bajo-bajo", 4: "alto-bajo"}
            for number, row in units.iterrows():
                p = float(local_moran.p_sim[number])
                local_rows.append({
                    "unit_key": row.unit_key, "canton_key": canton, "indicator": index,
                    "value": float(values[number]), "local_i": float(local_moran.Is[number]),
                    "permutation_p": p,
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
        "permutations": permutations,
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
