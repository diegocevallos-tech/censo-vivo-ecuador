"""Check browser indicator indexes against their manifest and official units."""

from __future__ import annotations

import argparse
import json
import math
import struct
from pathlib import Path

import pyarrow.parquet as pq


def check(root: Path) -> None:
    index_root = root / "indicator-maps/v2a"
    schema = json.loads((index_root / "schema.json").read_text(encoding="utf-8"))
    if schema["format"] != "CVEI1" or schema["geom_version"] != "marco-2021":
        raise ValueError("Unexpected indicator schema")
    if len(schema["indicators"]) != 45 or len(set(schema["indicators"])) != 45:
        raise ValueError("Incomplete indicator catalog")
    populations = {}
    total_rows = 0
    for relative, expected in schema["files"].items():
        level, filename = relative.split("/")
        packed = (index_root / relative).read_bytes()
        rows, indicators = struct.unpack_from("<IH", packed, 5)
        if packed[:5] != b"CVEI1" or rows != expected["rows"] or indicators != 45:
            raise ValueError(f"Invalid header in {relative}")
        if len(packed) != expected["bytes"] or len(packed) != 11 + rows * schema["stride"]:
            raise ValueError(f"Invalid length in {relative}")
        suffix = filename.replace(".bin", ".parquet")
        source_level = "finest" if level == "finest" else level
        path = root / "counts/v1b1" / source_level / suffix
        official = pq.read_table(path, columns=["unit_key", "population"]).to_pydict()
        if rows != len(official["unit_key"]):
            raise ValueError(f"Missing official units in {relative}")
        keys = set(official["unit_key"])
        seen = set()
        for row in range(rows):
            offset = 11 + row * schema["stride"]
            key = packed[offset : offset + schema["key_bytes"]].split(b"\0", 1)[0].decode("ascii")
            if key not in keys or key in seen:
                raise ValueError(f"Unexpected or duplicated geographic key in {relative}: {key}")
            seen.add(key)
            for indicator in range(indicators):
                value, status = struct.unpack_from(
                    "<fB", packed, offset + schema["key_bytes"] + indicator * 5
                )
                if status not in {0, 1, 2, 3} or (status <= 1) != math.isfinite(value):
                    raise ValueError(f"Invalid cell in {relative}: {key} indicator {indicator}")
        populations[relative] = sum(official["population"])
        total_rows += rows
    if total_rows != 286_265 or populations["nacion/data.bin"] != 16_938_986:
        raise ValueError("Indicator index lacks official census units or population")
    print(
        f"Checked {len(schema['files'])} indicator files, {total_rows} units, 45 indicators"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1] / "web/public/data"
    )
    check(parser.parse_args().root)
