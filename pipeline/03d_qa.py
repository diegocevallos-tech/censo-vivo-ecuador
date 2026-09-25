"""Check exact cross-count rollups and official national reference figures."""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = ROOT / "data/interim/cross_counts_v1b2"
LEVELS = ("finest", "sector", "parroquia", "canton", "provincia", "nacion")


def quote(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "''")


def check(root: Path) -> None:
    db = duckdb.connect()
    fields = [
        item[0] for item in db.execute(
            f"DESCRIBE SELECT * FROM read_parquet('{quote(root / 'nacion/data.parquet')}')"
        ).fetchall() if item[0] not in {"unit_key", "geom_version"}
    ]
    previous = None
    for level in LEVELS:
        file = root / level / ("*.parquet" if level == "finest" else "data.parquet")
        sums = db.execute(
            f"SELECT {','.join(f'SUM({field})' for field in fields)} "
            f"FROM read_parquet('{quote(file)}')"
        ).fetchone()
        if previous is not None and previous != sums:
            differences = {
                name: (left, right) for name, left, right in zip(
                    fields, previous, sums, strict=True
                ) if left != right
            }
            raise AssertionError(f"Cross-count rollup {level} differs: {differences}")
        previous = sums
        print(f"{level}: {len(fields)} additive fields, zero difference")
    national = dict(zip(fields, previous, strict=True))
    if national["all_heads"] != 5_188_827:
        raise AssertionError("Household representatives differ from INEC national households")
    checks = {
        "female_headship": (national["female_heads"] / national["all_heads"] * 100, 38.5),
        "illiteracy_15_plus": (
            national["illiterate_15"] / national["literacy_response_15"] * 100, 3.7
        ),
        "internet_use_5_plus": (
            national["internet_person_5"] / national["internet_response_5"] * 100, 69.4
        ),
    }
    for name, (own, official) in checks.items():
        if abs(own - official) > 0.5:
            raise AssertionError(f"{name} differs from INEC: own={own:.3f}, INEC={official}")
        print(f"{name}: {own:.3f}% (INEC {official:.1f}%)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    check(parser.parse_args().root)


if __name__ == "__main__":
    main()
