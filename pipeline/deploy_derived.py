"""Restore verified public Release aggregates into the Pages build directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tarfile
from pathlib import Path

import yaml
from check_derived_manifest import CONFIG, MANIFEST, ROOT, check, safe_relative


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def restore(manifest: dict, asset_dir: Path, dist: Path) -> None:
    destination = (dist / "data").resolve()
    destination.mkdir(parents=True, exist_ok=True)
    expected = {item["path"]: item for item in manifest["files"]}
    restored = set()
    for asset in manifest["assets"]:
        archive = asset_dir / asset["name"]
        if archive.stat().st_size != asset["size_bytes"]:
            raise ValueError(f"Release asset size changed: {archive.name}")
        if sha256_file(archive) != asset["sha256"]:
            raise ValueError(f"Release asset SHA256 changed: {archive.name}")
        with tarfile.open(archive, "r:gz") as source:
            for member in source:
                relative = safe_relative(member.name)
                name = str(relative)
                if not member.isfile() or name not in expected:
                    raise ValueError(f"Unexpected member in derived archive: {member.name}")
                if expected[name]["asset"] != asset["name"] or name in restored:
                    raise ValueError(f"Duplicate or misplaced derived file: {name}")
                target = (destination / name).resolve()
                if not target.is_relative_to(destination):
                    raise ValueError(f"Unsafe archive target: {name}")
                target.parent.mkdir(parents=True, exist_ok=True)
                digest = hashlib.sha256()
                size = 0
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError(f"Unreadable derived archive member: {name}")
                with stream, target.open("wb") as output:
                    while block := stream.read(8 * 1024 * 1024):
                        output.write(block)
                        digest.update(block)
                        size += len(block)
                if (
                    size != expected[name]["size_bytes"]
                    or digest.hexdigest() != expected[name]["sha256"]
                ):
                    raise ValueError(f"Derived file checksum mismatch: {name}")
                restored.add(name)
    if restored != set(expected):
        raise ValueError(f"Missing {len(set(expected) - restored)} derived browser files")
    print(f"Restored {len(restored)} verified aggregate files to {destination}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--dist", type=Path, default=ROOT / "web/dist")
    parser.add_argument("--local-assets", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    check(manifest, config)
    asset_dir = args.local_assets or ROOT / "data/interim/derived_release_download"
    asset_dir.mkdir(parents=True, exist_ok=True)
    if args.local_assets is None:
        for asset in manifest["assets"]:
            subprocess.run(
                [
                    "gh", "release", "download", manifest["release"],
                    "--repo", "diegocevallos-tech/censo-vivo-ecuador",
                    "--pattern", asset["name"], "--dir", str(asset_dir), "--clobber",
                ],
                check=True,
            )
    restore(manifest, asset_dir, args.dist)
    subprocess.run(
        [
            sys.executable, str(ROOT / "pipeline/verify_public_artifacts.py"),
            "--root", str(args.dist / "data"),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
