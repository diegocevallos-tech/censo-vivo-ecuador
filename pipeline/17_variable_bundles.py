"""Pack exact official-unit category counts into variable-addressable HTTP ranges.

Input is the already public, aggregate-only v1b1 Parquet package. Each province
gets one bundle. Its index points to independently gzipped blocks, so choosing
one census variable never downloads the other variables in that province.
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import numpy as np
import pyarrow.compute as pc
import pyarrow.parquet as pq
from category_counts import HIGH_CARDINALITY

ROOT = Path(__file__).resolve().parents[1]
COUNTS = ROOT / "web/public/data/counts/v1b1"
OUTPUT = ROOT / "web/public/data/variables/v2c"
MAGIC = b"CVEV1"
PROVINCES = tuple(f"{number:02d}" for number in range(1, 25))
AGE_GROUPS = tuple(f"{start:02d}_{start + 4:02d}" for start in range(0, 100, 5)) + (
    "100_120",)


def varint(buffer: bytearray, value: int) -> None:
    if value < 0:
        raise ValueError(f"Negative unsigned value: {value}")
    while value > 127:
        buffer.append((value & 127) | 128)
        value >>= 7
    buffer.append(value)


def compress_rows(
    indices: np.ndarray, categories: np.ndarray, counts: np.ndarray, minimum: int
) -> bytes:
    order = np.lexsort((categories, indices))
    encoded = bytearray()
    previous = 0
    for position in order:
        unit = int(indices[position])
        varint(encoded, unit - previous)
        varint(encoded, int(categories[position]) - minimum)
        varint(encoded, int(counts[position]))
        previous = unit
    return gzip.compress(encoded, compresslevel=6, mtime=0)


def keys_for(level: str, province: str) -> list[list[int | str]]:
    path = COUNTS / level / (f"{province}.parquet" if level != "canton" else "data.parquet")
    table = pq.read_table(path, columns=["unit_index", "unit_key"])
    if level == "canton":
        table = table.filter(pc.starts_with(table["unit_key"], province))
    rows = sorted(zip(table["unit_index"].to_pylist(),
                      table["unit_key"].to_pylist(), strict=True))
    if len({index for index, _ in rows}) != len(rows):
        raise ValueError(f"Duplicate {level} unit index within {province}")
    return [[int(index), str(key)] for index, key in rows]


def category_source(level: str, province: str) -> Path:
    if level == "finest":
        return COUNTS / "categories/finest" / f"{province}.parquet"
    if level == "sector":
        return COUNTS / "categories/sector_only" / f"{province}.parquet"
    return COUNTS / "categories/canton" / f"{province}.parquet"


def grouped_age(province: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    fields = ["unit_index"] + [f"age_{age}_{sex}" for age in AGE_GROUPS
                               for sex in ("m", "f")]
    table = pq.read_table(COUNTS / "finest" / f"{province}.parquet", columns=fields)
    groups = np.column_stack([
        table[f"age_{age}_m"].to_numpy().astype(np.uint32)
        + table[f"age_{age}_f"].to_numpy().astype(np.uint32)
        for age in AGE_GROUPS
    ])
    rows, categories = np.nonzero(groups)
    indices = table["unit_index"].to_numpy()[rows]
    return indices, categories, groups[rows, categories]


def build() -> dict:
    if not (COUNTS / "categories/codebook.parquet").is_file():
        raise FileNotFoundError("Restore the verified public Release first")
    book = pq.read_table(COUNTS / "categories/codebook.parquet",
                         columns=["variable_id", "category_id", "variable"])
    by_id: dict[int, dict] = {}
    for row in book.to_pylist():
        item = by_id.setdefault(row["variable_id"],
                                {"code": row["variable"], "min": row["category_id"]})
        item["min"] = min(item["min"], row["category_id"])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    index: dict = {"format": "CVEV1", "geom_version": "marco-2021",
                   "provinces": {}, "variables": {item["code"]: int(id_)
                                              for id_, item in by_id.items()}}
    index["variables"]["P03"] = -1  # Official five-year age groups, not exact ages.
    results = {}
    for province in PROVINCES:
        target = OUTPUT / f"{province}.bin"
        province_index: dict = {"keys": {}, "blocks": {}}
        with target.open("wb") as stream:
            stream.write(MAGIC)
            for level in ("finest", "sector", "canton"):
                keys = keys_for(level, province)
                raw = json.dumps(keys, separators=(",", ":")).encode("ascii")
                packed = gzip.compress(raw, compresslevel=6, mtime=0)
                offset = stream.tell()
                stream.write(packed)
                province_index["keys"][level] = {"offset": offset, "bytes": len(packed),
                                                 "rows": len(keys)}
            for level in ("finest", "sector", "canton"):
                table = pq.read_table(category_source(level, province),
                                      columns=["unit_index", "variable_id",
                                               "category_id", "n"])
                variable_ids = table["variable_id"].to_numpy()
                indices = table["unit_index"].to_numpy()
                categories = table["category_id"].to_numpy()
                counts = table["n"].to_numpy()
                for variable_id in np.unique(variable_ids):
                    spec = by_id[int(variable_id)]
                    code = spec["code"]
                    if level == "finest" and (code in HIGH_CARDINALITY or code == "P11R"):
                        continue
                    if level == "sector" and code != "P11R":
                        continue
                    if level == "canton" and code not in HIGH_CARDINALITY:
                        continue
                    selected = variable_ids == variable_id
                    packed = compress_rows(indices[selected], categories[selected],
                                           counts[selected], spec["min"])
                    offset = stream.tell()
                    stream.write(packed)
                    province_index["blocks"][code] = {
                        "level": level, "offset": offset, "bytes": len(packed),
                        "rows": int(selected.sum()), "category_min": int(spec["min"]),
                    }
            indices, categories, counts = grouped_age(province)
            packed = compress_rows(indices, categories, counts, 0)
            offset = stream.tell()
            stream.write(packed)
            province_index["blocks"]["P03"] = {
                "level": "finest", "offset": offset, "bytes": len(packed),
                "rows": len(counts), "category_min": 0,
            }
        province_index["bytes"] = target.stat().st_size
        index["provinces"][province] = province_index
        results[province] = {"bytes": target.stat().st_size,
                             "variables": len(province_index["blocks"]),
                             "max_range": max((part["bytes"] for part in
                                               province_index["blocks"].values()), default=0)}
        print(f"{province}: {results[province]}", flush=True)
    (OUTPUT / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8")
    total = sum(value["bytes"] for value in results.values())
    summary = {
        "total_bytes": total,
        "max_range": max(value["max_range"] for value in results.values()),
        "index_bytes": (OUTPUT / "index.json").stat().st_size,
    }
    print(json.dumps(summary))
    return summary


if __name__ == "__main__":
    build()
