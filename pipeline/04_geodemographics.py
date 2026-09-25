"""Deterministic national sector typology, portraits, SoVI weights and twin vectors."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from counts_schema import AGE_LABELS
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COUNTS = ROOT / "data/interim/exact_public/counts/v1b1"
DEFAULT_CROSS = ROOT / "data/interim/cross_counts_v1b2"
DEFAULT_CATEGORIES = ROOT / "data/interim/full_aggregate_v1a/counts/v1a/categories/sector"
DEFAULT_OUTPUT = ROOT / "data/interim/geodemographics_v1b2"
SEED = 2022
FEATURE_NAMES = [f"age_{label}_share" for label in AGE_LABELS] + [
    "female_share", "household_size", "vacant_share", "owned_share", "rented_share",
    "single_household_share", "overcrowded_share", "female_head_share", "solitude_65_share",
    "schooling_25_mean", "low_school_share", "high_school_share", "internet_5_share",
    "digital_gender_gap", "female_employment_share", "adolescent_mother_share",
    "indigenous_language_share", "illiteracy_15_share", "recent_intercanton_share",
]
LABELS = {
    "age_00_04_share": "Infancias", "age_65_69_share": "Mayores",
    "female_share": "Presencia femenina", "household_size": "Hogares numerosos",
    "vacant_share": "Viviendas vacías", "owned_share": "Vivienda propia",
    "rented_share": "Vivienda arrendada", "single_household_share": "Hogares solos",
    "overcrowded_share": "Hacinamiento", "female_head_share": "Jefatura femenina",
    "solitude_65_share": "Mayores solos", "schooling_25_mean": "Alta escolaridad",
    "low_school_share": "Baja escolaridad", "high_school_share": "Estudios superiores",
    "internet_5_share": "Vida conectada", "digital_gender_gap": "Brecha digital",
    "female_employment_share": "Trabajo femenino", "adolescent_mother_share": "Maternidad joven",
    "indigenous_language_share": "Lenguas originarias", "illiteracy_15_share": "Rezago educativo",
    "recent_intercanton_share": "Movilidad reciente",
}
SOVI_FEATURES = [
    "low_school_share", "illiteracy_15_share", "overcrowded_share",
    "solitude_65_share", "adolescent_mother_share", "digital_gender_gap",
]


def quote(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator.div(denominator.replace(0, np.nan))


def portrait_terms(means: np.ndarray) -> list[str]:
    candidates = [(LABELS[name], float(means[index])) for index, name in enumerate(
        FEATURE_NAMES
    ) if not name.startswith("age_")]
    candidates.extend([
        ("Infancias", float(np.mean(means[:3]))),
        ("Juventud", float(np.mean(means[3:6]))),
        ("Edad adulta", float(np.mean(means[6:13]))),
        ("Envejecimiento", float(np.mean(means[13:21]))),
    ])
    return [label for label, _ in sorted(candidates, key=lambda item: -item[1])]


def load_aggregate(counts: Path, cross: Path, categories: Path) -> pd.DataFrame:
    db = duckdb.connect()
    core = quote(counts / "sector/*.parquet")
    cross_path = quote(cross / "sector/data.parquet")
    category_path = quote(categories / "**/*.parquet")
    selected = {
        "vacant": ("vivienda", "V0201", ["4"]),
        "dwellings_valid": ("vivienda", "V0201", [str(i) for i in range(1, 6)]),
        "owned": ("hogar", "H09", ["1", "2", "3"]),
        "rented": ("hogar", "H09", ["4"]),
        "tenure_valid": ("hogar", "H09", [str(i) for i in range(1, 7)]),
        "single": ("hogar", "TIPO_HOGAR", ["1"]),
        "household_type_valid": ("hogar", "TIPO_HOGAR", [str(i) for i in range(1, 6)]),
        "overcrowded": ("hogar", "HAC", ["1"]),
        "crowding_valid": ("hogar", "HAC", ["1", "2"]),
    }
    expressions = []
    for field, (table, variable, codes) in selected.items():
        quoted = ",".join(f"'{code}'" for code in codes)
        expressions.append(
            f"SUM(n) FILTER (WHERE source_table='{table}' AND variable='{variable}' "
            f"AND category IN ({quoted})) AS {field}"
        )
    query = f"""
    WITH categories AS (
      SELECT unit_key,{','.join(expressions)}
      FROM read_parquet('{category_path}')
      WHERE (source_table='vivienda' AND variable='V0201')
        OR (source_table='hogar' AND variable IN ('H09','TIPO_HOGAR','HAC'))
      GROUP BY unit_key
    )
    SELECT c.*, x.* EXCLUDE(unit_key,geom_version),
      {','.join('COALESCE(k.'+field+',0) AS '+field for field in selected)}
    FROM read_parquet('{core}') c
    JOIN read_parquet('{cross_path}') x USING(unit_key)
    LEFT JOIN categories k USING(unit_key)
    ORDER BY c.unit_key
    """
    frame = db.execute(query).df()
    if len(frame) != 53_513 or int(frame.population.sum()) != 16_938_986:
        raise AssertionError("Sector typology input differs from official census totals")
    return frame


def feature_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    age = sum(frame[f"age_{label}_{sex}"] for label in AGE_LABELS for sex in ("m", "f"))
    features = {
        f"age_{label}_share": safe_ratio(
            frame[f"age_{label}_m"] + frame[f"age_{label}_f"], age
        ) for label in AGE_LABELS
    }
    features.update({
        "female_share": safe_ratio(frame.sex_female, frame.sex_male + frame.sex_female),
        "household_size": safe_ratio(frame.population, frame.households),
        "vacant_share": safe_ratio(frame.vacant, frame.dwellings_valid),
        "owned_share": safe_ratio(frame.owned, frame.tenure_valid),
        "rented_share": safe_ratio(frame.rented, frame.tenure_valid),
        "single_household_share": safe_ratio(frame.single, frame.household_type_valid),
        "overcrowded_share": safe_ratio(frame.overcrowded, frame.crowding_valid),
        "female_head_share": safe_ratio(frame.female_heads, frame.all_heads),
        "solitude_65_share": safe_ratio(frame.solitary_65, frame.all_65),
        "schooling_25_mean": safe_ratio(frame.school_years_25, frame.school_n_25),
        "low_school_share": safe_ratio(frame.school_low_25, frame.school_n_25),
        "high_school_share": safe_ratio(frame.school_high_25, frame.school_n_25),
        "internet_5_share": safe_ratio(frame.internet_person_5, frame.internet_response_5),
        "digital_gender_gap": (
            safe_ratio(frame.digital_male_score, frame.digital_male_max)
            - safe_ratio(frame.digital_female_score, frame.digital_female_max)
        ),
        "female_employment_share": safe_ratio(
            frame.labour_female_employed, frame.labour_female_force
        ),
        "adolescent_mother_share": safe_ratio(
            frame.adolescent_mothers, frame.adolescent_women
        ),
        "indigenous_language_share": safe_ratio(
            frame.indigenous_language, frame.language_eligible
        ),
        "illiteracy_15_share": safe_ratio(
            frame.illiterate_15, frame.literacy_response_15
        ),
        "recent_intercanton_share": safe_ratio(
            frame.residence_other_canton_5, frame.population
        ),
    })
    result = pd.DataFrame(features)
    if result.columns.tolist() != FEATURE_NAMES or len(FEATURE_NAMES) != 40:
        raise AssertionError("Expected exactly 40 documented input features")
    return result.replace([np.inf, -np.inf], np.nan)


def select_k(sample: np.ndarray) -> tuple[int, list[dict]]:
    rng = np.random.default_rng(SEED)
    candidates = (4, 6, 8, 10)
    lower, upper = np.min(sample, axis=0), np.max(sample, axis=0)
    rows = []
    for k in candidates:
        model = KMeans(n_clusters=k, random_state=SEED, n_init=3).fit(sample)
        silhouette = silhouette_score(sample, model.labels_, sample_size=1200,
                                      random_state=SEED)
        reference = []
        for _ in range(3):
            random_points = rng.uniform(lower, upper, size=sample.shape)
            reference.append(np.log(KMeans(
                n_clusters=k, random_state=SEED, n_init=1
            ).fit(random_points).inertia_))
        rows.append({"k": k, "silhouette": round(float(silhouette), 5),
                     "gap": round(float(np.mean(reference) - np.log(model.inertia_)), 5),
                     "gap_sd": round(float(np.std(reference, ddof=1)), 5)})
    # Gap grows across tested k, without a stable elbow. Keep models within
    # 0.1 log-dispersion of the best gap, then prefer silhouette and smaller k.
    best_gap = max(row["gap"] for row in rows)
    eligible = [row for row in rows if row["gap"] >= best_gap - .1]
    chosen = max(eligible, key=lambda row: (row["silhouette"], -row["k"]))
    return chosen["k"], rows


def build(counts: Path, cross: Path, categories: Path, output: Path) -> dict:
    if not output.resolve().is_relative_to((ROOT / "data/interim").resolve()):
        raise ValueError("Output must remain under ignored data/interim")
    output.mkdir(parents=True, exist_ok=True)
    raw = load_aggregate(counts, cross, categories)
    features = feature_matrix(raw)
    reliable = (raw.population >= 100).to_numpy()
    training = features.loc[reliable]
    medians = training.median()
    filled = features.fillna(medians).fillna(0)
    lower, upper = training.quantile(.01), training.quantile(.99)
    clipped = filled.clip(lower=lower, upper=upper, axis=1)
    scaler = StandardScaler().fit(clipped.loc[reliable])
    vectors = scaler.transform(clipped).astype(np.float32)
    rng = np.random.default_rng(SEED)
    sample_ids = rng.choice(np.flatnonzero(reliable),
                            size=min(2400, int(reliable.sum())), replace=False)
    selected_k, diagnostics = select_k(vectors[sample_ids])
    super_model = KMeans(n_clusters=selected_k, random_state=SEED, n_init=5).fit(
        vectors[reliable]
    )
    super_labels = super_model.predict(vectors)
    group_labels = np.zeros(len(raw), dtype=np.uint8)
    for supergroup in range(selected_k):
        train = vectors[reliable & (super_labels == supergroup)]
        model = KMeans(n_clusters=2, random_state=SEED + supergroup, n_init=5).fit(train)
        mask = super_labels == supergroup
        group_labels[mask] = supergroup * 2 + model.predict(vectors[mask])
    portraits = []
    for group in sorted(np.unique(group_labels)):
        mask = group_labels == group
        weights = raw.loc[mask, "population"].to_numpy()
        means = np.average(vectors[mask], axis=0, weights=weights)
        terms = portrait_terms(means)
        name = f"{terms[0]} · {terms[1]}"
        for extra in terms[2:]:
            if not any(existing["name_es"] == name for existing in portraits):
                break
            name += f" · {extra}"
        portraits.append({
            "id": int(group), "supergroup": int(group // 2),
            "name_es": name,
            "description_es": (
                "Perfil relativo con " + terms[0].lower() + " y "
                + terms[1].lower() + " por encima de la referencia nacional."
            ),
            "sectors": int(mask.sum()), "population": int(weights.sum()),
            "radar_z_vs_nation": {
                name: round(float(value), 3) for name, value in zip(
                    FEATURE_NAMES, means, strict=True
                )
            },
        })
    sovi_input = vectors[reliable][:, [FEATURE_NAMES.index(x) for x in SOVI_FEATURES]]
    pca = PCA(n_components=1, random_state=SEED).fit(sovi_input)
    loadings = pca.components_[0].copy()
    if np.sum(loadings) < 0:
        loadings *= -1
    svi = vectors[:, [FEATURE_NAMES.index(x) for x in SOVI_FEATURES]] @ loadings
    sovi_valid = features[SOVI_FEATURES].notna().all(axis=1).to_numpy()
    svi[~sovi_valid] = np.nan
    twin_eligible = reliable & sovi_valid
    assignment = pd.DataFrame({
        "unit_key": raw.unit_key, "geom_version": "marco-2021",
        "supergroup": super_labels.astype(np.uint8), "group": group_labels,
        "population": raw.population.astype(np.uint32),
        "rank_eligible": twin_eligible, "sovi_pca": svi.astype(np.float32),
    })
    profile = pd.DataFrame(vectors, columns=[f"z_{name}" for name in FEATURE_NAMES])
    profile.insert(0, "unit_key", raw.unit_key)
    profile.insert(1, "geom_version", "marco-2021")
    profile.insert(2, "rank_eligible", twin_eligible)
    db = duckdb.connect()
    for file, data in (("sector_clusters.parquet", assignment),
                       ("twin_profiles.parquet", profile)):
        db.register("prepared", data)
        db.execute(f"COPY prepared TO '{quote(output / file)}' "
                   "(FORMAT PARQUET, COMPRESSION ZSTD, COMPRESSION_LEVEL 12)")
        db.unregister("prepared")
    result = {
        "geom_version": "marco-2021", "seed": SEED,
        "unit_level": "sector", "n_sectors": len(raw),
        "fit_min_population": 100, "eligible_sectors": int(reliable.sum()),
        "twin_eligible_sectors": int(twin_eligible.sum()),
        "features": FEATURE_NAMES,
        "feature_mean": dict(zip(FEATURE_NAMES, map(float, scaler.mean_), strict=True)),
        "feature_scale": dict(zip(FEATURE_NAMES, map(float, scaler.scale_), strict=True)),
        "feature_clipping": {
            "p01": dict(zip(FEATURE_NAMES, map(float, lower), strict=True)),
            "p99": dict(zip(FEATURE_NAMES, map(float, upper), strict=True)),
        },
        "k_diagnostics": diagnostics, "selected_supergroups": selected_k,
        "subgroups_per_supergroup": 2, "clusters": portraits,
        "sovi_pca": {
            "features": SOVI_FEATURES,
            "loadings": dict(zip(SOVI_FEATURES, map(float, loadings), strict=True)),
            "explained_variance_ratio": float(pca.explained_variance_ratio_[0]),
            "orientation": "positive correlation with unweighted vulnerability feature mean",
        },
    }
    (output / "clusters.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--counts", type=Path, default=DEFAULT_COUNTS)
    parser.add_argument("--cross", type=Path, default=DEFAULT_CROSS)
    parser.add_argument("--categories", type=Path, default=DEFAULT_CATEGORIES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = build(args.counts, args.cross, args.categories, args.output)
    print(f"{result['n_sectors']} sectors; {result['selected_supergroups']} supergroups")


if __name__ == "__main__":
    main()
