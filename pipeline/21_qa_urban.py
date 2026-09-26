"""Check municipal-centroid aggregates and write the review report."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/interim/municipal_urban"
REPORT = ROOT / "docs/qa/parroquias_urbanas_resultados.md"


def main() -> None:
    manifest = json.loads((ROOT / "data/MUNICIPAL_SOURCES.json").read_text(encoding="utf-8"))
    for source in manifest["sources"]:
        raw = (ROOT / source["file"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != source["sha256"]:
            raise ValueError(f"Raw municipal checksum mismatch: {source['city']}")
    data = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
    boundaries = json.loads((OUT / "boundaries.geojson").read_text(encoding="utf-8"))
    counts = pq.read_table(OUT / "urban_counts.parquet").to_pandas()
    assignments = pq.read_table(OUT / "manzana_to_urban.parquet").to_pandas()
    parishes = data["parishes"]
    if len(parishes) != 81 or len(boundaries["features"]) != 81 or len(counts) != 81:
        raise ValueError("Expected 81 municipal urban parishes across six cities")
    if len(assignments) != len(assignments["manzana_key"].unique()):
        raise ValueError("A block was assigned to multiple municipal parishes")
    summary = {row["urban_id"]: row for row in parishes}
    if set(summary) != set(counts["urban_id"]) or set(summary) != {
        item["properties"]["urban_id"] for item in boundaries["features"]
    }:
        raise ValueError("Boundary/count/summary keys differ")
    for _, row in counts.iterrows():
        item = summary[row["urban_id"]]
        if any(int(row[field]) != item[field] for field in (
            "population", "dwellings", "households"
        )):
            raise ValueError(f"Count mismatch: {row['urban_id']}")
        if item["blocks"] != int((assignments["urban_id"] == row["urban_id"]).sum()):
            raise ValueError(f"Block count mismatch: {row['urban_id']}")
        if item["age_0_14"]:
            computed = 100 * item["age_65_plus"] / item["age_0_14"]
            if abs(computed - item["aging_index"]) > 1e-9:
                raise ValueError(f"Ageing index mismatch: {row['urban_id']}")
    for city in data["cities"]:
        if city["mapped_population"] + city["outside_population"] + city[
            "no_polygon_population"
        ] != city["official_census_parish_population"]:
            raise ValueError(f"Population balance failed: {city['city']}")
    inaquito = summary["municipal:quito:170112"]
    if inaquito["age_0_14"] < 30 or inaquito["age_65_plus"] < 30:
        raise ValueError("Iñaquito ageing denominator unexpectedly small")
    rows = []
    for city in data["cities"]:
        rows.append("| {city} | {municipal_parishes} | {blocks_assigned:,} / "
                    "{blocks_with_geometry:,} | {mapped_population:,} / "
                    "{official_census_parish_population:,} | {outside_population:,} | "
                    "{no_polygon_population:,} |".format(**city))
    source_rows = [f"- {item['city']}: [{item['url']}]({item['url']}) "
                   f"(SHA256 `{item['sha256']}`, {item['size_bytes']:,} B)."
                   for item in manifest["sources"]]
    content = """# Parroquias urbanas municipales · asignación por centroide

La geometría de referencia proviene de seis servicios oficiales de los GAD.
Cada manzana del Marco 2021 se asigna al polígono municipal que contiene su
centroide. Las estadísticas son sumas de agregados por manzana del CPV 2022;
**la parroquia urbana municipal no es una unidad censal del INEC**.
Las manzanas sin polígono siguen en su sector censal y no se adjudican a
ninguna parroquia urbana. Las manzanas fuera de los límites municipales
permanecen en su parroquia censal oficial.

| Ciudad | Parroquias | Manzanas / total | Población / cabecera | Fuera | Sin geometría¹ |
| --- | ---: | ---: | ---: | ---: | ---: |
""" + "\n".join(rows) + "\n\n" + f"""## Iñaquito

La fuente municipal identifica **Iñaquito (170112)**. El cruce asignó
**{inaquito['blocks']:,} manzanas** con **{inaquito['population']:,} personas**;
{inaquito['age_0_14']:,} tienen 0–14 años y {inaquito['age_65_plus']:,} tienen
65 años o más. El índice de envejecimiento es
**{inaquito['aging_index']:.2f} personas de 65+ por cada 100 de 0–14**
(100 × {inaquito['age_65_plus']:,} / {inaquito['age_0_14']:,}). Es un agregado
por centroides sobre un **límite no censal**, no una cifra oficial del INEC
para la parroquia urbana.

## QA y alcance

- **81 parroquias**: Quito 32, Guayaquil 15, Cuenca 15, Loja 6, Ambato 8 y
  Riobamba 5. Guayaquil devuelve 16 polígonos pero 15 nombres distintos;
  Tarqui tiene dos partes. El informe de fuentes dice 14 nombres únicos,
  discrepancia que aquí se corrige sin editar aquel documento.
- Ninguna manzana se asigna a dos polígonos. En cada ciudad, población asignada
  + fuera del límite + población sin geometría de manzana asignable = total
  oficial de la cabecera,
  **diferencia cero**. Los conteos por parroquia municipal coinciden con la
  tabla resumida; todos los SHA256 originales coinciden.
- ¹ «Sin geometría» incluye manzanas sin polígono y población que permanece
  solo en el sector disperso; no significa que todas sean manzanas sin match.
- La tabla manzana→parroquia municipal se conserva como intermedio privado.
  El navegador recibe únicamente geometrías de referencia y agregados por
  parroquia municipal. No se publican registros por persona.

## Fuentes verificadas

""" + "\n".join(source_rows) + "\n"
    REPORT.write_text(content, encoding="utf-8")
    print(json.dumps({"parishes": len(parishes), "assigned_blocks": len(assignments),
                      "inaquito_aging_index": inaquito["aging_index"]}))


if __name__ == "__main__":
    main()
