"""Compare per-file byte sizes of a prior aggregate artifact and a new package."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def inventory(root: Path) -> dict[str, int]:
    return {
        path.relative_to(root).as_posix(): path.stat().st_size
        for path in root.rglob("*")
        if path.is_file()
        and path.name != ".gitkeep"
        and "sample" not in path.relative_to(root).parts
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    before = inventory(args.before)
    after = inventory(args.after)
    if not before or not after:
        raise ValueError("Both aggregate inventories must contain files")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("archivo", "antes_bytes", "despues_bytes"))
        for path in sorted(before.keys() | after.keys()):
            writer.writerow((path, before.get(path, 0), after.get(path, 0)))
        writer.writerow(("TOTAL", sum(before.values()), sum(after.values())))
    print(f"Before: {len(before)} files, {sum(before.values())} bytes")
    print(f"After: {len(after)} files, {sum(after.values())} bytes")


if __name__ == "__main__":
    main()
