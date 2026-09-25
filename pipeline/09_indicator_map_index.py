"""Precompute map values from exact official-unit aggregates, never person rows.

The binary index is a delivery format. Indicators remain defined and tested in
indicators.yaml and are evaluated with the same additive Python engine.
"""

from __future__ import annotations

import json
import math
import struct
from pathlib import Path

import pyarrow.parquet as pq
import yaml
from aggregation import Aggregate
from indicators import evaluate

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data/interim"
CORE = INTERIM / "exact_public/counts/v1b1"
CROSS = INTERIM / "cross_counts_v1b2"
CATEGORIES = INTERIM / "full_aggregate_v1a/counts/v1a/categories"
OUTPUT = ROOT / "web/public/data/indicator-maps/v2a"
LEVELS = ("finest", "sector", "parroquia", "canton", "provincia", "nacion")
PROVINCES = tuple(f"{number:02d}" for number in range(1, 25))
MAGIC = b"CVEI1"
KEY_BYTES = 15


def strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [part for item in value for part in strings(item)]
    if isinstance(value, dict):
        return [part for item in value.values() for part in strings(item)]
    return []


def needed_categories(definitions: list[dict]) -> set[str]:
    terms = {
        term
        for definition in definitions
        for term in strings(definition)
        if term.startswith("cat:")
    }
    for definition in definitions:
        if definition["kind"] == "weighted_mean":
            stem = f"cat:{definition['source_table']}:{definition['source_variable']}:"
            terms.update(
                stem + str(number)
                for number in range(definition["valid_min"], definition["valid_max"] + 1)
            )
    return terms


def sources(level: str, province: str | None) -> tuple[Path, Path, list[Path]]:
    name = f"{province}.parquet" if province else "data.parquet"
    core = CORE / level / name
    cross = CROSS / level / name
    if not cross.is_file() and province:
        cross = CROSS / level / "data.parquet"
    if level == "finest":
        category_files = sorted((CATEGORIES / level).glob(f"*/{province}.parquet"))
    elif province:
        category_files = sorted((CATEGORIES / level / f"province_key={province}").glob("*.parquet"))
    elif level in {"parroquia", "canton"}:
        category_files = sorted((CATEGORIES / level).glob("province_key=*/*.parquet"))
    else:
        category_files = [CATEGORIES / level / "data.parquet"]
    if not core.is_file() or not cross.is_file() or not category_files:
        raise FileNotFoundError(f"Missing exact aggregate sources for {level} {province}")
    return core, cross, category_files


def rows_for(
    level: str, province: str | None, wanted: set[str]
) -> list[tuple[str, str, dict[str, float]]]:
    core_file, cross_file, category_files = sources(level, province)
    core_rows = pq.read_table(core_file).to_pylist()
    output: list[tuple[str, str, dict[str, float]]] = []
    lookup: dict[str, dict[str, float]] = {}
    for item in core_rows:
        key = item["unit_key"]
        counts = {
            f"core:{name}": float(value)
            for name, value in item.items()
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        }
        lookup[key] = counts
        output.append((key, item["unit_level"], counts))
    for item in pq.read_table(cross_file).to_pylist():
        if province and not item["unit_key"].startswith(province):
            continue
        counts = lookup.get(item["unit_key"])
        if counts is None:
            raise AssertionError(f"Cross unit absent from core: {item['unit_key']}")
        counts.update(
            {
                f"cross:{name}": float(value)
                for name, value in item.items()
                if isinstance(value, (int, float)) and not isinstance(value, bool)
            }
        )
    for path in category_files:
        for batch in pq.ParquetFile(path).iter_batches(
            batch_size=65_536, columns=["unit_key", "source_table", "variable", "category", "n"]
        ):
            for item in batch.to_pylist():
                term = f"cat:{item['source_table']}:{item['variable']}:{item['category']}"
                if term in wanted:
                    counts = lookup.get(item["unit_key"])
                    if counts is not None:
                        counts[term] = counts.get(term, 0.0) + item["n"]
    return output


def write_index(
    path: Path, rows: list[tuple[str, str, dict[str, float]]], definitions: list[dict], level: str
) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as stream:
        stream.write(MAGIC)
        stream.write(struct.pack("<IH", len(rows), len(definitions)))
        for key, unit_level, counts in rows:
            encoded = key.encode("ascii")
            if len(encoded) > KEY_BYTES:
                raise ValueError(f"Unit key exceeds {KEY_BYTES} bytes: {key}")
            stream.write(encoded.ljust(KEY_BYTES, b"\0"))
            for definition in definitions:
                result = evaluate(
                    definition,
                    Aggregate(counts, "exacto", 0),
                    level=unit_level if level == "finest" else level,
                )
                if result.unavailable_reason:
                    value, status = math.nan, 2
                elif result.value is None:
                    value, status = math.nan, 3
                else:
                    value = result.value
                    status = 1 if result.small_n else 0
                stream.write(struct.pack("<fB", value, status))
    return {"rows": len(rows), "bytes": path.stat().st_size}


def main() -> None:
    definitions = yaml.safe_load((ROOT / "indicators.yaml").read_text(encoding="utf-8"))[
        "indicators"
    ]
    wanted = needed_categories(definitions)
    files = {}
    for level in LEVELS:
        for province in PROVINCES if level in {"finest", "sector"} else (None,):
            relative = f"{level}/{province or 'data'}.bin"
            existing = OUTPUT / relative
            if existing.is_file():
                with existing.open("rb") as stream:
                    header = stream.read(11)
                if header[:5] == MAGIC:
                    rows, indicators = struct.unpack("<IH", header[5:])
                    if indicators == len(definitions) and existing.stat().st_size == 11 + rows * (
                        KEY_BYTES + 5 * indicators
                    ):
                        files[relative] = {"rows": rows, "bytes": existing.stat().st_size}
                        print(f"{relative}: verified existing {rows} units", flush=True)
                        continue
            records = rows_for(level, province, wanted)
            files[relative] = write_index(
                OUTPUT / relative, records, definitions, "manzana" if level == "finest" else level
            )
            print(
                f"{relative}: {files[relative]['rows']} units, {files[relative]['bytes']} bytes",
                flush=True,
            )
    schema = {
        "format": MAGIC.decode(),
        "geom_version": "marco-2021",
        "key_bytes": KEY_BYTES,
        "stride": KEY_BYTES + 5 * len(definitions),
        "indicators": [item["id"] for item in definitions],
        "files": files,
    }
    (OUTPUT / "schema.json").write_text(json.dumps(schema, separators=(",", ":")), encoding="utf-8")
    print(f"Total {sum(item['bytes'] for item in files.values()):,} bytes")


if __name__ == "__main__":
    main()
