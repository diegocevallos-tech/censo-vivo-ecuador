"""Validate the public derived data inventory and Pages size budget."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path, PurePosixPath

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/DERIVED_MANIFEST.json"
CONFIG = ROOT / "config.yaml"
DATA_SUFFIXES = {".parquet", ".pmtiles", ".bin", ".json"}
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def safe_relative(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"Unsafe derived path: {name}")
    if "\\" in name or ":" in name:
        raise ValueError(f"Non-POSIX derived path: {name}")
    return path


def check(manifest: dict, config: dict) -> dict[str, int]:
    budget = config["derived_budget_bytes"]
    release = manifest.get("release", "")
    if manifest.get("schema_version") != 1 or not re.fullmatch(
        r"data-derived-v[0-9]+[a-z0-9]*", release
    ):
        raise ValueError("Unexpected derived manifest version or release")
    assets = manifest.get("assets", [])
    files = manifest.get("files", [])
    if not assets or not files:
        raise ValueError("Derived manifest has no release assets or browser files")
    asset_names = set()
    for asset in assets:
        name = safe_relative(asset["name"])
        if len(name.parts) != 1 or name.suffix != ".gz":
            raise ValueError(f"Unexpected release asset: {name}")
        if str(name) in asset_names:
            raise ValueError(f"Duplicate release asset: {name}")
        asset_names.add(str(name))
        if (
            not isinstance(asset["size_bytes"], int)
            or not 0 < asset["size_bytes"] <= config["maximum_release_asset_bytes"]
        ):
            raise ValueError(f"Release asset exceeds 2 GiB: {name}")
        if not SHA256.fullmatch(asset["sha256"]):
            raise ValueError(f"Invalid SHA256 for {name}")
    totals: defaultdict[str, int] = defaultdict(int)
    paths = set()
    for item in files:
        path = safe_relative(item["path"])
        if str(path) in paths:
            raise ValueError(f"Duplicate browser file: {path}")
        paths.add(str(path))
        if path.suffix not in DATA_SUFFIXES:
            raise ValueError(f"Forbidden derived file type: {path}")
        if item["asset"] not in asset_names:
            raise ValueError(f"Missing release asset for {path}")
        if (
            not isinstance(item["size_bytes"], int)
            or not 0 < item["size_bytes"] <= budget["maximum_browser_file"]
        ):
            raise ValueError(f"Browser file exceeds 95 MB: {path}")
        if not SHA256.fullmatch(item["sha256"]):
            raise ValueError(f"Invalid SHA256 for {path}")
        category = item["category"]
        if category not in {"counts_parquet", "tiles", "binary_chunks"}:
            raise ValueError(f"Unknown data budget category: {category}")
        totals[category] += item["size_bytes"]
    for category in ("counts_parquet", "tiles", "binary_chunks"):
        if totals[category] > budget[category]:
            raise ValueError(f"{category} exceeds budget: {totals[category]} > {budget[category]}")
    if sum(totals.values()) + budget["app"] > budget["total_target"]:
        raise ValueError("Derived data plus reserved app size exceeds 800 MB target")
    if sum(totals.values()) + budget["app"] > config["maximum_pages_site_bytes"]:
        raise ValueError("Derived data plus reserved app size exceeds Pages 1 GB limit")
    return dict(totals)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--app-dir", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    totals = check(manifest, config)
    if args.app_dir:
        app_bytes = sum(
            path.stat().st_size
            for path in args.app_dir.rglob("*")
            if path.is_file() and "data" not in path.relative_to(args.app_dir).parts
        )
        if app_bytes > config["derived_budget_bytes"]["app"]:
            raise ValueError(f"App exceeds 20 MB budget: {app_bytes}")
        totals["app"] = app_bytes
    print(json.dumps({"release": manifest["release"], "totals": totals}, sort_keys=True))


if __name__ == "__main__":
    main()
