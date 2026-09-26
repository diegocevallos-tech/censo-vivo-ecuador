"""Add small municipal reference geography and aggregates to verified v2e."""

from __future__ import annotations

import json
import shutil
import tarfile
from pathlib import Path

import yaml
from check_derived_manifest import check
from deploy_derived import restore, sha256_file
from verify_public_artifacts import verify

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/DERIVED_MANIFEST.json"
BASE = ROOT / "data/interim/release_public_v2e"
OUTPUT = ROOT / "data/interim/release_public_v2f"
STAGE = ROOT / "data/interim/municipal_stage_v2f"
PUBLIC = STAGE / "data"
LOCAL = ROOT / "data/interim/municipal_urban"
WEB = ROOT / "web/public/data/municipal-urban/v1"
ASSET = "municipal-urban-v2f.tar.gz"
FILES = {
    "boundaries.geojson": "tiles",
    "summary.json": "counts_parquet",
    "urban_counts.parquet": "counts_parquet",
}


def package() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["release"] != "data-derived-v2e":
        raise ValueError("Expected verified v2e Release")
    restore(manifest, BASE, STAGE)
    WEB.mkdir(parents=True, exist_ok=True)
    for filename, category in FILES.items():
        source = LOCAL / filename
        if not source.is_file():
            raise FileNotFoundError(source)
        relative = f"municipal-urban/v1/{filename}"
        destination = PUBLIC / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        shutil.copy2(source, WEB / filename)
        manifest["files"].append({
            "path": relative, "size_bytes": source.stat().st_size,
            "sha256": sha256_file(source), "category": category, "asset": ASSET,
        })
    verify(PUBLIC)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    assets = []
    for old in manifest["assets"]:
        source = BASE / old["name"]
        if source.stat().st_size != old["size_bytes"] or sha256_file(source) != old["sha256"]:
            raise ValueError(f"Base Release asset changed: {old['name']}")
        shutil.copy2(source, OUTPUT / old["name"])
        assets.append(old)
    archive_path = OUTPUT / ASSET
    with tarfile.open(archive_path, "w:gz", compresslevel=6) as archive:
        for filename in FILES:
            relative = f"municipal-urban/v1/{filename}"
            source = PUBLIC / relative
            info = tarfile.TarInfo(relative)
            info.size = source.stat().st_size
            info.mode = 0o644
            info.mtime = 0
            with source.open("rb") as stream:
                archive.addfile(info, stream)
    assets.append({"name": ASSET, "size_bytes": archive_path.stat().st_size,
                   "sha256": sha256_file(archive_path)})
    manifest["assets"] = assets
    manifest["release"] = "data-derived-v2f"
    totals = check(manifest, yaml.safe_load((ROOT / "config.yaml").read_text(
        encoding="utf-8")))
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    result = {"release": manifest["release"], "totals": totals,
              "asset_bytes": archive_path.stat().st_size}
    print(json.dumps(result))
    return result


if __name__ == "__main__":
    package()
