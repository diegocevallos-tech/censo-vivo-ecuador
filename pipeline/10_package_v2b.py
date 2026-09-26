"""Publish corrected audited aggregates and a cantonal diaspora profile."""

from __future__ import annotations

import hashlib
import json
import shutil
import tarfile
from pathlib import Path

import yaml
from check_derived_manifest import check
from verify_public_artifacts import verify

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data/interim"
PUBLIC = ROOT / "web/public/data"
BASE = INTERIM / "release_public_v2a"
OUTPUT = INTERIM / "release_public_v2b"
MANIFEST = ROOT / "data/DERIVED_MANIFEST.json"
REPLACEMENTS = {
    "counts-other-v1b.tar.gz": "counts-other-v2b.tar.gz",
    "chunks-v1b.tar.gz": "chunks-v2b.tar.gz",
}
STAGED = {
    "mobility/v1b2/emigrant_profile_canton.parquet":
        INTERIM / "mobility_v1b2/emigrant_profile_canton.parquet",
    "geodemographics/v1b2/clusters.json":
        INTERIM / "geodemographics_v1b2/clusters.json",
    "geodemographics/v1b2/sector_clusters.parquet":
        INTERIM / "geodemographics_v1b2/sector_clusters.parquet",
    "geodemographics/v1b2/twin_profiles_parroquia.parquet":
        INTERIM / "geodemographics_v1b2/twin_profiles_parroquia.parquet",
    "geodemographics/v1b2/twin_profiles_canton.parquet":
        INTERIM / "geodemographics_v1b2/twin_profiles_canton.parquet",
    "spatial/v1b2/moran_canton.parquet":
        INTERIM / "spatial_v1b2/moran_canton.parquet",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def package() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["release"] != "data-derived-v2a":
        raise ValueError("Expected reviewed v2a manifest")
    for relative, source in STAGED.items():
        if not source.is_file():
            raise FileNotFoundError(source)
        target = PUBLIC / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    verify(PUBLIC)
    existing = {item["path"]: item for item in manifest["files"]}
    for relative in STAGED:
        if relative not in existing:
            existing[relative] = {"path": relative, "category": "counts_parquet",
                                  "asset": "counts-other-v1b.tar.gz"}
    for item in existing.values():
        item["asset"] = REPLACEMENTS.get(item["asset"], item["asset"])
        if item["asset"] in REPLACEMENTS.values():
            file = PUBLIC / item["path"]
            item["size_bytes"] = file.stat().st_size
            item["sha256"] = sha256(file)
    manifest["files"] = sorted(existing.values(), key=lambda item: item["path"])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    assets = []
    for asset in manifest["assets"]:
        old = asset["name"]
        name = REPLACEMENTS.get(old, old)
        target = OUTPUT / name
        if old in REPLACEMENTS:
            with tarfile.open(target, "w:gz", compresslevel=6) as archive:
                for item in manifest["files"]:
                    if item["asset"] != name:
                        continue
                    file = PUBLIC / item["path"]
                    info = tarfile.TarInfo(item["path"])
                    info.size = file.stat().st_size
                    info.mode = 0o644
                    info.mtime = 0
                    with file.open("rb") as stream:
                        archive.addfile(info, stream)
        else:
            origin = BASE / name
            if not origin.is_file() or sha256(origin) != asset["sha256"]:
                raise ValueError(f"Missing or altered base asset: {name}")
            shutil.copy2(origin, target)
        assets.append({"name": name, "size_bytes": target.stat().st_size,
                       "sha256": sha256(target)})
    manifest["assets"] = assets
    manifest["release"] = "data-derived-v2b"
    totals = check(manifest, yaml.safe_load((ROOT / "config.yaml").read_text(
        encoding="utf-8"
    )))
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps({"release": manifest["release"], "totals": totals,
                      "asset_bytes": {a["name"]: a["size_bytes"] for a in assets}}))
    return manifest


if __name__ == "__main__":
    package()
