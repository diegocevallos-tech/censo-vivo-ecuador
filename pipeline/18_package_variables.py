"""Replace mixed-variable fine Parquet with exact, range-addressable bundles."""

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
BASE = ROOT / "data/interim/release_public_v2d"
OUTPUT = ROOT / "data/interim/release_public_v2e"
STAGE = ROOT / "data/interim/variables_stage_v2e"
PUBLIC = STAGE / "data"
LOCAL = ROOT / "web/public/data/variables/v2c"
OLD = "counts-finest-v1b.tar.gz"
NEW = "counts-fine-vars-v2e.tar.gz"


def package() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["release"] != "data-derived-v2d":
        raise ValueError("Expected verified v2d Release")
    restore(manifest, BASE, STAGE)
    removed = [item for item in manifest["files"] if item["path"].startswith(
        "counts/v1b1/categories/finest/")]
    if len(removed) != 24 or any(not item["path"].startswith(
        "counts/v1b1/categories/finest/") or item["asset"] != OLD for item in removed):
        raise ValueError("Unexpected original fine-category inventory")
    for item in removed:
        (PUBLIC / item["path"]).unlink()
    manifest["files"] = [item for item in manifest["files"] if item not in removed]
    for item in manifest["files"]:
        if item["asset"] == OLD:
            item["asset"] = NEW
    browser_files = sorted(LOCAL.glob("*.bin")) + [LOCAL / "index.json"]
    if len(browser_files) != 25 or any(not file.is_file() for file in browser_files):
        raise ValueError("Missing province variable bundle")
    for source in browser_files:
        name = f"variables/v2c/{source.name}"
        target = PUBLIC / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        manifest["files"].append({
            "path": name, "size_bytes": target.stat().st_size,
            "sha256": sha256_file(target), "category": "counts_parquet", "asset": NEW,
        })
    verify(PUBLIC)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    assets = []
    for old in manifest["assets"]:
        if old["name"] == OLD:
            continue
        source = BASE / old["name"]
        if source.stat().st_size != old["size_bytes"] or sha256_file(source) != old["sha256"]:
            raise ValueError(f"Base Release asset changed: {old['name']}")
        shutil.copy2(source, OUTPUT / old["name"])
        assets.append(old)
    archive_path = OUTPUT / NEW
    with tarfile.open(archive_path, "w:gz", compresslevel=6) as archive:
        for item in sorted(manifest["files"], key=lambda entry: entry["path"]):
            if item["asset"] != NEW:
                continue
            source = PUBLIC / item["path"]
            info = tarfile.TarInfo(item["path"])
            info.size = source.stat().st_size
            info.mode = 0o644
            info.mtime = 0
            with source.open("rb") as stream:
                archive.addfile(info, stream)
    assets.append({"name": NEW, "size_bytes": archive_path.stat().st_size,
                   "sha256": sha256_file(archive_path)})
    manifest["assets"] = assets
    manifest["release"] = "data-derived-v2e"
    totals = check(manifest, yaml.safe_load((ROOT / "config.yaml").read_text(
        encoding="utf-8")))
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    result = {"release": manifest["release"], "replaced_bytes": sum(
        item["size_bytes"] for item in removed), "bundles_bytes": sum(
            file.stat().st_size for file in browser_files), "totals": totals,
            "asset_bytes": archive_path.stat().st_size}
    print(json.dumps(result))
    return result


if __name__ == "__main__":
    package()
