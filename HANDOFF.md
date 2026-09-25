# Continuidad de Censo Vivo Ecuador

## Estado

- Fase actual: **1B-3 · tiles y paquete web**, rama `feat/fase-1b3-tiles-paquete-web`. PR #45 fusionado por squash; tag `fase-1b2` publicado. La rama independiente `feat/auditoria-1b2` de Antigravity no se toca.
- Pages se habilitó con `build_type: workflow`, sin despliegue de producción aún. El usuario autorizó publicar el mapa mínimo en producción durante 1B-3.
- Los datos pesados están ignorados en `data/interim/` y `web/public/data/`. El manifiesto `data/DERIVED_MANIFEST.json` versionado apunta al Release público `data-derived-v1b`, que aún debe crearse.

## Pasos terminados

1. Unión por clave de conteos CPV 2022 y Marco 2021: 24 provincias, 221 cantones, 1.042 parroquias, 52.864 sectores y 209.373 manzanas con geometría y conteo. Las 1.852 manzanas sin polígono permanecen en el sector.
2. Tippecanoe v2.79.0 generó 52 PMTiles, total 154.511.848 bytes; máximo por archivo 14.637.118 bytes. Fuentes GeoJSONL agregadas y tiles se generaron en un Codespace de 4 CPU, 16 GB RAM, 32 GB de almacenamiento y se trasladaron localmente; no entraron al historial Git.
3. Chunks binarios por provincia: 64.162.668 bytes. [`06_qa_chunks.py`](pipeline/06_qa_chunks.py) comparó población y jefatura femenina de 48 chunks y 284.977 unidades con los Parquet.
4. Paquete `data-derived-v1b` preparado: conteos y Parquet 149.130.353 bytes, tiles 154.511.848, chunks 64.162.668, total de datos 367.804.869. Manifest y cuatro tar.gz con SHA256 ya generados localmente. QA aditiva de conteos: diferencia cero; 11 tests Python y 4 TypeScript pasan.
5. Mapa mínimo multinivel renderizado en prueba local; se corrigió el worker de MapLibre v6. CARTO Dark Matter respondió «API key required», por lo que se usa fondo oscuro propio. [Captura](docs/qa/fase1b3_mapa.png) e [informe](docs/fase1b3_report.md).

## Siguiente comando exacto

```sh
gh release create data-derived-v1b data/interim/release_public_v1b/counts-finest-v1b.tar.gz data/interim/release_public_v1b/counts-other-v1b.tar.gz data/interim/release_public_v1b/tiles-v1b.tar.gz data/interim/release_public_v1b/chunks-v1b.tar.gz -R diegocevallos-tech/censo-vivo-ecuador --target feat/fase-1b3-tiles-paquete-web --title "CPV 2022 · paquete web 1B-3" --notes "Agregados por unidad censal oficial, PMTiles y chunks binarios; SHA256 en data/DERIVED_MANIFEST.json"
```

Antes, hacer commit y push de los cambios pendientes del manifiesto, workflow, informe y visor. Luego restaurar el Release para verificar hashes; despachar `deploy.yml` con `preview=false`, comprobar Pages y abrir PR 1B-3. Mantener el PR abierto para revisión. Después seguir 2A y 2B según la autorización vigente sin tocar la auditoría independiente.

## Archivos tocados en 1B-3

- `HANDOFF.md`, `data/DERIVED_MANIFEST.json`
- `pipeline/06_tiles.py`, `06_chunks.py`, `06_aux_binary.py`, `06_package_v1b.py`, `06_qa_chunks.py`, `verify_public_artifacts.py`
- `.github/workflows/ci.yml`, `.github/workflows/deploy.yml`
- `web/src/main.ts`, `web/src/map.ts`, `web/src/style.css`, `web/src/vite-env.d.ts`
- `README.md`, `docs/schema.md`, `docs/data-access.md`, `docs/fase1b3_report.md`, `docs/qa/fase1b3_mapa.png`

## Decisiones pendientes

- La distancia al pico temporal del bono demográfico sigue diferida a la Fase 5 opcional. Cobertura de seguro de salud sigue descartada por variable inexistente.
- La capa de fondo oscuro usa un color propio hasta encontrar un basemap externo sin token que permita uso en producción. El mapa censal no depende de un proveedor externo.
- El «último plan» no está archivado literalmente en el repo; 2A se interpreta como mapa, navegación, indicadores y coropleta (issues #14–15); 2B como selección, paneles, controles y accesibilidad (issues #16–18). Conservar PRs separados.
