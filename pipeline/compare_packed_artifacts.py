"""Compare aggregate release candidates from local and private CI builds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pyarrow.parquet as pq


def inventory(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and path.name != ".gitkeep"
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", type=Path, required=True)
    parser.add_argument("--ci", type=Path, required=True)
    args = parser.parse_args()
    local = inventory(args.local)
    ci = inventory(args.ci)
    if local.keys() != ci.keys():
        raise ValueError(f"File lists differ: {local.keys() ^ ci.keys()}")
    parquet_count = 0
    for name in sorted(local):
        if name.endswith(".parquet"):
            left = pq.read_table(local[name])
            right = pq.read_table(ci[name])
            if "unit_key" in left.column_names:
                left = left.sort_by("unit_key")
                right = right.sort_by("unit_key")
            if not left.equals(right):
                details = []
                if left.schema != right.schema:
                    details.append(f"schema: {left.schema} vs {right.schema}")
                if left.num_rows != right.num_rows:
                    details.append(f"rows: {left.num_rows} vs {right.num_rows}")
                for column in set(left.column_names) & set(right.column_names):
                    if not left.column(column).equals(right.column(column)):
                        details.append(f"first differing column: {column}")
                        a = left.column(column).to_pylist()
                        b = right.column(column).to_pylist()
                        position = next(
                            i for i, (x, y) in enumerate(zip(a, b, strict=True))
                            if x != y
                        )
                        details.append(
                            f"row {position} keys {left.column('unit_key')[position].as_py()}"
                            f"/{right.column('unit_key')[position].as_py()}"
                            f" local={a[position]} ci={b[position]}"
                        )
                        break
                raise ValueError(f"Aggregate Parquet content differs: {name}; {details}")
            parquet_count += 1
        elif name.endswith(".json"):
            if json.loads(local[name].read_text(encoding="utf-8")) != json.loads(
                ci[name].read_text(encoding="utf-8")
            ):
                raise ValueError(f"Aggregate metadata differs: {name}")
        elif local[name].read_bytes() != ci[name].read_bytes():
            raise ValueError(f"Aggregate file differs: {name}")
    print(f"Equivalent local and CI aggregates: {parquet_count} Parquet, {len(local)} files")


if __name__ == "__main__":
    main()
