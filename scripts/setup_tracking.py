"""Create the GitHub milestones, labels and planning issues for Censo Vivo.

Run from a checkout with ``gh`` authenticated as the repository owner. The
script checks existing objects before creating them, so it is safe to rerun.
"""

from __future__ import annotations

import json
import subprocess

REPO = "diegocevallos-tech/censo-vivo-ecuador"


def gh(method: str, endpoint: str, payload: dict | None = None) -> object:
    command = ["gh", "api", "-X", method, f"repos/{REPO}/{endpoint}"]
    if payload is not None:
        command.extend(["--input", "-"])
    result = subprocess.run(
        command,
        input=json.dumps(payload) if payload is not None else None,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


LABELS = {
    "phase:0": ("5319e7", "Repositorio, fuentes y validación"),
    "phase:1": ("1d76db", "Pipeline e índices"),
    "phase:2": ("0e8a16", "Núcleo del visor"),
    "phase:3": ("fbca04", "Módulos innovadores"),
    "phase:4": ("d93f0b", "Calidad y despliegue"),
    "phase:5": ("c5def5", "Cambio intercensal opcional"),
    "blocked:data": ("b60205", "Pendiente de una fuente oficial verificable"),
}

MILESTONES = {
    i: (
        [
            "Fase 0 · Repositorio, entorno y datos",
            "Fase 1 · Pipeline e índices",
            "Fase 2 · Núcleo del visor",
            "Fase 3 · Módulos innovadores",
            "Fase 4 · Calidad, documentación y despliegue",
            "Fase 5 · Cambio intercensal opcional",
        ][i]
    )
    for i in range(6)
}


def item(phase: int, title: str, tasks: list[str]) -> tuple[int, str, str]:
    return phase, title, "\n".join(f"- [ ] {task}" for task in tasks)


ISSUES = [
    item(0, "0.1 · Repositorio y gobernanza", ["Cuenta y repositorio público verificados", "Topics, licencias y labels", "Milestones e issues de planificación", "main protegido; cambios por PR"]),
    item(0, "0.2 · Estructura del proyecto", ["Devcontainer y workflows", "Directorios de datos, pipeline, web y docs", "Ignorar datos crudos e intermedios en git"]),
    item(0, "0.3 · Entorno y herramientas", ["Python 3.11 y dependencias GIS/QA", "Node 20 y dependencias web", "Binarios duckdb, tippecanoe, pmtiles y mapshaper"]),
    item(0, "0.4 · Fuentes oficiales", ["Microdatos CSV MANZANA de las cinco bases; diccionario y guía", "Cartografía 2022 de todos los niveles", "Registrar fuentes opcionales OSM y CPV 2010", "Documentar cualquier bloqueo de descarga sin inventar datos"]),
    item(0, "0.5 · Release reproducible de originales", ["Subir originales a data-raw-v1, con archivos ≤2 GiB", "MANIFEST con URL, fecha, bytes y SHA256", "fetch_raw.py descarga del Release y verifica checksums"]),
    item(0, "0.6 · Validación de fuentes", ["Muestras y encabezados con DuckDB", "Matriz de variables confirmada en diccionario", "Match cartográfico de manzanas y sectores >95% por provincia", "Reporte fase 0 y PR"]),
    item(1, "1.1 · Filtrar microdatos a Parquet", ["01_filter_to_parquet.py reproducible", "Excluir identificadores personales del producto publicado"]),
    item(1, "1.2 · Conteos por unidad y roll-up", ["02_counts_by_unit.py", "Pirámide de 21 grupos × sexo", "Conteos de categorías disponibles", "Aditividad verificada"]),
    item(1, "1.3 · Catálogo e índices", ["indicators.yaml con metadatos y referencias", "03_indicators.py", "Paridad Python/TypeScript y reglas n mínimo/EB"]),
    item(1, "1.4 · Geodemografía", ["04_geodemographics.py", "Selección de k y clusters.json", "Retratos y documentación"]),
    item(1, "1.5 · Estadística espacial", ["05_spatial_stats.py", "Moran/LISA, disimilitud y perfiles de gemelos"]),
    item(1, "1.6 · Tiles y formatos de consulta", ["06_tiles.py", "PMTiles, chunks binarios y Parquet por nivel", "Total de sitio <900 MB o propuesta de opciones"]),
    item(1, "1.7 · QA y CI del pipeline", ["07_qa.py con totales oficiales <0,5%", "data-interim-v1", "workflow_dispatch regenera y abre PR"]),
    item(2, "2.1 · Mapa multiescala y navegación", ["Basemap Dark Matter", "Zoom automático por nivel y breadcrumb", "Buscador de lugares"]),
    item(2, "2.2 · Indicadores y coropletas", ["Selector agrupado y buscable", "Cuantiles, Jenks y desviación estándar", "Leyendas y estado en URL"]),
    item(2, "2.3 · Selección espacial", ["Círculo con dos handles, lazo, clic y multiselección", "Agregación en vivo y recálculo ponderado", "Mostrar solo unidades seleccionadas; medir 60 fps"]),
    item(2, "2.4 · Paneles analíticos", ["Donut, pirámide, barras e índices", "Percentiles, n pequeño y suavizado", "Chips temáticos activos en #F5B82E"]),
    item(2, "2.5 · Controles y accesibilidad", ["Controles inferiores, densidad y 3D", "ES/EN y móvil con bottom-sheet", "Accesibilidad AA y capturas del PR"]),
]

MODULES = [
    "Skyline demográfico", "Mapa de puntos por densidad", "Constructor bivariado",
    "Gemelo censal", "Comparador A/B", "Geodemografía", "Mapa de la diáspora",
    "Flujos internos", "Hot spots LISA", "Si esta zona fueran 100 personas",
    "Beeswarm comparativo", "Laboratorio SQL", "Historias scrollytelling",
    "Ficha de lugar", "Sonificación accesible", "Descarga de selección",
]
for number, name in enumerate(MODULES, 1):
    ISSUES.append(item(3, f"3.{number:02d} · {name}", [
        "Implementar solo con variables oficiales verificadas",
        "Documentar método y limitaciones",
        "Incluir en el PR del bloque de cuatro módulos y esperar aprobación",
    ]))

ISSUES.extend([
    item(4, "4.1 · CI integral", ["ruff, pytest, eslint y vitest", "Playwright e2e para selección, gemelo, comparador y SQL"]),
    item(4, "4.2 · Despliegue GitHub Pages", ["deploy.yml", "Sitio ≤1 GB, archivos <100 MB", "Verificar CORS y HTTP range"]),
    item(4, "4.3 · Rendimiento móvil", ["Lighthouse ≥85", "Carga inicial 4G <3 s"]),
    item(4, "4.4 · Documentación bilingüe", ["README ES/EN y GIF", "Diagrama, reproducibilidad, catálogo, límites y créditos", "Metodología generada desde indicators.yaml"]),
    item(4, "4.5 · Release de producto", ["v1.0.0 con changelog", "PR al README de perfil si existe"]),
    item(5, "5.1 · Cambio intercensal 2010–2022", ["Verificar fuentes y equivalencias parroquiales", "Índices de cambio", "Slider antes/después", "PR independiente"]),
])


def main() -> None:
    existing_labels = {entry["name"] for entry in gh("GET", "labels?per_page=100")}
    for name, (color, description) in LABELS.items():
        if name not in existing_labels:
            gh("POST", "labels", {"name": name, "color": color, "description": description})

    existing_milestones = {
        entry["title"]: entry["number"]
        for entry in gh("GET", "milestones?state=all&per_page=100")
    }
    for title in MILESTONES.values():
        if title not in existing_milestones:
            milestone = gh("POST", "milestones", {"title": title})
            existing_milestones[title] = milestone["number"]

    existing_issues = {
        entry["title"] for entry in gh("GET", "issues?state=all&per_page=100")
        if "pull_request" not in entry
    }
    for phase, title, body in ISSUES:
        if title not in existing_issues:
            gh("POST", "issues", {
                "title": title,
                "body": body,
                "labels": [f"phase:{phase}"],
                "milestone": existing_milestones[MILESTONES[phase]],
            })
            print(f"Created: {title}")


if __name__ == "__main__":
    main()
