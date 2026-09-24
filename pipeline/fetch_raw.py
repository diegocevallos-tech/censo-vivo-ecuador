"""Restore verified original INEC archives from a private GitHub Release.

The private repository requires ``gh auth login`` with authorized access.
Downloaded person-level records stay under ``data/raw/``, which is gitignored.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "data" / "MANIFEST.json"
BLOCK_SIZE = 8 * 1024 * 1024


def safe_name(name: str) -> str:
    if not name or Path(name).name != name or "/" in name or "\\" in name:
        raise ValueError(f"Unsafe asset name in manifest: {name!r}")
    return name


def verify(path: Path, expected_size: int, expected_sha256: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.stat().st_size != expected_size:
        raise ValueError(f"Size mismatch: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(BLOCK_SIZE), b""):
            digest.update(block)
    if digest.hexdigest() != expected_sha256:
        raise ValueError(f"SHA256 mismatch: {path}")


def download_asset(repo: str, tag: str, asset: dict) -> Path:
    name = safe_name(asset["name"])
    path = RAW / name
    if path.exists():
        verify(path, asset["size_bytes"], asset["sha256"])
        return path
    subprocess.run(
        [
            "gh",
            "release",
            "download",
            tag,
            "--repo",
            repo,
            "--pattern",
            name,
            "--dir",
            str(RAW),
        ],
        check=True,
    )
    verify(path, asset["size_bytes"], asset["sha256"])
    return path


def restore(entry: dict, repo: str, tag: str) -> None:
    filename = safe_name(entry["filename"])
    target = RAW / filename
    if target.exists():
        verify(target, entry["size_bytes"], entry["sha256"])
        print(f"Verified existing {filename}")
        return
    assets = entry.get("release_assets")
    if not assets or not entry.get("published_to_private_release"):
        raise ValueError(f"Source {entry['id']} is not available in the private Release")
    parts = [download_asset(repo, tag, asset) for asset in assets]
    if len(parts) == 1 and parts[0].name == filename:
        verify(target, entry["size_bytes"], entry["sha256"])
    else:
        partial = RAW / f"{filename}.reassembling"
        with partial.open("wb") as output:
            for part in parts:
                with part.open("rb") as stream:
                    for block in iter(lambda: stream.read(BLOCK_SIZE), b""):
                        output.write(block)
        verify(partial, entry["size_bytes"], entry["sha256"])
        partial.replace(target)
    print(f"Restored and verified {filename}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="*", help="Source IDs; omitted means all Release sources")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    release = manifest["private_release"]
    available = {entry["id"]: entry for entry in manifest["sources"]}
    selected = args.source or list(available)
    unknown = set(selected) - set(available)
    if unknown:
        parser.error(f"Unknown source IDs: {', '.join(sorted(unknown))}")
    RAW.mkdir(parents=True, exist_ok=True)
    for source_id in selected:
        restore(available[source_id], release["repo"], release["tag"])


if __name__ == "__main__":
    main()
