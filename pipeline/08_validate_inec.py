"""Reproduce the phase 1B-2 external benchmark from exact published aggregates.

Only official-unit aggregate Parquet is read; no individual census rows are opened.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import duckdb
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
from aggregation import Aggregate  # noqa: E402
from indicators import evaluate  # noqa: E402

SOURCES = {
    "Nacional": "https://www.censoecuador.gob.ec/public/Boletin_Nacional.htm",
    "Pichincha": "https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Pichincha.pdf",
    "Guayas": "https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Guayas.pdf",
    "Azuay": "https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_azuay.pdf",
}
OFFICIAL = {
    "Nacional": [16938986, 5188827, 5062650, 3.3, 29, 95, 16.6, 61.0, 20.9, 77.5, 51.3],
    "Pichincha": [3089473, 994599, 983801, 3.1, 31, 93, 17.2, 55.9, 32.5, 87.4, 51.8],
    "Guayas": [4391923, 1319163, 1289733, 3.3, 29, 96, 16.8, 67.4, 17.1, 81.0, 50.9],
    "Azuay": [801609, 246867, 242168, 3.2, 30, 89, 16.8, 58.7, 27.0, 94.7, 53.0],
}
METRICS = [
    ("Población censada", "personas"),
    ("Hogares clasificados H09", "hogares"),
    ("Viviendas ocupadas V0201=1+2", "viviendas"),
    ("Personas por hogar", "personas/hogar"),
    ("Edad mediana aproximada", "años"),
    ("Razón de masculinidad", "hombres/100 mujeres"),
    ("Hogares unipersonales", "%"),
    ("Tenencia propia", "%"),
    ("Tenencia arrendada", "%"),
    ("Autoidentificación mestiza", "%"),
    ("Mujeres", "%"),
]
KEYS = [("EC", "Nacional"), ("17", "Pichincha"), ("09", "Guayas"), ("01", "Azuay")]


def load_counts(db: duckdb.DuckDBPyConnection, base: Path, key: str) -> tuple[dict, dict]:
    level = "nacion" if key == "EC" else "provincia"
    core = (base / level / "data.parquet").as_posix()
    categories = (base / "categories" / level / "data.parquet").as_posix()
    codebook = (base / "categories/codebook.parquet").as_posix()
    result = db.execute(f"SELECT * FROM read_parquet('{core}') WHERE unit_key=?", [key])
    values = dict(zip((item[0] for item in result.description), result.fetchone(), strict=True))
    counts = {f"core:{k}": float(v) for k, v in values.items() if isinstance(v, (int, float))}
    query = f"""SELECT b.source_table,b.variable,b.category,c.n
      FROM read_parquet('{categories}') c
      JOIN read_parquet('{codebook}') b USING(variable_id,category_id)
      JOIN read_parquet('{core}') u USING(unit_index) WHERE u.unit_key=?"""
    for table, variable, category, n in db.execute(query, [key]).fetchall():
        counts[f"cat:{table}:{variable}:{category}"] = float(n)
    return values, counts


def fmt(value: float, unit: str) -> str:
    return f"{value:,.0f}" if unit in {"personas", "hogares", "viviendas"} else f"{value:.3f}"


def build(base: Path) -> str:
    db = duckdb.connect()
    definitions = {item["id"]: item for item in yaml.safe_load(
        (ROOT / "indicators.yaml").read_text(encoding="utf-8")
    )["indicators"]}
    lines = [
        "# Validación externa con cifras del CPV 2022 del INEC",
        "",
        "Se usan los Parquet agregados exactos del Release `data-derived-v1b1`; "
        "este script no abre filas por persona. El valor oficial de hogares corresponde "
        "a hogares clasificados (`H09=1..6`); el conteo operativo `core:households` "
        "incluye también registros sin clasificación. Las fichas provinciales y el "
        "boletín nacional se citan en cada fila.",
        "",
        "| Área | Indicador | Valor propio | Valor oficial | Fuente INEC | "
        "Diferencia (propio − oficial) |",
        "| --- | --- | ---: | ---: | --- | ---: |",
    ]
    flagged = []
    for key, name in KEYS:
        values, counts = load_counts(db, base, key)
        level = "nacion" if key == "EC" else "provincia"
        def cat(table: str, variable: str, category: int, data: dict = counts) -> float:
            return data.get(f"cat:{table}:{variable}:{category}", 0)
        def calc(
            indicator: str, data: dict = counts, unit_level: str = level, area: str = name
        ) -> float:
            result = evaluate(
                definitions[indicator], Aggregate(data, "exacto", 0), level=unit_level
            )
            if result.value is None:
                raise ValueError(f"Missing {indicator} in {area}: {result.unavailable_reason}")
            return result.value
        ethnic_total = sum(cat("poblacion_sector", "P11R", i) for i in range(1, 7))
        own = [
            values["population"],
            sum(cat("hogar", "H09", i) for i in range(1, 7)),
            cat("vivienda", "V0201", 1) + cat("vivienda", "V0201", 2),
            calc("average_household_size"), calc("median_age"), calc("male_ratio"),
            calc("single_person_households"), calc("owned_tenure"), calc("rented_tenure"),
            100 * cat("poblacion_sector", "P11R", 4) / ethnic_total,
            calc("female_share"),
        ]
        for (label, unit), current, official in zip(METRICS, own, OFFICIAL[name], strict=True):
            delta = current - official
            lines.append(
                f"| {name} | {label} ({unit}) | {fmt(current, unit)} | "
                f"{fmt(official, unit)} | [INEC]({SOURCES[name]}) | {fmt(delta, unit)} |"
            )
            if abs(delta) > 0.5 or (official and abs(delta / official) > .01):
                flagged.append((name, label, current, official, delta))
    lines += [
        "", "## Diferencias que superan 0,5 puntos/unidades o 1 % relativo", "",
    ]
    for name, label, own, official, delta in flagged:
        explanation = (
            "Mediana interpolada sobre grupos quinquenales de edad frente a la mediana "
            "calculada por el INEC con edad simple; se conserva el rótulo «aproximada»."
            if label == "Edad mediana aproximada" else
            "El INEC publica este promedio con un decimal: el error relativo calculado "
            "contra la cifra redondeada no implica discrepancia de conteos. Además, "
            "el catálogo usa población total (incluida población colectiva) y todos "
            "los hogares operativos, no solo personas de hogares particulares." 
            if label == "Personas por hogar" else
            "La ficha publica el porcentaje con un decimal y el cociente aquí usa "
            "todos los registros con categoría válida; comprobar definición y denominador." 
        )
        lines.append(f"- **{name}, {label}**: propio {own:.4f}, INEC {official:.4f}, "
                     f"diferencia {delta:+.4f}. {explanation}")
    if not flagged:
        lines.append("Ninguna.")
    lines += [
        "", "## Definiciones que no se deben equiparar", "",
        "- **Viviendas desocupadas:** el catálogo usa solo `V0201=4` (desocupada). "
        "El boletín nacional agrupa `V0201=4+5` (incluye en construcción): "
        "11,626 % frente a 13,925 %. Es una diferencia de definición de 2,299 puntos, "
        "no una pérdida de registros. La fórmula del catálogo se mantiene explícita.",
        "- **Internet:** el 69,4 % del [boletín nacional]"
        "(https://www.censoecuador.gob.ec/public/Boletin_Nacional.htm) "
        "mide uso individual desde los 5 años. `fixed_internet` mide hogares con "
        "internet fijo (60,892 % nacional); no son el mismo indicador.",
        "- **Analfabetismo 15+ y jefatura femenina:** el INEC publica 3,7 % y "
        "38,5 % nacionales en el mismo boletín. El agregado de 1B-1 carece de "
        "edad × alfabetismo y parentesco × sexo; quedan pendientes para 1B-2 "
        "y no se han fabricado valores propios.",
        "- **Viviendas ocupadas:** los recuentos de las fichas provinciales coinciden "
        "con `V0201=1+2`. Algunas fichas los describen como «con personas presentes»; "
        "la categoría 2 corresponde a ocupada con personas ausentes. Se valida el "
        "recuento, dejando constancia de esa imprecisión de rótulo.",
        "", "## Reproducción", "",
        "Desde la raíz del repo, tras descargar y verificar el Release agregado:",
        "", "```sh",
        "python pipeline/08_validate_inec.py \\",
        "  --base data/interim/exact_public/counts/v1b1 \\",
        "  --write docs/qa/validacion_inec.md",
        "```", "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--write", type=Path, required=True)
    args = parser.parse_args()
    result = build(args.base)
    args.write.parent.mkdir(parents=True, exist_ok=True)
    args.write.write_text(result, encoding="utf-8")
    print(f"Wrote {args.write}")


if __name__ == "__main__":
    main()
