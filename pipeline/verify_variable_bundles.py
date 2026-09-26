"""Verify ten seeded INEC variables at official-unit, parish and national levels."""

from __future__ import annotations

import argparse
import gzip
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "web/public/meta/variables.json"
PROVINCES = tuple(f"{number:02d}" for number in range(1, 25))


def read_varint(data: bytes, position: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while True:
        if position >= len(data) or shift > 49:
            raise ValueError("Malformed variable block")
        byte = data[position]
        position += 1
        value |= (byte & 127) << shift
        if byte < 128:
            return value, position
        shift += 7


def part(stream, entry: dict) -> bytes:
    stream.seek(entry["offset"])
    packed = stream.read(entry["bytes"])
    if len(packed) != entry["bytes"]:
        raise ValueError("Truncated variable range")
    return gzip.decompress(packed)


def decode(stream, province: dict, code: str) -> dict[tuple[str, int], int]:
    block = province["blocks"][code]
    keys = {int(index): key for index, key in json.loads(
        part(stream, province["keys"][block["level"]]))}
    data = part(stream, block)
    values = Counter()
    position = 0
    unit_index = 0
    rows = 0
    while position < len(data):
        delta, position = read_varint(data, position)
        local_category, position = read_varint(data, position)
        count, position = read_varint(data, position)
        unit_index += delta
        key = keys.get(unit_index)
        if key is None:
            raise AssertionError(f"Unknown {province=} {unit_index=}")
        values[(key, block["category_min"] + local_category)] += count
        rows += 1
    if rows != block["rows"]:
        raise AssertionError(f"Variable block row mismatch: {code}")
    return dict(values)


def expected_categories(path: Path, variable_id: int) -> dict[tuple[int, int], int]:
    table = pq.read_table(path, columns=["unit_index", "variable_id", "category_id", "n"])
    table = table.filter(pc.equal(table["variable_id"], variable_id))
    return {(int(row["unit_index"]), int(row["category_id"])): int(row["n"])
            for row in table.to_pylist()}


def chosen_variables() -> list[str]:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["variables"]
    by_table: dict[str, list[str]] = defaultdict(list)
    for item in catalog:
        if item["available"] and item["id"] != "P03" and item["categories"]:
            by_table[item["table"]].append(item["id"])
    randomizer = random.Random(2022)
    return [code for table in sorted(by_table)
            for code in randomizer.sample(sorted(by_table[table]), 2)]


def check_manzana_and_sector(root: Path, province: str, chosen: list[str],
                             decoded: dict[str, dict], index: dict) -> None:
    core = pq.read_table(root / "finest" / f"{province}.parquet",
                         columns=["unit_index", "unit_key"])
    keys = dict(zip(core["unit_index"].to_pylist(), core["unit_key"].to_pylist(), strict=True))
    fine = pq.read_table(root / "categories/finest" / f"{province}.parquet",
                         columns=["unit_index", "variable_id", "category_id", "n"])
    wanted = {index["variables"][code]: code for code in chosen}
    expected = {code: {} for code in chosen}
    for row in fine.to_pylist():
        code = wanted.get(row["variable_id"])
        if code:
            expected[code][(keys[row["unit_index"]], row["category_id"])] = row["n"]
    for code in chosen:
        if decoded[code] != expected[code]:
            raise AssertionError(f"Manzana category mismatch: {province}/{code}")
    codebook = pq.read_table(root / "categories/codebook.parquet").to_pylist()
    ids = {(row["source_table"], row["variable"], row["category"]):
           row["category_id"] for row in codebook}
    source = ROOT / "data/interim/full_aggregate_v1a/counts/v1a/categories/sector"
    paths = sorted((source / f"province_key={province}").glob("*.parquet"))
    if not paths:
        raise FileNotFoundError("Local exact sector categories unavailable")
    sector = Counter()
    for path in paths:
        table = pq.read_table(path, columns=["sector_key", "source_table", "variable",
                                             "category", "n"])
        table = table.filter(pc.is_in(table["variable"], value_set=pa.array(chosen)))
        for row in table.to_pylist():
            category_id = ids[(row["source_table"], row["variable"], row["category"])]
            sector[(row["variable"], row["sector_key"], category_id)] += row["n"]
    observed = Counter()
    for code in chosen:
        for (key, category), count in decoded[code].items():
            observed[(code, key[:12], category)] += count
    if sector != observed:
        raise AssertionError(f"Sector category mismatch: {province}")


def verify(root: Path, with_interim: bool = False) -> dict:
    root = root / "counts/v1b1" if (root / "counts/v1b1").is_dir() else root
    bundle_dir = root.parents[1] / "variables/v2c"
    if not bundle_dir.is_dir():
        raise FileNotFoundError(bundle_dir)
    index = json.loads((bundle_dir / "index.json").read_text(encoding="utf-8"))
    if index["format"] != "CVEV1" or index["geom_version"] != "marco-2021":
        raise ValueError("Unknown variable index")
    chosen = chosen_variables()
    if len(chosen) != 10:
        raise AssertionError("Expected ten seeded variables")
    controls = ["P11R", "P08P", "P03"]
    checked = list(dict.fromkeys(chosen + controls))
    national: dict[str, Counter[int]] = {code: Counter() for code in checked}
    parishes_checked = 0
    block_units_checked = 0
    for province in PROVINCES:
        spec = index["provinces"][province]
        path = bundle_dir / f"{province}.bin"
        if path.stat().st_size != spec["bytes"]:
            raise AssertionError(f"Bundle length changed: {province}")
        with path.open("rb") as stream:
            if stream.read(5) != b"CVEV1":
                raise ValueError(f"Invalid province variable bundle: {province}")
            decoded = {}
            for code in checked:
                cells = decode(stream, spec, code)
                decoded[code] = cells
                block_units_checked += len({key for key, _ in cells})
                for (_, category), count in cells.items():
                    national[code][category] += count
                variable_id = index["variables"][code]
                level = spec["blocks"][code]["level"]
                if code == "P03":
                    continue  # The official category table excludes exact age.
                if level == "canton":
                    core = pq.read_table(root / "canton/data.parquet",
                                         columns=["unit_index", "unit_key"])
                    core = core.filter(pc.starts_with(core["unit_key"], province))
                    keys = dict(zip(core["unit_key"].to_pylist(),
                                    core["unit_index"].to_pylist(), strict=True))
                    observed = {(keys[key], category): count
                                for (key, category), count in cells.items()}
                    expected = expected_categories(
                        root / "categories/canton" / f"{province}.parquet", variable_id)
                    if observed != expected:
                        raise AssertionError(f"Canton variable mismatch: {province}/{code}")
                else:
                    core = pq.read_table(root / "parroquia/data.parquet",
                                         columns=["unit_index", "unit_key"])
                    core = core.filter(pc.starts_with(core["unit_key"], province))
                    keys = dict(zip(core["unit_key"].to_pylist(),
                                    core["unit_index"].to_pylist(), strict=True))
                    parish = Counter()
                    for (key, category), count in cells.items():
                        parish[(keys[key[:6]], category)] += count
                    expected = expected_categories(
                        root / "categories/parroquia" / f"{province}.parquet", variable_id)
                    if dict(parish) != expected:
                        raise AssertionError(f"Parish roll-up mismatch: {province}/{code}")
                    parishes_checked += len({key for key, _ in parish})
            if with_interim:
                check_manzana_and_sector(root, province, chosen, decoded, index)
    table = pq.read_table(root / "categories/nacion/data.parquet",
                          columns=["variable_id", "category_id", "n"])
    official = defaultdict(Counter)
    for row in table.to_pylist():
        official[row["variable_id"]][row["category_id"]] += row["n"]
    for code in checked:
        if code == "P03":
            ages = [f"age_{start:02d}_{start + 4:02d}" for start in range(0, 100, 5)]
            ages.append("age_100_120")
            source = pq.read_table(root / "nacion/data.parquet")
            nation = source.to_pylist()[0]
            for category, age in enumerate(ages):
                expected = nation[f"{age}_m"] + nation[f"{age}_f"]
                if national[code][category] != expected:
                    raise AssertionError(f"National age group differs: {age}")
            continue
        if national[code] != official[index["variables"][code]]:
            raise AssertionError(f"National category totals differ: {code}")
    result = {"seed": 2022, "variables": chosen, "controls": controls, "provinces": 24,
              "official_units": block_units_checked, "parish_units": parishes_checked,
              "national_difference": 0, "manzana_sector_checked": with_interim}
    print(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT / "web/public/data")
    parser.add_argument("--with-interim", action="store_true")
    args = parser.parse_args()
    verify(args.root, with_interim=args.with_interim)
