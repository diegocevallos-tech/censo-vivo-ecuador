## FASE 2C · Variables del censo

Explorador de los agregados originales del CPV 2022: catálogo desde cinco
diccionarios INEC, 126 variables disponibles, búsqueda por pregunta/código,
categorías, mapa en %/conteo/densidad o media, histogramas y distribución en
selecciones. Respeta `min_level`; `P08P` mueve el mapa a cantón y explica por
qué. El visor descarga solo rangos de la variable elegida.

| Componente | Antes v2d | Después v2e |
| --- | ---: | ---: |
| Categorías finas mezcladas | 122.687.539 B | 0 B |
| Bloques por variable | 0 B | 99.217.596 B |
| Conteos y Parquet | 149.529.581 B | 126.059.638 B |
| Datos completos para Pages | 447.948.448 B | 424.478.505 B |

El bloque máximo es 1.171.306 B por variable/provincia. En la prueba de
`V03` (techo) se descargaron 575,6 KB; las seis respuestas binarias usaron
HTTP 206 y ninguna superó 134.357 B.

QA: 10 variables elegidas con semilla fija y controles `P11R`, `P08P`, `P03`
coinciden en manzana, sector, parroquia/cantón y nación, diferencia cero.
También pasa la aditividad de conteos sector→nación. Ruff, 15 pytest,
13 Vitest, ESLint, build y E2E local pasaron sin errores JS. Los cinco assets
del [prerelease v2e](https://github.com/diegocevallos-tech/censo-vivo-ecuador/releases/tag/data-derived-v2e)
se descargaron de nuevo: 398 archivos y SHA256 correctos. Solo agregados.

Revisión: [informe](docs/fase2c_report.md),
[captura de techo](docs/capturas/fase2c_variables_techo.png),
[captura de escala mínima](docs/capturas/fase2c_min_level_canton.png).

Límite de las fuentes: algunos códigos de país, ocupación y rama carecen de
etiqueta en los clasificadores verificados. Se muestran como códigos INEC con
aviso; no se inventaron nombres. `P03` usa grupos de cinco años y rotula su
media como aproximada.

**Esperando aprobación para fusionar y activar v2e en Pages.** La producción
permanece en v2d. La optimización móvil de #51 empieza después de 2C.
