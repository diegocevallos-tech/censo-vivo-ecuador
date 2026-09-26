"""Add official census zone assets to the verified v2c Pages package."""

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
BASE = ROOT / "data/interim/release_public_v2c"
OUTPUT = ROOT / "data/interim/release_public_v2d"
STAGE = ROOT / "data/interim/zona_stage_v2d"
PUBLIC = STAGE / "data"
LOCAL = ROOT / "web/public/data"
REPLACEMENTS = {
    "counts-other-v1b.tar.gz": "counts-other-v2d.tar.gz",
    "tiles-v2c.tar.gz": "tiles-v2d.tar.gz",
    "indicators-v2a.tar.gz": "indicators-v2d.tar.gz",
}
NEW = {
    "counts/v1b1/zona/data.parquet": ("counts_parquet", "counts-other-v2d.tar.gz"),
    "tiles/v1b/zona/data.pmtiles": ("tiles", "tiles-v2d.tar.gz"),
    "indicator-maps/v2a/zona/data.bin": ("binary_chunks", "indicators-v2d.tar.gz"),
}
UPDATED = {"tiles/v1b/catalog.json", "indicator-maps/v2a/schema.json",
           "counts/v1b1/schema.json"}


def package() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["release"] != "data-derived-v2c":
        raise ValueError("Expected the verified public v2c package")
    restore(manifest, BASE, STAGE)
    for name in NEW.keys() | UPDATED:
        source = LOCAL / name
        if not source.is_file():
            raise FileNotFoundError(source)
        target = PUBLIC / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for item in manifest["files"]:
        if item["asset"] in REPLACEMENTS:
            item["asset"] = REPLACEMENTS[item["asset"]]
        if item["path"] in UPDATED:
            path = PUBLIC / item["path"]
            item["size_bytes"] = path.stat().st_size
            item["sha256"] = sha256_file(path)
    for name, (category, asset) in NEW.items():
        path = PUBLIC / name
        manifest["files"].append({"path": name, "size_bytes": path.stat().st_size,
                                  "sha256": sha256_file(path),
                                  "category": category, "asset": asset})
    verify(PUBLIC)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    assets = []
    for old in manifest["assets"]:
        name = old["name"]
        if name not in REPLACEMENTS:
            source = BASE / name
            if source.stat().st_size != old["size_bytes"] or sha256_file(source) != old["sha256"]:
                raise ValueError(f"Base asset changed: {name}")
            shutil.copy2(source, OUTPUT / name)
            assets.append(old)
            continue
        new_name = REPLACEMENTS[name]
        target = OUTPUT / new_name
        with tarfile.open(target, "w:gz", compresslevel=6) as archive:
            for item in sorted(manifest["files"], key=lambda entry: entry["path"]):
                if item["asset"] != new_name:
                    continue
                source = PUBLIC / item["path"]
                info = tarfile.TarInfo(item["path"])
                info.size = source.stat().st_size
                info.mode = 0o644
                info.mtime = 0
                with source.open("rb") as stream:
                    archive.addfile(info, stream)
        assets.append({"name": new_name, "size_bytes": target.stat().st_size,
                       "sha256": sha256_file(target)})
    manifest["assets"] = assets
    manifest["release"] = "data-derived-v2d"
    totals = check(manifest, yaml.safe_load((ROOT / "config.yaml").read_text(
        encoding="utf-8")))
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    result = {"release": manifest["release"], "totals": totals,
              "assets": {item["name"]: item["size_bytes"] for item in assets}}
    print(json.dumps(result))
    return result


if __name__ == "__main__":
    package()
