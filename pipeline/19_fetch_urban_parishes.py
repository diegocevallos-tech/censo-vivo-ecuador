"""Fetch unmodified municipal urban-parish GeoJSON from six official services.

The downloaded files stay under ignored data/raw. The versioned manifest records
the exact response checksum so spatial processing can be reproduced and audited.
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/municipal_urban"
MANIFEST = ROOT / "data/MUNICIPAL_SOURCES.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CensoVivoEcuador/1.0)"}

SOURCES = {
    "quito": {
        "city": "Quito", "canton_key": "1701", "census_parish": "170150",
        "kind": "arcgis", "crs": "EPSG:4326", "features": 60,
        "url": "https://geoquito.quito.gob.ec/server/rest/services/Hosted/"
               "parroquias_ref_a/FeatureServer/0/query",
        "name_field": "dpa_despar", "code_field": "dpa_parroq",
    },
    "guayaquil": {
        "city": "Guayaquil", "canton_key": "0901", "census_parish": "090150",
        "kind": "arcgis", "crs": "EPSG:4326", "features": 16,
        "url": "https://geoportalcat.guayaquil.gob.ec/arcgis/rest/services/"
               "Geoportal_Actualizado/GEOPORTAL_ACTUALIZADO/MapServer/9/query",
        "name_field": "Nam", "code_field": None,
    },
    "cuenca": {
        "city": "Cuenca", "canton_key": "0101", "census_parish": "010150",
        "kind": "wfs", "crs": "EPSG:32717", "features": 15,
        "url": "https://ide.cuenca.gob.ec/geoserver/wfs?service=WFS&version=1.0.0"
               "&request=GetFeature&typeName=dgpt_limites:limite_parroquias_urbanas"
               "&outputFormat=application/json",
        "name_field": "parroquias", "code_field": None,
    },
    "loja": {
        "city": "Loja", "canton_key": "1101", "census_parish": "110150",
        "kind": "wfs", "crs": "EPSG:32717", "features": 6,
        "url": "http://sil.loja.gob.ec/geoserver/wfs?service=WFS&version=1.0.0"
               "&request=GetFeature&typeName=pugs_2023_2033:"
               "limites_parroquias_urbanas_2023_2033&outputFormat=application/json",
        "name_field": "parroquia", "code_field": "cod_parroq",
    },
    "ambato": {
        "city": "Ambato", "canton_key": "1801", "census_parish": "180150",
        "kind": "arcgis", "crs": "EPSG:4326", "features": 8,
        "url": "https://arcgis.ambato.gob.ec/mapas/rest/services/MXD/AMBATO/"
               "MapServer/1/query",
        "name_field": "PARROQUIA", "code_field": "CODIGO",
    },
    "riobamba": {
        "city": "Riobamba", "canton_key": "0601", "census_parish": "060150",
        "kind": "arcgis", "crs": "EPSG:4326", "features": 5,
        "url": "https://services9.arcgis.com/WR0heBS35BiLFAuA/arcgis/rest/services/"
               "parroquias_urbanas/FeatureServer/0/query",
        "name_field": "PARROQUIA", "code_field": None,
    },
}


def fetch(source: dict) -> tuple[bytes, str]:
    params = None
    if source["kind"] == "arcgis":
        params = {"where": "1=1", "outFields": "*", "returnGeometry": "true",
                  "f": "geojson", "outSR": "4326", "resultOffset": 0,
                  "resultRecordCount": 2000}
    for attempt in range(1, 6):
        try:
            response = requests.get(source["url"], params=params, headers=HEADERS,
                                    timeout=45)
            response.raise_for_status()
            document = response.json()
            features = document.get("features")
            if document.get("type") != "FeatureCollection" or not isinstance(features, list):
                raise ValueError(f"Unexpected response: {str(document.get('error'))[:150]}")
            if len(features) != source["features"]:
                raise ValueError(f"Expected {source['features']} features, got {len(features)}")
            if any(feature.get("geometry") is None for feature in features):
                raise ValueError("Null municipal geometry")
            return response.content, response.url
        except (requests.RequestException, ValueError) as exc:
            print(f"{source['city']} attempt {attempt}/5: {exc}", flush=True)
            if attempt == 5:
                raise
            time.sleep(min(2 ** (attempt - 1), 16))
    raise AssertionError("Unreachable")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    rows = []
    for slug, source in SOURCES.items():
        payload, resolved_url = fetch(source)
        path = RAW / f"{slug}.geojson"
        path.write_bytes(payload)
        row = {**source, "file": path.relative_to(ROOT).as_posix(),
               "resolved_url": resolved_url, "size_bytes": len(payload),
               "sha256": hashlib.sha256(payload).hexdigest()}
        rows.append(row)
        print(f"{source['city']}: {source['features']} geometries, {len(payload)} bytes",
              flush=True)
    MANIFEST.write_text(json.dumps({"captured_at_utc": datetime.now(UTC).isoformat(),
                                    "sources": rows}, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")


if __name__ == "__main__":
    main()
