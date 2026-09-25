# Continuidad de Censo Vivo Ecuador

## Estado

- Fase actual: 1B-2, rama pública `feat/fase-1b2-geodemografia`.
- Los PR privado #4 y público #44 se fusionaron por squash en ese orden. Sus ramas remotas se borraron. El tag `fase-1b1` se publicó en ambos repos.
- Producción de Pages continúa desactivada hasta Fase 2. El PR 1B-2 quedará abierto hasta aprobación.

## Terminado

- [Inventario](docs/qa/indicadores_pendientes.md) de 13 indicadores pendientes y uno descartado.
- [Validación INEC](docs/qa/validacion_inec.md) de 11 magnitudes para nación, Pichincha, Guayas y Azuay; diferencias investigadas.
- [Script reproducible](pipeline/08_validate_inec.py) que lee solo agregados por unidad censal.

## Siguiente comando exacto

```sh
.\.venv\Scripts\python.exe -m pytest tests/test_indicators.py -q
```

Después, implementar los cruces disponibles, geodemografía, Moran/LISA, disimilitud y perfiles de gemelos. Mantener agregados pesados en Release y fuera de Git. Actualizar HANDOFF.md y hacer commit al cerrar cada paso.

## Archivos tocados

- `HANDOFF.md`
- `docs/qa/indicadores_pendientes.md`
- `docs/qa/validacion_inec.md`
- `pipeline/08_validate_inec.py`

## Decisiones pendientes

- La distancia al pico temporal del bono demográfico necesita una serie comparable; queda para la Fase 5 opcional.
- El usuario aprobará el PR 1B-2 antes del merge o de iniciar 1B-3.
