# Mapa visible en móviles

## Hallazgo

En producción, a 390 × 844 px, el explorador ocupaba la zona superior derecha y el panel de análisis hasta el 40 % inferior de la pantalla. El mapa quedaba reducido a una franja entre ambos. En teléfonos más bajos, la superposición era mayor.

## Corrección

- El mapa es la vista inicial. Los botones **Mapa**, **Explorar** y **Análisis** muestran un solo panel a la vez.
- Cada panel abierto ocupa como máximo el 42 % de la altura; en pantallas de hasta 700 px de alto, el 34 %. El contenido largo se desplaza dentro del panel.
- La búsqueda, la ruta territorial, el idioma y las herramientas quedan disponibles sin abrir paneles.
- Elegir un indicador o una herramienta devuelve el foco al mapa. Una selección permanece visible y señala que hay resultados disponibles en **Análisis**; el panel se abre solo al solicitarlo.
- Las etiquetas del selector móvil cambian con ES/EN y el estado de selección se comunica mediante una etiqueta accesible.

## Verificación

`node web/scripts/test-mobile-layout.mjs` pasó en 390 × 844 y 360 × 640 px, además de comprobar que escritorio (1280 × 800 px) conserva ambos paneles. Se probó selección por toque, alternancia de paneles, herramienta de lazo y ausencia de errores JavaScript. También pasaron `npm run build`, `npm run lint` y 13 pruebas Vitest.

Capturas: [mapa](../capturas/mobile-mapa.png), [selección](../capturas/mobile-seleccion.png), [explorador](../capturas/mobile-explorar.png) y [análisis](../capturas/mobile-analisis.png).

Esta corrección aborda la visibilidad del mapa. La carga inicial y Lighthouse móvil permanecen en la [issue #51](https://github.com/diegocevallos-tech/censo-vivo-ecuador/issues/51).
