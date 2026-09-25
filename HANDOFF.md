# Continuidad de Censo Vivo Ecuador

## Estado

- Fase actual: 1B-1 Indicadores, rama pública `feat/fase-1b1-indicadores`; PR aún sin abrir.
- Último paso cerrado: Release público `data-derived-v1b1` publicado y verificado por descarga remota; workflow privado 1B-1 lanzado.
- Criterio definitivo del usuario: publicar conteos agregados completos en unidades oficiales del INEC, sin supresión, perturbación ni microzonas.

## Terminado

- Rama 1B-1 reiniciada desde `origin/main` antes de publicarse para retirar código experimental de supresión, recodificación e IPF que el usuario reemplazó.
- Se constató que 1.333 sectores tienen menos de 50 personas o 15 viviendas ocupadas; la idea de microzonas fue descartada por instrucción posterior del usuario.
- `deploy.yml` solo permite preview manual. Producción de Pages continúa desactivada hasta Fase 2.
- El Release histórico `data-derived-v1a` contiene agregados suprimidos; el nuevo Release de 1B-1 deberá reemplazarlo en el manifiesto y el deploy.
- `02c_pack_exact.py` produjo 153 archivos agregados, 135.974.755 bytes, máximo 30.201.346 bytes. El paquete inicial exacto ocupó 186.136.613 bytes; se ahorraron 50.161.858 bytes derivando categorías sectoriales de las finas y almacenando solo `P11R` por separado.
- `verify_release_integrity.py` pasó con diferencia cero en todos los niveles y categorías tras restaurar los archivos del Release local y comprobar sus SHA256. Nacional: 16.938.986 personas y 6.611.555 viviendas. `verify_public_artifacts.py` confirmó ausencia de columnas personales.
- `aggregation.py` y `web/src/aggregation.ts` suman unidades completas y ponderan por área solo cortes de borde; tests compartidos pasan a 1e-9.
- `indicators.yaml` declara 30 indicadores con `min_level` y `min_n`; 1 descartado y 13 pendientes están documentados. Documentación y casos de paridad se generan del catálogo.
- Motor Python/TypeScript: 10 tests Python, 3 TypeScript y compilación web pasan. Empirical Bayes está apagado por defecto; `rank_eligible` excluye resultados con pocos casos.
- CI pública restaura el Release público, rechaza columnas personales y comprueba aditividad exacta hasta nación. El empaquetador antiguo de supresión fue retirado.
- Los casos de paridad se redujeron a claves relevantes por indicador: 135.473 bytes, sin blobs grandes en esta rama.
- Release público: https://github.com/diegocevallos-tech/censo-vivo-ecuador/releases/tag/data-derived-v1b1. Descarga remota, SHA256 e integridad exacta pasaron.
- Workflow privado en curso: https://github.com/diegocevallos-tech/censo-vivo-ecuador-raw/actions/runs/36127455216. Rama privada `feat/fase-1b1-publicacion-exacta` publicada.

## Siguiente comando exacto

Consultar el run privado y abrir los PR de 1B-1:

```sh
gh run view 36127455216 -R diegocevallos-tech/censo-vivo-ecuador-raw
```

Después, abrir PR público 1B-1 y PR privado del workflow, verificar CI y preview, y esperar aprobación. No iniciar 1B-2.

## Archivos tocados en este paso

- `HANDOFF.md`, `docs/metodologia.md`, `docs/schema.md`, `docs/fase1b1_report.md`: criterio, esquema, QA y estado.
- `pipeline/02c_pack_exact.py`, `pipeline/package_derived.py`, `pipeline/check_derived_manifest.py`, `pipeline/verify_public_artifacts.py`, `pipeline/verify_release_integrity.py`: generación y comprobación del paquete.
- `pipeline/aggregation.py`, `web/src/aggregation.ts`, `tests/aggregation_cases.json`, `tests/test_aggregation.py`, `web/src/aggregation.test.ts`: suma directa y paridad.
- `data/DERIVED_MANIFEST.json`: SHA256 y tamaño del nuevo paquete exacto.
- `indicators.yaml`, `pipeline/indicators.py`, `web/src/indicators.ts`, generador y tests: catálogo y paridad.
- `.github/workflows/ci.yml`, `pipeline/verify_public_artifacts.py`: integridad pública.

## Decisiones pendientes

- El paquete exacto y Release público cumplen 150 MB; faltan PR, CI y run de preview.
- El aviso «pocos casos» excluye índices con denominador bajo de rankings, percentiles y gemelos; Empirical Bayes queda apagado por defecto.
