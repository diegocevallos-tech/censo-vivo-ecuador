# Continuidad de Censo Vivo Ecuador

## Estado

- Fase actual: cierre de Fase 1A; siguiente fase autorizada: 1B-1 Indicadores.
- PR público actual: [#43](https://github.com/diegocevallos-tech/censo-vivo-ecuador/pull/43), rama `feat/fase-1a-conteos`.
- PR privado actual: [#3](https://github.com/diegocevallos-tech/censo-vivo-ecuador-raw/pull/3), rama `feat/fase-1a-workflow`.
- Paso actual: preparar el merge en el orden privado → público. Ambos PR siguen abiertos.

## Terminado

- Fase 1A validada: conteos aditivos, QA oficial, supresión de manzanas pequeñas y categorías de sectores dispersos.
- Los derivados completos están en el Release público `data-derived-v1a`; git solo conserva el manifiesto y una muestra agregada.
- El preview de Pages verificó el Release. El workflow `deploy.yml` quedó limitado a `workflow_dispatch`: no hay disparador por `push` ni job de publicación de producción.

## Siguiente comando exacto

Desde el repositorio privado, después de confirmar la CI del PR público:

```sh
gh pr merge 3 --repo diegocevallos-tech/censo-vivo-ecuador-raw --squash --delete-branch
```

Luego fusionar el PR público #43 con squash, crear `fase-1a` en ambos repos, cerrar el milestone específico de 1A y abrir `feat/fase-1b1-indicadores`. No cerrar el milestone general «Fase 1 · Pipeline e índices» hasta terminar toda la Fase 1B.

## Archivos tocados en este paso

- `.github/workflows/deploy.yml`: solo preview manual.
- `HANDOFF.md`: estado y siguiente comando.

## Decisiones pendientes

- En 1B-1, calcular `docs/qa/supresion_impacto.md`. Si alguna variable supera 20 % de celdas de manzana suprimidas, presentar umbral alternativo con tabla de riesgo/beneficio y esperar decisión antes de cambiarlo.
- Mantener producción de Pages desactivada hasta la Fase 2.
