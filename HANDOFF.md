# Continuidad de Censo Vivo Ecuador

## Estado

- Fase actual: **2 terminada y desplegada**. Los [PR #48](https://github.com/diegocevallos-tech/censo-vivo-ecuador/pull/48), [#49](https://github.com/diegocevallos-tech/censo-vivo-ecuador/pull/49) y [#50](https://github.com/diegocevallos-tech/censo-vivo-ecuador/pull/50) se fusionaron en ese orden con squash, cada uno tras rebase sobre `main` y CI verde. La auditoría independiente [#46](https://github.com/diegocevallos-tech/censo-vivo-ecuador/pull/46) sigue en borrador y su rama no se toca.
- [Producción](https://diegocevallos-tech.github.io/censo-vivo-ecuador/) tiene 2B mediante el [deploy 36211854596](https://github.com/diegocevallos-tech/censo-vivo-ecuador/actions/runs/36211854596). El Release público vigente es [`data-derived-v2a`](https://github.com/diegocevallos-tech/censo-vivo-ecuador/releases/tag/data-derived-v2a), 436.512.440 bytes. Los datos pesados permanecen fuera de Git.
- Subtarea actual: documentación y capturas del smoke de producción en la rama `docs/fase-2-smoke`; después, PR `fix/1b2-auditoria`, agregado cantonal de Emigración en el próximo Release y tag `fase-2`.

## Pasos terminados

1. Unión por clave de conteos CPV 2022 y Marco 2021: 24 provincias, 221 cantones, 1.042 parroquias, 52.864 sectores y 209.373 manzanas con geometría y conteo. Las 1.852 manzanas sin polígono permanecen en el sector.
2. Tippecanoe v2.79.0 generó 52 PMTiles, total 154.511.848 bytes; máximo por archivo 14.637.118 bytes. Fuentes GeoJSONL agregadas y tiles se generaron en un Codespace de 4 CPU, 16 GB RAM, 32 GB de almacenamiento y se trasladaron localmente; no entraron al historial Git.
3. Chunks binarios por provincia: 64.162.668 bytes. [`06_qa_chunks.py`](pipeline/06_qa_chunks.py) comparó población y jefatura femenina de 48 chunks y 284.977 unidades con los Parquet.
4. Paquete `data-derived-v1b` preparado: conteos y Parquet 149.130.353 bytes, tiles 154.511.848, chunks 64.162.668, total de datos 367.804.869. Manifest y cuatro tar.gz con SHA256 ya generados localmente. QA aditiva de conteos: diferencia cero; 11 tests Python y 4 TypeScript pasan.
5. Mapa mínimo multinivel renderizado en prueba local; se corrigió el worker de MapLibre v6. CARTO Dark Matter respondió «API key required», por lo que se usa fondo oscuro propio. [Captura](docs/qa/fase1b3_mapa.png) e [informe](docs/fase1b3_report.md).
6. Release público publicado con cuatro tar.gz. Se descargó de nuevo y se restauraron 341 archivos con SHA256 coincidente; la QA aditiva completa, incluidas categorías y 96 chunks de conteo/análisis, pasó. El verificador de artefactos ahora extrae el esquema desde el AST sin depender de DuckDB en el runner.
7. [Deploy de producción](https://github.com/diegocevallos-tech/censo-vivo-ecuador/actions/runs/36185327073) exitoso tras permitir la rama exacta de 1B-3 en el environment `github-pages` (manteniendo `main`). Pages devuelve HTTP 206 y rango correcto para PMTiles y Parquet al pedir `Accept-Encoding: identity`. El navegador recorrió todos los niveles sin errores; [captura](docs/qa/fase1b3_pages.png).
8. [PR #48](https://github.com/diegocevallos-tech/censo-vivo-ecuador/pull/48) abierto. Su primer CI detectó que el runner no instalaba NumPy para `06_qa_chunks.py`; se añadió a las dependencias de CI. Verificar el nuevo run. La autorización vigente permite continuar con 2A y 2B en PRs separados y apilados.
9. El PR #48 tiene los checks `build` y `checks` en verde tras incluir NumPy y Pandas. En 2A, `09_indicator_map_index.py` evaluó los 45 indicadores sobre 286.265 unidades oficiales y produjo 52 binarios (68.704.172 bytes). `09_qa_indicator_map.py` validó sus claves, longitudes y estados. [Release v2a](https://github.com/diegocevallos-tech/censo-vivo-ecuador/releases/tag/data-derived-v2a) publicado y restaurado con SHA256: 394 archivos, 436.512.440 bytes; chunks 132.870.239/150.000.000 bytes.
10. El visor 2A integra búsqueda territorial, breadcrumb, catálogo de 45 indicadores, `min_level`, coropleta con tres métodos de corte, estado URL y ES/EN. [Prueba de navegador y captura](docs/fase2a_report.md) sin errores. Ruff, 8 tests TypeScript y build pasaron. [PR #49](https://github.com/diegocevallos-tech/censo-vivo-ecuador/pull/49) abierto; [preview CI](https://github.com/diegocevallos-tech/censo-vivo-ecuador/actions/runs/36193870442) compiló y verificó el Release v2a sin publicar en producción.
11. El visor 2B suma clic, multiselección, círculo con controles y lazo; vista previa con KDBush, ponderación por área solo para unidades cortadas, panel con pirámide nacional, distribución por sexo, fichas de indicadores y percentiles elegibles. Se añadió ESLint a CI. [Informe y pruebas](docs/fase2b_report.md): clic exacto en manzana, círculos y lazos a zoom 14,3, móvil y 3D sin errores JavaScript. El p95 de cálculo por cuadro fue 0,40 ms Quito, 0,30 ms Guayaquil y 0,40 ms Cuenca en Chromium de escritorio. El Release v2a no cambia.
12. [PR #50](https://github.com/diegocevallos-tech/censo-vivo-ecuador/pull/50) creado con base 2A; checks de CI iniciados. La rama 2B se publicó sin blobs nuevos mayores de 1 MB. El sitio en producción sigue en 1B-3.
13. Los dos checks de #50 pasaron (build devcontainer 4 min 13 s; checks públicos 58 s). Se detectó una ausencia en áreas rurales sin manzanas: a zoom fino la vista estaba vacía. Se añadió fallback a sector cuando no hay ninguna manzana visible después de cargar los tiles; se probó clic exacto en Morona Santiago a zoom 14,3 y sin errores JavaScript. Los cambios se están verificando nuevamente en CI.
14. #48, #49 y #50 fueron rebasados sobre `main` y fusionados por squash tras CI verde. #49 se reabrió después de que GitHub lo cerrara al borrar la rama base de #48; se retargeteó a `main`, se verificó y fusionó. #50 se retargeteó antes de borrar la rama base de #49. Las ramas de fase se borraron.
15. [Deploy 36211854596](https://github.com/diegocevallos-tech/censo-vivo-ecuador/actions/runs/36211854596) exitoso. El [smoke de producción](docs/fase2_smoke_produccion.md) recorrió seis niveles, tres círculos, lazo, multiselección, 30 indicadores y URL compartida sin errores de consola; primera carga 487.698 bytes. Lighthouse escritorio: rendimiento 91, accesibilidad 94, LCP 1,26 s. Móvil: 47, 94, 4,89 s. La brecha móvil está en la [issue #51](https://github.com/diegocevallos-tech/censo-vivo-ecuador/issues/51).
16. La auditoría [#46](https://github.com/diegocevallos-tech/censo-vivo-ecuador/pull/46) concluye «aprobar con correcciones»: Queen, 999 permutaciones, topología fija, seis índices canónicos, 16 grupos y gemelos a parroquia/cantón. No existe todavía el PR `fix/1b2-auditoria`. El agregado cantonal de Emigración se ensayó desde el Parquet parroquial agregado: 32.123 filas, 46.081 bytes, 124.992 emigrantes en ambos niveles.

## Siguiente comando exacto

```sh
git add HANDOFF.md docs/fase2_smoke_produccion.md docs/capturas web/scripts/smoke-production.mjs
```

Crear el PR de documentación del smoke y verificar CI. Luego abrir `fix/1b2-auditoria` sin tocar `feat/auditoria-1b2`; preparar el agregado cantonal en el siguiente Release y taguear `fase-2` desde el `main` documentado.

## Archivos tocados en 1B-3

- `HANDOFF.md`, `data/DERIVED_MANIFEST.json`
- `pipeline/06_tiles.py`, `06_chunks.py`, `06_aux_binary.py`, `06_package_v1b.py`, `06_qa_chunks.py`, `verify_public_artifacts.py`
- `.github/workflows/ci.yml`, `.github/workflows/deploy.yml`
- `web/src/main.ts`, `web/src/map.ts`, `web/src/style.css`, `web/src/vite-env.d.ts`
- `README.md`, `docs/schema.md`, `docs/data-access.md`, `docs/fase1b3_report.md`, `docs/qa/fase1b3_mapa.png`, `docs/qa/fase1b3_pages.png`
- 2A: `pipeline/09_indicator_map_index.py`, `09_places.py`, `09_package_v2a.py`, `09_qa_indicator_map.py`, `pipeline/verify_public_artifacts.py`, `web/src/indicatorMaps.ts`, `map.ts`, `style.css`, `web/src/generated/places.json`, `docs/fase2a_report.md`, `docs/qa/fase2a_mapa.png`, `data/DERIVED_MANIFEST.json`.
- 2B: `.github/workflows/ci.yml`, `pipeline/10_national_profile.py`, `web/package.json`, `web/package-lock.json`, `web/eslint.config.mjs`, `web/src/map.ts`, `selection.ts`, `countChunks.ts`, `analysisPanel.ts`, `style.css`, `web/src/generated/nationalProfile.json`, `docs/fase2b_report.md`, `docs/qa/fase2b_mapa.png`, `docs/qa/fase2b_movil.png`.
- Smoke producción: `docs/fase2_smoke_produccion.md`, `docs/capturas/`, `web/scripts/smoke-production.mjs`, `HANDOFF.md`.

## Decisiones pendientes

- La distancia al pico temporal del bono demográfico sigue diferida a la Fase 5 opcional. Cobertura de seguro de salud sigue descartada por variable inexistente.
- La capa de fondo oscuro usa un color propio hasta encontrar un basemap externo sin token que permita uso en producción. El mapa censal no depende de un proveedor externo.
- La optimización móvil queda en la issue #51, con Lighthouse 47 y LCP 4,89 s frente a la meta ≥85 y <3 s.
- Validar 60 fps de extremo a extremo en móviles y provincias densas antes de afirmar el criterio nacional; el p95 KDBush de escritorio mide solo el cálculo de la vista previa.
