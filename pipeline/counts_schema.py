"""Shared, additive output schema for Phase 1A geographic counts."""

GEOM_VERSION = "marco-2021"
AGE_LABELS = [f"{n:02d}_{n + 4:02d}" for n in range(0, 100, 5)] + ["100_120"]
AGE_SEX_FIELDS = [f"age_{label}_{sex}" for label in AGE_LABELS for sex in ("m", "f")]
NUMERIC_FIELDS = [
    "population",
    "dwellings",
    "households",
    "emigrants",
    "deaths",
    "assigned_population",
    "assigned_dwellings",
    "assigned_households",
    "assigned_emigrants",
    "assigned_deaths",
    "assigned_manzanas",
    "rural_population",
    "masked_population",
    "sex_male",
    "sex_female",
    "sex_unknown",
    "age_sex_unknown",
    *AGE_SEX_FIELDS,
]
