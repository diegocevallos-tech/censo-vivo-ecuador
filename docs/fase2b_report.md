# Fase 2B · selección y análisis

## Entrega

- Selección de unidades oficiales por clic y multiselección, círculo con controles de centro y radio, y lazo dibujado. El círculo usa un índice KDBush para la vista previa en cada cuadro; al soltar, el área de intersección determina la proporción de cada unidad cortada.
- Los conteos publicados se cargan por provincia desde los chunks binarios del Release público. Una unidad completa suma exactamente sus conteos; una unidad cortada se pondera por área y el resultado lleva la calidad `estimado` y el porcentaje estimado. Los 1.852 registros de manzana sin polígono se conservan en el sector; en escala de manzana se incorporan únicamente si se seleccionan todas las manzanas cartografiadas de ese sector. No se asignan a una ubicación inventada dentro de una selección parcial.
- Panel de análisis con población, distribución por sexo, pirámide de 21 grupos con silueta nacional, grupos amplios de edad e indicadores. Se muestran `pocos casos` según el umbral del catálogo y se excluyen del percentil. El suavizado Empirical Bayes es opcional y está apagado por defecto.
- Selector temático, controles de densidad, unidades y extrusión 3D, estado territorial en la URL, ES/EN y panel desplazable en móvil.

## Pruebas

| Prueba | Resultado |
| --- | --- |
| Ruff y pytest | Sin errores; 11 tests Python |
| ESLint, Vitest y build Vite/TypeScript | Sin errores; 8 tests TypeScript |
| Navegador 1440 × 900 | Círculo, lazo, multiselección, 3D e idioma; 0 errores JavaScript |
| Navegador móvil 390 × 844 | Mapa y barra de herramientas disponibles; 0 errores JavaScript |
| Vista previa KDBush a zoom 14,3 | p95 del cálculo por cuadro: Quito 0,40 ms; Guayaquil 0,30 ms; Cuenca 0,40 ms, en Chromium de escritorio |
| Clic en manzana completa | Resultado `exacto` |
| Datos Release `data-derived-v2a` | Manifiesto verificado; 436.512.440 bytes de datos, bajo el objetivo de 800 MB |

[Captura de escritorio](qa/fase2b_mapa.png) · [Captura móvil](qa/fase2b_movil.png).

## Límites conocidos

- La vista previa del círculo usa centroides de polígonos visibles; el cálculo final usa intersección por área. Por ello la cifra preliminar puede cambiar al soltar el control.
- La ponderación por área en bordes supone densidad uniforme dentro de cada unidad. El porcentaje estimado cuantifica la parte de población calculada así, no un intervalo de confianza.
- La selección de manzanas sin polígono solo es localizable al sector. Los sectores y niveles superiores contienen sus conteos completos.
- Los p95 medidos cubren tres vistas urbanas de escritorio. La tasa de 60 cuadros por segundo en todas las provincias y en móviles de gama baja requiere una prueba adicional sobre esos dispositivos; el p95 de cálculo no mide el coste total de pintar el mapa.
