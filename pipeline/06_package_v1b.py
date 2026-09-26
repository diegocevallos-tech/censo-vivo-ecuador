"""Stage checked aggregates, enforce Pages budgets, and make public Release assets."""

from __future__ import annotations

import hashlib
import json
import shutil
import tarfile
from pathlib import Path

import yaml
from check_derived_manifest import check

ROOT = Path(__file__).resolve().parents[1]
INTERIM = ROOT / "data/interim"
PUBLIC = ROOT / "web/public/data"
OUTPUT = INTERIM / "release_public_v1b"
MANIFEST = ROOT / "data/DERIVED_MANIFEST.json"
GROUPS = {
    "counts_finest": "counts-finest-v1b.tar.gz",
    "counts_other": "counts-other-v1b.tar.gz",
    "tiles": "tiles-v1b.tar.gz",
    "chunks": "chunks-v1b.tar.gz",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def copy_tree(source: Path, destination: Path, allowed: set[str] | None = None) -> None:
    if not source.is_dir():
        raise FileNotFoundError(source)
    for path in source.rglob("*"):
        if path.is_file() and (allowed is None or path.name in allowed):
            target = destination / path.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def stage() -> None:
    obsolete = (PUBLIC / "counts/v1a").resolve()
    if not obsolete.is_relative_to(PUBLIC.resolve()):
        raise ValueError("Unsafe obsolete package path")
    if obsolete.is_dir():
        shutil.rmtree(obsolete)
    copy_tree(INTERIM / "exact_public/counts/v1b1", PUBLIC / "counts/v1b1")
    copy_tree(INTERIM / "cross_counts_v1b2", PUBLIC / "cross/v1b2")
    copy_tree(INTERIM / "mobility_v1b2", PUBLIC / "mobility/v1b2")
    copy_tree(
        INTERIM / "geodemographics_v1b2",
        PUBLIC / "geodemographics/v1b2",
        {"clusters.json", "sector_clusters.parquet"},
    )
    copy_tree(
        INTERIM / "spatial_v1b2",
        PUBLIC / "spatial/v1b2",
        {"moran_canton.parquet", "dissimilarity_canton.parquet"},
    )
    if not (PUBLIC / "tiles/v1b/catalog.json").is_file():
        raise FileNotFoundError("PMTiles catalog must be built before packaging")
    if not (PUBLIC / "chunks/v1b/schema.json").is_file():
        raise FileNotFoundError("Binary chunks must be built before packaging")


def group_for(relative: Path) -> tuple[str, str]:
    if relative.parts[0] == "tiles":
        return "tiles", "tiles"
    if relative.parts[0] == "chunks":
        return "chunks", "binary_chunks"
    if relative.parts[:3] == ("counts", "v1b1", "finest") or (
        relative.parts[:4] == ("counts", "v1b1", "categories", "finest")
    ):
        return "counts_finest", "counts_parquet"
    return "counts_other", "counts_parquet"


def package() -> dict:
    stage()
    from verify_public_artifacts import verify  # avoid importing PyArrow until staging

    verify(PUBLIC)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    paths = sorted(
        path
        for path in PUBLIC.rglob("*")
        if path.is_file()
        and path.name != ".gitkeep"
        and "sample" not in path.relative_to(PUBLIC).parts
    )
    by_group: dict[str, list[tuple[Path, Path]]] = {group: [] for group in GROUPS}
    files = []
    for path in paths:
        relative = path.relative_to(PUBLIC)
        group, category = group_for(relative)
        by_group[group].append((path, relative))
        files.append(
            {
                "path": relative.as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
                "category": category,
                "asset": GROUPS[group],
            }
        )
    assets = []
    for group, name in GROUPS.items():
        target = OUTPUT / name
        with tarfile.open(target, "w:gz", compresslevel=6) as archive:
            for path, relative in by_group[group]:
                info = tarfile.TarInfo(relative.as_posix())
                info.size = path.stat().st_size
                info.mode = 0o644
                info.mtime = 0
                with path.open("rb") as stream:
                    archive.addfile(info, stream)
        assets.append({"name": name, "size_bytes": target.stat().st_size, "sha256": sha256(target)})
    manifest = {
        "schema_version": 1,
        "release": "data-derived-v1b",
        "geom_version": "marco-2021",
        "assets": assets,
        "files": files,
    }
    config = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    totals = check(manifest, config)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "files": len(files),
                "totals": totals,
                "asset_bytes": {a["name"]: a["size_bytes"] for a in assets},
            }
        ),
        flush=True,
    )
    return manifest


if __name__ == "__main__":
    package()
