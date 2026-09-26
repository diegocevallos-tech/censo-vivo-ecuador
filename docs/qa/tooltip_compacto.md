# Tooltip compacto · corrección de UI

El tooltip de hover sigue el cursor y tiene un ancho máximo de 240 px. Presenta
nombre o código oficial, ruta, valor activo, población y las notas de escala o
manzanas sin polígono cuando corresponden. El clic deja el detalle en el panel
de análisis y ya no abre un segundo popup sobre el mapa.

No cambian los datos, `indicators.yaml`, la metodología ni la agregación.

## Verificación

[`test-tooltips.mjs`](../../web/scripts/test-tooltips.mjs) pasó siete casos locales
sin errores JavaScript. La prueba comprueba que el tooltip sigue el cursor,
que cada popup mide ≤240 px, y que al pulsar una parroquia o una variable
el detalle aparece en el panel. Anchos medidos: provincia 240, cantón 240,
parroquia 240, zona 226,6, sector 225 y variable sectorial 240 px.

[Resultado E2E](../capturas/tooltip-results.json) ·
[captura parroquia](../capturas/tooltip-parroquia.png) ·
[captura variable](../capturas/tooltip-variable.png) ·
[panel tras clic](../capturas/tooltip-analisis-parroquia.png).
