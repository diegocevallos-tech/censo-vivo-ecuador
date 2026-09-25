"""Check every binary province chunk against published Parquet geography and counts."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "web/public/data"
DTYPES = {"uint8": "<u1", "uint16": "<u2", "uint32": "<u4", "uint64": "<u8"}


def check(root: Path) -> None:
    chunk_root = root / "chunks/v1b"
    schema = json.loads((chunk_root / "schema.json").read_text(encoding="utf-8"))
    sector_cross = pq.read_table(root / "cross/v1b2/sector/data.parquet",
                                 columns=["unit_key", "female_heads"]).to_pandas()
    checked = 0
    for relative, metadata in schema["chunks"].items():
        path = chunk_root / relative
        raw = path.read_bytes()
        if raw[:5] != b"CVEB1":
            raise AssertionError(f"Invalid chunk header: {relative}")
        rows = struct.unpack_from("<I", raw, 5)[0]
        if rows != metadata["rows"]:
            raise AssertionError(f"Row count mismatch: {relative}")
        keys = [raw[9 + index * 15:9 + (index + 1) * 15].rstrip(b"\0").decode("ascii")
                for index in range(rows)]
        level, filename = relative.split("/")
        province = filename[:2]
        core = pq.read_table(root / "counts/v1b1" / level / f"{province}.parquet",
                             columns=["unit_key", "population"]).to_pandas()
        if keys != core.unit_key.to_list():
            raise AssertionError(f"Geography order mismatch: {relative}")
        cross = (pq.read_table(root / "cross/v1b2" / level / f"{province}.parquet",
                               columns=["unit_key", "female_heads"]).to_pandas()
                 if level == "finest" else
                 sector_cross[sector_cross.unit_key.str.startswith(province)])
        cross_values = cross.set_index("unit_key").loc[keys].female_heads.to_numpy()
        for name, expected in (("population", core.population.to_numpy()),
                               ("female_heads", cross_values)):
            column = next((c for c in metadata["columns"] if c["name"] == name), None)
            if column is None:
                raise AssertionError(f"Missing {name}: {relative}")
            values = np.frombuffer(raw, dtype=DTYPES[column["type"]], count=rows,
                                   offset=column["offset"])
            if not np.array_equal(values, expected):
                raise AssertionError(f"Value mismatch: {relative}/{name}")
        last = metadata["columns"][-1]
        expected_size = last["offset"] + rows * np.dtype(DTYPES[last["type"]]).itemsize
        if len(raw) != expected_size:
            raise AssertionError(f"Trailing or truncated bytes: {relative}")
        checked += rows
    print(f"Validated {len(schema['chunks'])} binary chunks, {checked} official units")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DATA)
    args = parser.parse_args()
    check(args.root)


if __name__ == "__main__":
    main()
