"""Convert 1B-2 profile and LISA tables to viewport-loadable typed arrays."""

from __future__ import annotations

import json
import struct
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/interim"
OUTPUT = ROOT / "web/public/data/chunks/v1b/analysis"
PROVINCES = tuple(f"{number:02d}" for number in range(1, 25))
KEY_BYTES = 12


def write_keys(stream, keys: list[str]) -> None:
    for key in keys:
        encoded = key.encode("ascii")
        if len(encoded) != KEY_BYTES:
            raise ValueError(f"Unexpected sector key: {key}")
        stream.write(encoded)


def build() -> dict:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    profiles = pq.read_table(SOURCE / "geodemographics_v1b2/twin_profiles.parquet").to_pandas()
    lisa = pq.read_table(SOURCE / "spatial_v1b2/lisa_sector.parquet").to_pandas()
    fields = [name for name in profiles if name.startswith("z_")]
    indicators = sorted(lisa.indicator.unique())
    clusters = sorted(lisa.cluster.unique())
    result = {
        "geom_version": "marco-2021",
        "key_bytes": KEY_BYTES,
        "profiles": {
            "magic": "CVEP1",
            "fields": fields,
            "layout": "magic[5],rows[u32],keys[rows*12],eligible[u8*rows],z[f32*rows*fields]",
        },
        "lisa": {
            "magic": "CVEL1",
            "indicators": indicators,
            "clusters": clusters,
            "layout": (
                "magic[5],rows[u32],keys[rows*12],indicator[u8*rows],"
                "cluster[u8*rows],value[f32*rows],local_i[f32*rows],p[f32*rows]"
            ),
        },
        "chunks": {},
    }
    for province in PROVINCES:
        subset = profiles[profiles.unit_key.str.startswith(province)].sort_values("unit_key")
        path = OUTPUT / f"profiles_{province}.bin"
        with path.open("wb") as stream:
            stream.write(b"CVEP1")
            stream.write(struct.pack("<I", len(subset)))
            write_keys(stream, subset.unit_key.to_list())
            stream.write(subset.rank_eligible.to_numpy(dtype=np.uint8).tobytes())
            stream.write(subset[fields].to_numpy(dtype="<f4").tobytes())
        result["chunks"][path.name] = {"rows": len(subset), "bytes": path.stat().st_size}
        subset = lisa[lisa.unit_key.str.startswith(province)].sort_values(["unit_key", "indicator"])
        path = OUTPUT / f"lisa_{province}.bin"
        with path.open("wb") as stream:
            stream.write(b"CVEL1")
            stream.write(struct.pack("<I", len(subset)))
            write_keys(stream, subset.unit_key.to_list())
            stream.write(
                np.array(
                    [indicators.index(value) for value in subset.indicator], dtype=np.uint8
                ).tobytes()
            )
            stream.write(
                np.array(
                    [clusters.index(value) for value in subset.cluster], dtype=np.uint8
                ).tobytes()
            )
            for field in ("value", "local_i", "permutation_p"):
                stream.write(subset[field].to_numpy(dtype="<f4").tobytes())
        result["chunks"][path.name] = {"rows": len(subset), "bytes": path.stat().st_size}
    (OUTPUT / "schema.json").write_text(
        json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "files": len(result["chunks"]),
                "bytes": sum(value["bytes"] for value in result["chunks"].values()),
            }
        )
    )
    return result


if __name__ == "__main__":
    build()
