"""Generate a tiny exact national comparison silhouette from public aggregates."""

from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "web/public/data/counts/v1b1/nacion/data.parquet"
OUTPUT = ROOT / "web/src/generated/nationalProfile.json"
AGES = [f"{start:02d}_{start + 4:02d}" for start in range(0, 100, 5)] + ["100_120"]


def main() -> None:
    row = pq.read_table(SOURCE).to_pylist()[0]
    profile = {"source": "CPV 2022, INEC", "population": row["population"],
               "male": row["sex_male"], "female": row["sex_female"],
               "age_groups": AGES,
               "male_counts": [row[f"age_{age}_m"] for age in AGES],
               "female_counts": [row[f"age_{age}_f"] for age in AGES]}
    if profile["population"] != 16_938_986:
        raise ValueError("Unexpected national population")
    OUTPUT.write_text(json.dumps(profile, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Wrote exact national profile: {OUTPUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
