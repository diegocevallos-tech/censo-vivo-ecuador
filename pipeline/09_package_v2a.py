"""Add official-unit indicator map indexes to a new public Release manifest."""

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
BASE_ASSETS = ROOT / "data/interim/release_public_v1b"
OUTPUT = ROOT / "data/interim/release_public_v2a"
PUBLIC = ROOT / "web/public/data"
MANIFEST = ROOT / "data/DERIVED_MANIFEST.json"
ASSET = "indicators-v2a.tar.gz"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["release"] != "data-derived-v1b":
        raise ValueError("Expected the reviewed v1b manifest as input")
    source = PUBLIC / "indicator-maps/v2a"
    schema = json.loads((source / "schema.json").read_text(encoding="utf-8"))
    if schema["format"] != "CVEI1" or len(schema["indicators"]) != 45:
        raise ValueError("Indicator index has unexpected schema")
    verify(PUBLIC)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for asset in manifest["assets"]:
        origin = BASE_ASSETS / asset["name"]
        if not origin.is_file() or sha256(origin) != asset["sha256"]:
            raise ValueError(f"Missing or changed v1b asset: {origin}")
        shutil.copy2(origin, OUTPUT / asset["name"])
    paths = sorted(path for path in source.rglob("*") if path.is_file())
    target = OUTPUT / ASSET
    with tarfile.open(target, "w:gz", compresslevel=6) as archive:
        for path in paths:
            relative = path.relative_to(PUBLIC).as_posix()
            info = tarfile.TarInfo(relative)
            info.size = path.stat().st_size
            info.mode = 0o644
            info.mtime = 0
            with path.open("rb") as stream:
                archive.addfile(info, stream)
    manifest["release"] = "data-derived-v2a"
    manifest["assets"].append(
        {"name": ASSET, "size_bytes": target.stat().st_size, "sha256": sha256(target)}
    )
    for path in paths:
        manifest["files"].append(
            {
                "path": path.relative_to(PUBLIC).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
                "category": "binary_chunks",
                "asset": ASSET,
            }
        )
    config = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    totals = check(manifest, config)
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "release": manifest["release"],
                "files": len(manifest["files"]),
                "assets": len(manifest["assets"]),
                "totals": totals,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
