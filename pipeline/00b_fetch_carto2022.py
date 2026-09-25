"""Fetch the official INEC 2022 ArcGIS census layers page by page.

Each response is preserved verbatim under gitignored data/raw/. Failed and
successful HTTP attempts are recorded in docs/qa/carto2022_attempts.csv.
The fallback IDs below come from the official MapServer layer listing and
permit probing layer queries when the service root itself returns HTTP 500.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = (
    "https://idgn.ecuadorencifras.gob.ec/server/rest/services/Cartografia_Censal_WMS_2022/MapServer"
)
LOG = ROOT / "docs/qa/carto2022_attempts.csv"
RAW = ROOT / "data/raw/carto2022"
USER_AGENT = "Mozilla/5.0 (compatible; CensoVivoEcuador/0.1; source verification)"
FALLBACK_LAYERS = {
    "parroquia": 2,
    "zona": 3,
    "sector_disperso": 4,
    "sector_amanzanado": 5,
    "manzana": 6,
    "sector_censal": 7,
}


def log_attempt(
    run_id: str, stage: str, layer: str, attempt: int, status: str, detail: str
) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    is_new = not LOG.exists()
    with LOG.open("a", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        if is_new:
            writer.writerow(["run_utc", "stage", "layer", "attempt", "http_status", "detail"])
        writer.writerow([run_id, stage, layer, attempt, status, detail[:240]])


def get_json(
    path: str,
    params: dict[str, str | int],
    *,
    run_id: str,
    stage: str,
    layer: str,
    max_attempts: int,
    timeout: int,
) -> dict | None:
    url = f"{BASE}{path}?{urlencode(params)}"
    for attempt in range(1, max_attempts + 1):
        status = "network_error"
        try:
            with urlopen(
                Request(url, headers={"User-Agent": USER_AGENT}), timeout=timeout
            ) as response:
                status = str(response.status)
                document = json.load(response)
            if not isinstance(document, dict) or "error" in document:
                raise ValueError(f"ArcGIS response: {str(document)[:160]}")
            log_attempt(run_id, stage, layer, attempt, status, "ok")
            print(f"{layer} {stage}: HTTP {status} on attempt {attempt}", flush=True)
            return document
        except HTTPError as exc:
            status = str(exc.code)
            detail = exc.reason
        except (URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
            detail = str(exc)
        log_attempt(run_id, stage, layer, attempt, status, str(detail))
        print(f"{layer} {stage}: HTTP {status} attempt {attempt}/{max_attempts}", flush=True)
        if attempt < max_attempts:
            time.sleep(2 ** (attempt - 1))
    return None


def layer_ids(metadata: dict | None) -> dict[str, int]:
    if metadata is None:
        return FALLBACK_LAYERS.copy()
    found = {}
    for layer in metadata.get("layers", []):
        name = str(layer.get("name", "")).lower()
        identifier = layer.get("id")
        if not isinstance(identifier, int):
            continue
        if "manzana" in name:
            found["manzana"] = identifier
        elif "parroqui" in name:
            found["parroquia"] = identifier
        elif "zona" in name:
            found["zona"] = identifier
        elif "sector" in name:
            key = (
                "sector_disperso"
                if "dispers" in name
                else ("sector_amanzanado" if "amanzan" in name else "sector_censal")
            )
            found[key] = identifier
    return found


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--page-size", type=int, default=1000)
    args = parser.parse_args()
    if not 1 <= args.max_attempts <= 5 or args.timeout < 1 or args.page_size < 1:
        parser.error("Attempts must be 1..5 and timeout/page-size must be positive")
    run_id = datetime.now(UTC).isoformat()
    metadata = get_json(
        "",
        {"f": "json"},
        run_id=run_id,
        stage="metadata",
        layer="MapServer",
        max_attempts=args.max_attempts,
        timeout=args.timeout,
    )
    found = layer_ids(metadata)
    if not found:
        print("No required layers found in the official metadata", flush=True)
        return
    pages = 0
    for name, identifier in found.items():
        offset = 0
        while True:
            document = get_json(
                f"/{identifier}/query",
                {
                    "where": "1=1",
                    "outFields": "*",
                    "returnGeometry": "true",
                    "f": "geojson",
                    "resultOffset": offset,
                    "resultRecordCount": args.page_size,
                },
                run_id=run_id,
                stage="query",
                layer=name,
                max_attempts=args.max_attempts,
                timeout=args.timeout,
            )
            if document is None:
                break
            features = document.get("features")
            if document.get("type") != "FeatureCollection" or not isinstance(features, list):
                log_attempt(
                    run_id, "validation", name, 0, "invalid", "Not GeoJSON FeatureCollection"
                )
                break
            if not features:
                break
            RAW.mkdir(parents=True, exist_ok=True)
            target = RAW / f"{name}_{offset:09d}.geojson"
            payload = json.dumps(document, ensure_ascii=False).encode("utf-8")
            if len(payload) >= 2 * 1024**3:
                raise ValueError(f"Page exceeds the GitHub Release 2 GiB limit: {target}")
            target.write_bytes(payload)
            pages += 1
            if len(features) < args.page_size:
                break
            offset += len(features)
    print(f"Saved {pages} GeoJSON pages; attempts logged in {LOG}", flush=True)


if __name__ == "__main__":
    main()
