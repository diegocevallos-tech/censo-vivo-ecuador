# Continuidad de Censo Vivo Ecuador

## Estado

- Fase actual: 1B-3, rama `feat/fase-1b3-tiles-paquete-web`. [PR público #45](https://github.com/diegocevallos-tech/censo-vivo-ecuador/pull/45) fusionado por squash y tag `fase-1b2` publicado. No tocar la rama de auditoría independiente `feat/auditoria-1b2`.
- Fase 1B-1 cerrada: PR privado #4 y público #44 fusionados por squash en ese orden, ramas eliminadas, tag `fase-1b1` en ambos repos.
- El usuario autorizó producción de Pages en 1B-3 para el mapa mínimo multinivel de densidad. Los Parquet nuevos siguen ignorados bajo `data/interim/`; se publicarán como assets agregados del Release público.

## Pasos terminados

1. Primer commit `1532927`: [inventario de 13 pendientes y un descarte](docs/qa/indicadores_pendientes.md), [51 comparaciones INEC](docs/qa/validacion_inec.md) y script reproducible. Cumple el orden pedido antes de implementar 1B-2.
2. Cruces por unidad censal oficial: 46 campos aditivos, diferencia cero desde unidad fina hasta nación. Flujos inter-cantonales: 604.723, saldo nacional cero. Perfiles de emigración: 124.992; mortalidad: 250.746, idénticos a 1B-1.
3. Catálogo: 45 indicadores con `min_level` y `min_n`, incluido SoVI con cargas PCA publicadas. Queda diferida la distancia temporal al pico del bono demográfico; seguro de salud sigue descartado. Python y TypeScript usan la misma fórmula sobre sumas.
4. Geodemografía: 40 rasgos, k=4 elegido con silhouette/gap, 8 grupos con retratos y 53.513 sectores. Hay 50.353 perfiles aptos para gemelos; los sectores de pocos casos no entran en comparaciones.
5. Moran/LISA para seis índices en 221 cantones; disimilitud educativa en 221 cantones. Match Marco 2021: 52.864/53.513 sectores (98,787 %). QA de diez puntajes SoVI frente al catálogo pasó.
6. [Informe 1B-2](docs/fase1b2_report.md) con método, cifras, límites y tamaños. Ningún dato pesado entró en Git.
7. PR #45 fusionado con squash (`9fc13528`), rama remota y local eliminadas, tag `fase-1b2` publicado. Rama nueva 1B-3 creada desde `main`.
8. Geometrías del Marco 2021 cruzadas solo por clave con los conteos exactos: 24 provincias, 221 cantones, 1.042 parroquias, 52.864 sectores y 209.373 manzanas con polígono y conteo. Fuentes GeoJSONL locales ignoradas; no entran a Git.
9. Chunks binarios por provincia para conteos y perfiles 1B-2 generados localmente. Mapa mínimo de densidad por nivel creado y `npm run build` pasa. Falta ejecutar tippecanoe, empaquetar Release y desplegar Pages.

## Siguiente comando exacto

```sh
gh codespace create -R diegocevallos-tech/censo-vivo-ecuador -b feat/fase-1b3-tiles-paquete-web -d censo-vivo-fase-1b3-tiles
```

Transferir las fuentes GeoJSONL agregadas al Codespace con tippecanoe; generar PMTiles, verificar límites, empaquetar Release público, activar Pages en producción y abrir PR 1B-3.

## Archivos tocados

- `HANDOFF.md`, `pipeline/06_tiles.py`, `pipeline/06_chunks.py`, `pipeline/06_aux_binary.py`, `pipeline/06_package_v1b.py`, `pipeline/verify_public_artifacts.py`, `web/src/main.ts`, `web/src/map.ts`, `web/src/style.css`, `web/src/vite-env.d.ts`
- `pipeline/03_cross_counts.py`, `03b_mobility.py`, `03d_qa.py`, `04_geodemographics.py`, `05_spatial_stats.py`, `06_qa_phase1b2.py`, `08_validate_inec.py`, `indicators.py`, `generate_indicators.py`
- `indicators.yaml`, `tests/indicator_cases.json`, `tests/test_indicators.py`, `web/src/indicators.ts`, `web/src/generated/indicators.json`

## Decisiones pendientes

- La distancia al pico del bono demográfico requiere una serie comparable; permanece para Fase 5 opcional.
- El paquete local adicional de 21.992.240 bytes deberá compactarse y categorizarse según el presupuesto de 1B-3 antes de entrar a Pages. No se publica en esta fase.
- La secuencia precisa de 2A y 2B se reconstruirá de issues y del plan vigente al concluir 1B-3. No alterar la rama de auditoría 1B-2.
