"""Replace only administrative PMTiles in the public v2a package."""

from __future__ import annotations

import hashlib
import json
import shutil
import tarfile
from pathlib import Path

import yaml
from check_derived_manifest import check
from deploy_derived import restore
from verify_public_artifacts import verify

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/interim/release_public_v2a"
OUTPUT = ROOT / "data/interim/release_public_v2c"
NAMED_TILES = ROOT / "web/public/data/tiles/v1b"
STAGE = ROOT / "data/interim/named_stage_v2c"
PUBLIC = STAGE / "data"
MANIFEST = ROOT / "data/DERIVED_MANIFEST.json"
NEW_ASSET = "tiles-v2c.tar.gz"
NAMED_LEVELS = ("provincia", "canton", "parroquia")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["release"] != "data-derived-v2a":
        raise ValueError("Expected the reviewed v2a package")
    restore(manifest, BASE, STAGE)
    for level in NAMED_LEVELS:
        source = NAMED_TILES / level / "data.pmtiles"
        if not source.is_file():
            raise FileNotFoundError(source)
        shutil.copy2(source, PUBLIC / "tiles/v1b" / level / "data.pmtiles")
    catalog_file = PUBLIC / "tiles/v1b/catalog.json"
    catalog = json.loads(catalog_file.read_text(encoding="utf-8"))
    catalog["name_source"] = "INEC DPA 2022"
    catalog["named_levels"] = list(NAMED_LEVELS)
    catalog_file.write_text(json.dumps(catalog, ensure_ascii=False,
                                       separators=(",", ":")) + "\n", encoding="utf-8")
    verify(PUBLIC)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    assets = []
    for asset in manifest["assets"]:
        old_name = asset["name"]
        if old_name != "tiles-v1b.tar.gz":
            source = BASE / old_name
            if not source.is_file() or sha256(source) != asset["sha256"]:
                raise ValueError(f"Altered v2a asset: {old_name}")
            shutil.copy2(source, OUTPUT / old_name)
            assets.append(asset)
            continue
        target = OUTPUT / NEW_ASSET
        with tarfile.open(target, "w:gz", compresslevel=6) as archive:
            for item in manifest["files"]:
                if item["asset"] != old_name:
                    continue
                file = PUBLIC / item["path"]
                info = tarfile.TarInfo(item["path"])
                info.size = file.stat().st_size
                info.mode = 0o644
                info.mtime = 0
                with file.open("rb") as stream:
                    archive.addfile(info, stream)
                item["asset"] = NEW_ASSET
                item["size_bytes"] = file.stat().st_size
                item["sha256"] = sha256(file)
        assets.append({"name": NEW_ASSET, "size_bytes": target.stat().st_size,
                       "sha256": sha256(target)})
    manifest["assets"] = assets
    manifest["release"] = "data-derived-v2c"
    totals = check(manifest, yaml.safe_load((ROOT / "config.yaml").read_text(
        encoding="utf-8"
    )))
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps({"release": manifest["release"], "totals": totals,
                      "assets": {asset["name"]: asset["size_bytes"] for asset in assets}}))
    return manifest


if __name__ == "__main__":
    package()
