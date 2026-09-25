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
