# Selección táctil en móvil

Corrección de interfaz sobre los datos y métodos ya publicados. No cambia la cartografía, los conteos ni las reglas de agregación.

## Recorrido como usuario

| Herramienta | Interacción móvil comprobada |
| --- | --- |
| Inspeccionar | Tocar una unidad la selecciona; tocarla otra vez la deselecciona y limpia la ruta. Las demás unidades quedan atenuadas y visibles. |
| Círculo | Un toque lo coloca con radio inicial visible. Se mueve desde el centro y se ajusta con el asa o el deslizador; el radio y la población se actualizan. |
| Lazo | Se dibuja con un dedo y se cierra al levantarlo. |
| Multi | Cada toque añade o quita una unidad sin cerrar el mapa. Las demás permanecen visibles para escoger otra. |
| Limpiar | Borra figura, resaltado, análisis y ruta; vuelve a Inspeccionar. «Borrar selección» está también dentro de la guía de dibujo. |

Las asas tienen un objetivo táctil de 44 × 44 px. Mientras se dibuja, el mapa no se desplaza ni cambia de zoom por gestos accidentales. El doble toque para deseleccionar tampoco hace zoom; el gesto de pellizcar sigue disponible en Inspeccionar y Multi. Los cálculos anteriores quedan invalidados al borrar o iniciar otra selección. En modo de dibujo se oculta la búsqueda para dejar más mapa visible; vuelve al pulsar «Hecho» o «Limpiar». Las selecciones por área identifican la población estimada con ≈ cuando incluyen unidades cortadas.

## Verificación

- `npm run lint`: correcto.
- `npm test -- --run`: 13 pruebas en 5 archivos, correctas.
- `npm run build`: correcto.
- `node scripts/test-mobile-layout.mjs`: mapa, explorador, análisis, barra y escritorio, correctos.
- `node scripts/test-mobile-selection.mjs`: 390 × 844 y 360 × 640, inspección y deselección, círculo con radio, lazo, multiselección, limpiar y ausencia de errores JavaScript, correctos.
- [CI pública](https://github.com/diegocevallos-tech/censo-vivo-ecuador/actions/runs/37049414704) y [build del devcontainer](https://github.com/diegocevallos-tech/censo-vivo-ecuador/actions/runs/37049414793): correctos.
- [Despliegue a Pages](https://github.com/diegocevallos-tech/censo-vivo-ecuador/actions/runs/37050038443): correcto. Se repitió el mismo E2E contra [producción](https://diegocevallos-tech.github.io/censo-vivo-ecuador/) en 390 × 844 y 360 × 640; pasó sin errores JavaScript.

Capturas: [círculo en Quito a 360 px](../capturas/mobile-circulo-quito.png), [control de radio](../capturas/mobile-circulo-control.png), [lazo](../capturas/mobile-lazo-control.png) y [multiselección](../capturas/mobile-multi-control.png).
