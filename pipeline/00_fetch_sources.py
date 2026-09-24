"""Download official INEC source files locally and record size and SHA256.

Raw archives remain gitignored. This script does not publish source data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "data" / "MANIFEST.json"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
BASE = "https://www.ecuadorencifras.gob.ec/documentos/web-inec"
SOURCES = {
    "cpv2022_manloc_csv": {
        "url": f"{BASE}/bd-censo/manzana/BDD_CPV2022_MANLOC_CSV.zip",
        "filename": "BDD_CPV2022_MANLOC_CSV.zip",
        "classification": "person_or_household_microdata",
        "required": True,
    },
    "cpv2022_dictionary_manloc": {
        "url": f"{BASE}/dicc-censo/2022/DICCIONARIO_BDD_MANLOC.xlsx",
        "filename": "DICCIONARIO_BDD_MANLOC.xlsx",
        "classification": "documentation",
        "required": True,
    },
    "cpv2022_dictionary_sector": {
        "url": f"{BASE}/dicc-censo/2022/DICCIONARIO_BDD_SECTOR.xlsx",
        "filename": "DICCIONARIO_BDD_SECTOR.xlsx",
        "classification": "documentation",
        "required": True,
    },
    "cpv2022_guide": {
        "url": "https://www.censoecuador.gob.ec/wp-content/uploads/2024/12/"
        "GUIA_BASE_CPV_2022.pdf",
        "filename": "GUIA_BASE_CPV_2022.pdf",
        "classification": "documentation",
        "required": True,
    },
    "cpv2022_guide_v6": {
        "url": f"{BASE}/bd-censo/5.GUIA_BASE_CPV_2022_v6.pdf",
        "filename": "5.GUIA_BASE_CPV_2022_v6.pdf",
        "classification": "documentation",
        "required": False,
    },
    "cartography_sectors_anonymized": {
        "url": f"{BASE}/capa/CapaSectores.zip",
        "filename": "CapaSectores.zip",
        "classification": "geometry",
        "required": True,
    },
    "cartography_geodatabase_2021_backup": {
        "url": f"{BASE}/Geografia_Estadistica/Documentos/GEODATABASE_NACIONAL_2021.zip",
        "filename": "GEODATABASE_NACIONAL_2021.zip",
        "classification": "geometry_prior_year",
        "required": False,
    },
    "cartography_classifier_2022": {
        "url": f"{BASE}/Cartografia/Clasificador_Geografico/"
        "CLASIFICADOR%20GEOGRAFICO_2022.zip",
        "filename": "CLASIFICADOR_GEOGRAFICO_2022.zip",
        "classification": "geographic_classifier",
        "required": False,
    },
}


def source_length(session: requests.Session, url: str) -> int | None:
    response = session.get(url, headers={"Range": "bytes=0-0"}, stream=True, timeout=60)
    response.raise_for_status()
    if response.status_code == 206:
        match = re.fullmatch(r"bytes 0-0/(\d+)", response.headers.get("Content-Range", ""))
        response.close()
        return int(match.group(1)) if match else None
    response.close()
    return None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download(session: requests.Session, source: dict) -> dict:
    RAW.mkdir(parents=True, exist_ok=True)
    path = RAW / source["filename"]
    expected = source_length(session, source["url"])
    partial = path.with_suffix(path.suffix + ".part")
    if path.exists() and expected is not None and path.stat().st_size == expected:
        pass
    else:
        for attempt in range(3):
            offset = partial.stat().st_size if partial.exists() else 0
            headers = {"Range": f"bytes={offset}-"} if offset else {}
            try:
                with session.get(source["url"], headers=headers, stream=True, timeout=120) as response:
                    response.raise_for_status()
                    if offset and response.status_code != 206:
                        offset = 0
                    mode = "ab" if offset else "wb"
                    with partial.open(mode) as stream:
                        for block in response.iter_content(chunk_size=8 * 1024 * 1024):
                            if block:
                                stream.write(block)
                break
            except (requests.RequestException, OSError):
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
        if expected is not None and partial.stat().st_size != expected:
            raise ValueError(
                f"Incomplete {source['filename']}: {partial.stat().st_size} of {expected} bytes"
            )
        partial.replace(path)
    return {
        **source,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "size_bytes": path.stat().st_size,
        "sha256": sha256(path),
        "published_to_public_release": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="*", choices=tuple(SOURCES))
    parser.add_argument("--required", action="store_true", help="Download every required source")
    args = parser.parse_args()
    selected = list(args.source)
    if args.required:
        selected.extend(name for name, source in SOURCES.items() if source["required"])
    if not selected:
        parser.error("Select source IDs or --required")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    sources = {entry["id"]: entry for entry in manifest["sources"]}
    for source_id in dict.fromkeys(selected):
        print(f"Fetching {source_id}...", flush=True)
        sources[source_id] = {"id": source_id, **download(session, SOURCES[source_id])}
        manifest["sources"] = list(sources.values())
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Verified {source_id}: {sources[source_id]['size_bytes']} bytes", flush=True)


if __name__ == "__main__":
    main()
