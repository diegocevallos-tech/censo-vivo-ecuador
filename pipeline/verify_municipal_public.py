"""Check the small municipal reference package after Release restoration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pyarrow.parquet as pq


def verify(root: Path) -> None:
    folder = root / "municipal-urban/v1"
    boundaries = json.loads((folder / "boundaries.geojson").read_text(encoding="utf-8"))
    summary = json.loads((folder / "summary.json").read_text(encoding="utf-8"))
    counts = pq.read_table(folder / "urban_counts.parquet").to_pandas()
    items = summary["parishes"]
    ids = {item["urban_id"] for item in items}
    shape_ids = {item["properties"]["urban_id"] for item in boundaries["features"]}
    if len(ids) != len(shape_ids) or len(ids) != len(counts):
        raise AssertionError("Municipal package row counts differ")
    if len(ids) != 81 or ids != shape_ids or ids != set(counts["urban_id"]):
        raise AssertionError("Municipal package IDs differ")
    if summary["geom_version"] != "marco-2021":
        raise AssertionError("Unexpected census geometry version")
    if not all(item["urban_id"].startswith("municipal:") for item in items):
        raise AssertionError("Municipal keys are not distinct from census keys")
    by_id = counts.set_index("urban_id")
    for item in items:
        row = by_id.loc[item["urban_id"]]
        for field in ("population", "dwellings", "households"):
            if int(row[field]) != item[field]:
                raise AssertionError(f"Municipal count mismatch: {item['urban_id']} {field}")
    inaquito = next(item for item in items if item["urban_id"] == "municipal:quito:170112")
    if (inaquito["population"], inaquito["age_0_14"], inaquito["age_65_plus"]) != (
        55_879, 6_455, 9_648,
    ):
        raise AssertionError("Iñaquito published numerator/denominator changed")
    if abs(inaquito["aging_index"] - 100 * 9_648 / 6_455) > 1e-8:
        raise AssertionError("Iñaquito ageing index changed")
    print("Municipal Release: 81 reference parishes; counts and Iñaquito verified")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    verify(parser.parse_args().root)
