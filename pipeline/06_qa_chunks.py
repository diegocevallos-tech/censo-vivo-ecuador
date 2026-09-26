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
    analysis = json.loads((chunk_root / "analysis/schema.json").read_text(encoding="utf-8"))
    sector_keys = set()
    for province in (f"{number:02d}" for number in range(1, 25)):
        sector_keys.update(pq.read_table(
            root / "counts/v1b1/sector" / f"{province}.parquet",
            columns=["unit_key"],
        )["unit_key"].to_pylist())
    analysis_rows = 0
    for name, metadata in analysis["chunks"].items():
        raw = (chunk_root / "analysis" / name).read_bytes()
        magic = b"CVEP1" if name.startswith("profiles_") else b"CVEL1"
        rows = struct.unpack_from("<I", raw, 5)[0]
        if raw[:5] != magic or rows != metadata["rows"]:
            raise AssertionError(f"Invalid analysis chunk header: {name}")
        keys = [raw[9 + index * 12:9 + (index + 1) * 12].decode("ascii")
                for index in range(rows)]
        if not set(keys) <= sector_keys:
            raise AssertionError(f"Analysis chunk contains a non-sector key: {name}")
        extra = rows + rows * len(analysis["profiles"]["fields"]) * 4
        if magic == b"CVEL1":
            extra = rows * (2 + 3 * 4)
        expected_size = 9 + rows * 12 + extra
        if len(raw) != expected_size:
            raise AssertionError(f"Analysis chunk size mismatch: {name}")
        analysis_rows += rows
    print(f"Validated {len(schema['chunks'])} count chunks ({checked} units) and "
          f"{len(analysis['chunks'])} analysis chunks ({analysis_rows} sector rows)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DATA)
    args = parser.parse_args()
    check(args.root)


if __name__ == "__main__":
    main()
