# Fase 1B-1 · paquete exacto y control de integridad

## Decisión de publicación

Se publican únicamente conteos agregados del INEC en sus unidades censales oficiales. No hay supresión, perturbación ni microzonas. El paquete conserva 209.373 manzanas censales en la tabla fina y 53.513 sectores, incluidos los 1.333 sectores que no habrían cumplido los umbrales descartados de microzonas. Las 1.852 manzanas sin polígono permanecen en su sector; no se crea geometría ficticia. Los códigos `888` se conservan.

Los 93.102.177 registros categóricos del nivel fino son **celdas agregadas por unidad**, no registros de persona. De ellos, 40.538.404 tienen conteo 1 o 2 y se conservan tal como provienen del agregado de las fuentes abiertas. [`verify_public_artifacts.py`](../pipeline/verify_public_artifacts.py) rechaza identificadores y columnas de registros individuales.

## Tamaño

| Paquete | Bytes | Cambio |
| --- | ---: | --- |
| Exacto, con categorías sectoriales duplicadas | 186.136.613 | Base de comparación |
| Exacto, sector derivado de suma fina + `P11R` sectorial | **135.974.755** | −50.161.858 (−26,95 %) |
| Presupuesto de conteos y Parquet | 150.000.000 | Margen 14.025.245 |

El mayor archivo navegador mide 30.201.346 bytes; el máximo permitido es 95.000.000. Los 153 archivos del paquete usan zstd, tipos enteros mínimos y suman 135,97 MB decimales. La eliminación de la copia sectorial no descarta observaciones: las categorías de sector se reconstruyen por suma exacta de `categories/finest/`; `P11R` se conserva aparte porque no existe a nivel manzana.

Los tres archivos comprimidos están en el [Release público `data-derived-v1b1`](https://github.com/diegocevallos-tech/censo-vivo-ecuador/releases/tag/data-derived-v1b1). Se descargaron de GitHub tras publicarlos; sus SHA256 coincidieron con el manifiesto versionado y la prueba de aditividad volvió a dar diferencia cero.

| Componente | Bytes |
| --- | ---: |
| Categorías finas completas | 122.687.539 |
| Conteos finos anchos | 6.267.432 |
| Conteos sectoriales anchos | 2.365.322 |
| `P11R` solo sector | 380.685 |
| Otros niveles, codebook y metadatos | 4.273.777 |

## QA reproducible

[`02c_pack_exact.py`](../pipeline/02c_pack_exact.py) contrastó filas y sumas de cada campo y categoría con el agregado completo privado. Después de empaquetar, [`verify_release_integrity.py`](../pipeline/verify_release_integrity.py) comprobó **diferencia cero** en cada transición: manzana/sector disperso → sector → parroquia → cantón → provincia → nación, incluidos los conteos categóricos. Los totales nacionales publicados son **16.938.986 personas y 6.611.555 viviendas**, iguales a los oficiales. El paquete se restauró desde sus archivos comprimidos tras verificar tamaños y SHA256 del [manifiesto derivado](../data/DERIVED_MANIFEST.json), y repitió esa QA con diferencia cero.

La selección de unidades completas suma conteos exactos. Solo una manzana cortada por el borde de una selección se pondera por área y se marca «estimado». El test compartido Python/TypeScript comprueba esa regla con tolerancia `1e-9`. La política de «pocos casos» y Empirical Bayes se describe en la [metodología](metodologia.md).

## Indicadores

El [catálogo único](../indicators.yaml) define **30 indicadores calculables** con nivel mínimo, denominador de referencia y umbral `min_n`. Documentación y casos de paridad se generan desde ese archivo. Hay **1 indicador descartado** (cobertura de seguro de salud: la fuente disponible registra aportes a seguridad social, que no equivalen a seguro) y **13 pendientes** por cruces no incluidos en el agregado actual o por corresponder a 1B-2. Sus razones concretas constan en el catálogo y en la [metodología](metodologia.md).

El motor Python y el de TypeScript usan la suma directa de conteos. **10 tests Python y 3 tests TypeScript** pasaron; los casos compartidos cubren los 30 indicadores y comparan valores, denominadores, fiabilidad e intervalos de Empirical Bayes con tolerancia `1e-9`. Un denominador inferior a `min_n` activa «pocos casos» y excluye ese resultado de rankings, percentiles y gemelos. El suavizado es opcional y está apagado por defecto.
