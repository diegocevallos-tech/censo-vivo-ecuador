# Continuidad de Censo Vivo Ecuador

## Estado

- Fase actual: 1B-1 Indicadores, rama pública `feat/fase-1b1-indicadores`; PR aún sin abrir.
- Último paso cerrado: PR privado #3 y público #43 fusionados con squash, ramas borradas, tag `fase-1a` en ambos repos y milestone 1A cerrado.
- Criterio definitivo del usuario: publicar conteos agregados completos en unidades oficiales del INEC, sin supresión, perturbación ni microzonas.

## Terminado

- Rama 1B-1 reiniciada desde `origin/main` antes de publicarse para retirar código experimental de supresión, recodificación e IPF que el usuario reemplazó.
- Se constató que 1.333 sectores tienen menos de 50 personas o 15 viviendas ocupadas; la idea de microzonas fue descartada por instrucción posterior del usuario.
- `deploy.yml` solo permite preview manual. Producción de Pages continúa desactivada hasta Fase 2.
- El Release histórico `data-derived-v1a` contiene agregados suprimidos; el nuevo Release de 1B-1 deberá reemplazarlo en el manifiesto y el deploy.

## Siguiente comando exacto

Con el agregado completo en `data/interim/full_aggregate_v1a` y la base `data/interim/counts_v1a.duckdb`:

```sh
.\.venv\Scripts\python.exe pipeline/02c_pack_exact.py
```

El empaquetador aún debe implementarse. Después, ejecutar QA de aditividad exacta, ausencia de columnas personales, presupuesto ≤150 MB, motor Python/TypeScript, CI, Release público y PR. No iniciar 1B-2.

## Archivos tocados en este paso

- `HANDOFF.md`: decisión definitiva y punto de reanudación.

## Decisiones pendientes

- Si los conteos completos no caben en 150 MB pese a la compresión y los tipos mínimos, detener publicación y presentar tamaños y opciones sin perder variables.
- El aviso «pocos casos» excluye índices con denominador bajo de rankings, percentiles y gemelos; Empirical Bayes queda apagado por defecto.
