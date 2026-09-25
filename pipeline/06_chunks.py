"""Pack exact official-unit numerator/denominator arrays by province.

CVEB1 layout: 5-byte magic, uint32 row count, fixed 15-byte ASCII keys,
then little-endian column arrays. Offsets and types live in schema.json.
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "data/interim/exact_public/counts/v1b1"
CROSS = ROOT / "data/interim/cross_counts_v1b2"
OUTPUT = ROOT / "web/public/data/chunks/v1b"
PROVINCES = tuple(f"{number:02d}" for number in range(1, 25))
MAGIC = b"CVEB1"
KEY_BYTES = 15


def dtype_for(maximum: int) -> str:
    if maximum <= 255:
        return "uint8"
    if maximum <= 65_535:
        return "uint16"
    if maximum <= 4_294_967_295:
        return "uint32"
    return "uint64"


def build() -> dict:
    if not (CORE / "schema.json").is_file() or not CROSS.is_dir():
        raise FileNotFoundError("Verified exact counts and 1B-2 crosses are required")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    schema: dict = {
        "format": "CVEB1", "geom_version": "marco-2021",
        "key_bytes": KEY_BYTES, "byte_order": "little", "chunks": {},
    }
    sector_cross = pq.read_table(CROSS / "sector/data.parquet").to_pandas()
    for level in ("finest", "sector"):
        for province in PROVINCES:
            core = pq.read_table(CORE / level / f"{province}.parquet").to_pandas()
            cross = (pq.read_table(CROSS / level / f"{province}.parquet").to_pandas()
                     if level == "finest" else
                     sector_cross[sector_cross.unit_key.str.startswith(province)].copy())
            if core.unit_key.duplicated().any() or cross.unit_key.duplicated().any():
                raise ValueError(f"Duplicate census key: {level}/{province}")
            if set(core.unit_key) != set(cross.unit_key):
                raise ValueError(f"Cross/count key mismatch: {level}/{province}")
            cross = cross.set_index("unit_key").loc[core.unit_key].reset_index()
            values = {name: core[name].to_numpy() for name in core.columns
                      if np.issubdtype(core[name].dtype, np.integer)}
            values.update({name: cross[name].to_numpy() for name in cross.columns
                           if np.issubdtype(cross[name].dtype, np.integer)
                           and name not in values})
            keys = core.unit_key.to_list()
            if any(len(key.encode("ascii")) > KEY_BYTES for key in keys):
                raise ValueError(f"Oversized geographic key: {level}/{province}")
            target = OUTPUT / level / f"{province}.bin"
            target.parent.mkdir(parents=True, exist_ok=True)
            columns = []
            with target.open("wb") as stream:
                stream.write(MAGIC)
                stream.write(struct.pack("<I", len(keys)))
                for key in keys:
                    stream.write(key.encode("ascii").ljust(KEY_BYTES, b"\0"))
                for name, source in values.items():
                    if (source < 0).any():
                        raise ValueError(f"Negative count: {level}/{province}/{name}")
                    kind = dtype_for(int(source.max(initial=0)))
                    array = source.astype(np.dtype("<" + np.dtype(kind).str[1:]), copy=False)
                    offset = stream.tell()
                    stream.write(array.tobytes(order="C"))
                    columns.append({"name": name, "type": kind, "offset": offset,
                                    "max": int(source.max(initial=0))})
            relative = target.relative_to(OUTPUT).as_posix()
            schema["chunks"][relative] = {"rows": len(keys), "columns": columns}
            print(f"{relative}: {len(keys)} units, {target.stat().st_size} bytes", flush=True)
    (OUTPUT / "schema.json").write_text(
        json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return schema


if __name__ == "__main__":
    build()
