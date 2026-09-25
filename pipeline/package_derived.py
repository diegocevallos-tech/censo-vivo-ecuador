"""Package verified public aggregates as small Release assets and a SHA256 manifest."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tarfile
from pathlib import Path

import yaml
from check_derived_manifest import CONFIG, MANIFEST, ROOT, check

PUBLIC = ROOT / "web/public/data"
OUTPUT = ROOT / "data/interim/release_public_v1a"
RELEASE = "data-derived-v1a"
GROUPS = {
    "finest": "counts-finest-v1a.tar.gz",
    "sector": "counts-sector-v1a.tar.gz",
    "other": "counts-other-v1a.tar.gz",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def classify(relative: Path) -> str:
    parts = relative.parts
    if len(parts) >= 4 and parts[:2] == ("counts", "v1a"):
        if parts[2] == "finest" or parts[2:4] == ("categories", "finest"):
            return "finest"
        if parts[2] == "sector" or parts[2:4] == ("categories", "sector"):
            return "sector"
    return "other"


def main() -> None:
    subprocess.run(
        [sys.executable, str(ROOT / "pipeline/verify_public_artifacts.py")],
        check=True,
    )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    paths = [
        path for path in PUBLIC.rglob("*")
        if path.is_file()
        and path.name != ".gitkeep"
        and "sample" not in path.relative_to(PUBLIC).parts
    ]
    files = []
    by_group: dict[str, list[tuple[Path, Path]]] = {key: [] for key in GROUPS}
    for path in sorted(paths):
        relative = path.relative_to(PUBLIC)
        group = classify(relative)
        by_group[group].append((path, relative))
        files.append({
            "path": relative.as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "category": "counts_parquet",
            "asset": GROUPS[group],
        })
    assets = []
    for group, name in GROUPS.items():
        target = OUTPUT / name
        with tarfile.open(target, "w:gz", compresslevel=6) as archive:
            for path, relative in by_group[group]:
                info = tarfile.TarInfo(relative.as_posix())
                info.size = path.stat().st_size
                info.mode = 0o644
                info.mtime = 0
                with path.open("rb") as source:
                    archive.addfile(info, source)
        assets.append({
            "name": name,
            "size_bytes": target.stat().st_size,
            "sha256": sha256_file(target),
        })
    manifest = {
        "schema_version": 1,
        "release": RELEASE,
        "geom_version": "marco-2021",
        "assets": assets,
        "files": files,
    }
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    totals = check(manifest, config)
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Packaged {len(files)} files: {totals}")
    for asset in assets:
        print(f"{asset['name']}: {asset['size_bytes']} bytes")


if __name__ == "__main__":
    main()
