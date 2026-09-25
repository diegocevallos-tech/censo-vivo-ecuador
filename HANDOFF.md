# Continuidad de Censo Vivo Ecuador

## Estado

- Fase actual: 1B-2, rama `feat/fase-1b2-geodemografia`; PR de 1B-2 por abrir, pendiente de aprobación antes del merge.
- Fase 1B-1 cerrada: PR privado #4 y público #44 fusionados por squash en ese orden, ramas eliminadas, tag `fase-1b1` en ambos repos.
- Producción de Pages desactivada hasta Fase 2. Los Parquet nuevos siguen ignorados bajo `data/interim/`; su publicación web corresponde a 1B-3.

## Pasos terminados

1. Primer commit `1532927`: [inventario de 13 pendientes y un descarte](docs/qa/indicadores_pendientes.md), [51 comparaciones INEC](docs/qa/validacion_inec.md) y script reproducible. Cumple el orden pedido antes de implementar 1B-2.
2. Cruces por unidad censal oficial: 46 campos aditivos, diferencia cero desde unidad fina hasta nación. Flujos inter-cantonales: 604.723, saldo nacional cero. Perfiles de emigración: 124.992; mortalidad: 250.746, idénticos a 1B-1.
3. Catálogo: 45 indicadores con `min_level` y `min_n`, incluido SoVI con cargas PCA publicadas. Queda diferida la distancia temporal al pico del bono demográfico; seguro de salud sigue descartado. Python y TypeScript usan la misma fórmula sobre sumas.
4. Geodemografía: 40 rasgos, k=4 elegido con silhouette/gap, 8 grupos con retratos y 53.513 sectores. Hay 50.353 perfiles aptos para gemelos; los sectores de pocos casos no entran en comparaciones.
5. Moran/LISA para seis índices en 221 cantones; disimilitud educativa en 221 cantones. Match Marco 2021: 52.864/53.513 sectores (98,787 %). QA de diez puntajes SoVI frente al catálogo pasó.
6. [Informe 1B-2](docs/fase1b2_report.md) con método, cifras, límites y tamaños. Ningún dato pesado entró en Git.

## Siguiente comando exacto

```sh
git status --short --branch
```

Después, ejecutar QA final, confirmar paridad Python/TypeScript, hacer commit Conventional Commits, push de la rama y abrir el PR. Actualizar este archivo con el número de PR y el siguiente comando `gh pr checks` en un commit final. Esperar la aprobación del usuario.

## Archivos tocados

- `HANDOFF.md`, `docs/qa/indicadores_pendientes.md`, `docs/qa/validacion_inec.md`, `docs/schema.md`, `docs/metodologia.md`, `docs/fase1b2_report.md`
- `pipeline/03_cross_counts.py`, `03b_mobility.py`, `03d_qa.py`, `04_geodemographics.py`, `05_spatial_stats.py`, `06_qa_phase1b2.py`, `08_validate_inec.py`, `indicators.py`, `generate_indicators.py`
- `indicators.yaml`, `tests/indicator_cases.json`, `tests/test_indicators.py`, `web/src/indicators.ts`, `web/src/generated/indicators.json`

## Decisiones pendientes

- La distancia al pico del bono demográfico requiere una serie comparable; permanece para Fase 5 opcional.
- El paquete local adicional de 21.992.240 bytes deberá compactarse y categorizarse según el presupuesto de 1B-3 antes de entrar a Pages. No se publica en esta fase.
- El usuario debe aprobar el PR 1B-2 antes del merge y antes de comenzar 1B-3.
