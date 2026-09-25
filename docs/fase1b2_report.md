# Fase 1B-2 · cruces, geodemografía y estadística espacial

**Estado:** cálculos ejecutados localmente con originales verificados del Release privado y agregados exactos de 1B-1. Este PR contiene código, catálogo y resultados resumidos; los Parquet y `clusters.json` generados permanecen bajo `data/interim/` (ignorado por Git). La publicación de todo el paquete web y su manifiesto corresponde a 1B-3.

## Cruces e indicadores

El catálogo incluye **45 indicadores** implementados, uno pendiente por falta de serie temporal comparable y uno descartado porque la variable solicitada no existe. Se añadieron los cruces de jefatura femenina, soledad 65+, escolaridad por edad, rezago, acceso digital compuesto por sexo y edad, empleo por sexo, maternidad adolescente y lengua indígena. La matriz entre cantones, perfiles de emigración y mortalidad y el SoVI se calculan a partir de las fuentes verificadas. [Inventario de pendientes](qa/indicadores_pendientes.md) y [esquema](schema.md).

La QA comprobó **diferencia cero en 46 campos aditivos** para unidad fina → sector → parroquia → cantón → provincia → nación. Los perfiles de emigración suman **124.992** personas y los de mortalidad **250.746** fallecimientos, iguales a 1B-1. Los flujos inter-cantonales suman **604.723** movimientos observados; entradas menos salidas dan **cero** a nivel nacional. La [validación externa](qa/validacion_inec.md) presenta 51 comparaciones: jefatura femenina nacional **38,457 %** (INEC 38,5 %), analfabetismo 15+ **3,740 %** (3,7 %) y uso individual de internet 5+ **69,440 %** (69,4 %).

## Selección de k y retratos

La muestra determinista contiene 2.400 sectores. Los 40 rasgos y el preprocesamiento constan en [metodología](metodologia.md) y en `clusters.json` generado localmente. El gap siguió subiendo entre los k ensayados, sin codo claro. Entre modelos a menos de 0,1 del mejor gap, k=4 obtuvo el mayor silhouette. La separación es modesta; se presentan los grupos como una **tipología exploratoria**, no como categorías oficiales.

| Supergrupos `k` | Silhouette | Gap | Desviación del gap |
| ---: | ---: | ---: | ---: |
| **4** | **0,06926** | 0,91274 | 0,00188 |
| 6 | 0,05208 | 0,94974 | 0,00487 |
| 8 | 0,04392 | 0,97475 | 0,00160 |
| 10 | 0,04923 | 0,99775 | 0,00405 |

El segundo k-means divide cada supergrupo en dos: **8 grupos**. Se asignó un retrato a los **53.513 sectores** y a sus **16.938.986** habitantes. Los **50.457 sectores** con al menos 100 personas participaron en el ajuste. De ellos, **50.353** tienen además los seis componentes SoVI válidos y quedan habilitados como perfiles comparables para gemelos. Los 3.056 sectores pequeños reciben grupo para el mapa pero se excluyen de rankings y gemelos; los otros 104 sin un componente válido también se excluyen de gemelos.

| Grupo | Retrato | Sectores | Población |
| ---: | --- | ---: | ---: |
| 0 | Lenguas originarias · Rezago educativo | 1.712 | 243.428 |
| 1 | Baja escolaridad · Rezago educativo | 9.978 | 2.073.463 |
| 2 | Alta escolaridad · Estudios superiores | 6.898 | 2.372.109 |
| 3 | Alta escolaridad · Estudios superiores · Hogares solos | 2.938 | 906.299 |
| 4 | Hacinamiento · Infancias | 10.832 | 3.722.804 |
| 5 | Lenguas originarias · Hogares numerosos | 1.613 | 396.991 |
| 6 | Vivienda arrendada · Vida conectada | 7.211 | 2.497.886 |
| 7 | Vida conectada · Estudios superiores | 12.331 | 4.726.006 |

El primer componente PCA del SoVI explica **40,02 %** de la varianza de sus seis rasgos. Sus cargas orientadas hacia mayor rezago son: escolaridad baja **+0,5724**, analfabetismo **+0,5081**, hacinamiento **+0,4376**, soledad 65+ **+0,2078**, maternidad adolescente **+0,4150** y brecha digital por sexo **−0,0846**. Los centros, escalas y límites de recorte exactos están en [`indicators.yaml`](../indicators.yaml); la QA comparó el cálculo por sumas del catálogo con diez puntajes sectoriales publicados (tolerancia 1e−5 por float32). Los vectores estandarizados de 40 rasgos para gemelos se generan por sector.

## Estadística espacial

El Marco 2021 aportó geometría a **52.864 de 53.513 sectores (98,787 %)**. Los 649 sin coincidencia se conservan en los conteos e índices, y se omiten solo de Moran/LISA. Tras el umbral de denominador de 30, **52.654 sectores** tienen al menos un resultado LISA. Se calculó Moran global por cantón y LISA por sector para seis variables: hacinamiento, vacancia, jefatura femenina, analfabetismo 15+, uso de internet 5+ e índice de envejecimiento. Son 221 cantones × 6 variables; los casos sin al menos cuatro sectores válidos o sin variación quedan con valor nulo, no inventado. La disimilitud educativa se calculó para 221 cantones y varía entre **0,1597 y 0,6426**. Los valores p de 99 permutaciones y las etiquetas alto-alto/bajo-bajo son exploratorios, con múltiples pruebas locales.

## Tamaños y publicación

| Salida local | Bytes | Destino previsto en 1B-3 |
| --- | ---: | --- |
| Cruces aditivos (29 Parquet) | 12.545.931 | Paquete de conteos |
| Flujos y perfiles (4 Parquet) | 213.411 | Paquete de conteos |
| Clusters, perfiles y metadatos | 5.169.900 | Chunks/perfiles |
| Moran, LISA y disimilitud | 4.062.998 | Capa espacial |
| **Total adicional** | **21.992.240** | Release público `data-derived-v1b` en 1B-3 |

El paquete 1B-1 permanece en **135.974.755 bytes**. La suma provisional de todos los Parquet rebasaría los 150 MB reservados a conteos y Parquet si se publicara sin convertir los perfiles y la capa LISA a los formatos finales de 1B-3. No se ha añadido ninguno de estos archivos al historial público ni a Pages. La comprobación del presupuesto final se hará antes del PR 1B-3.

## Reproducción y pruebas

Tras restaurar las fuentes privadas verificadas y ejecutar 1A/1B-1:

```sh
python pipeline/03_cross_counts.py
python pipeline/03b_mobility.py
python pipeline/03d_qa.py
python pipeline/04_geodemographics.py
python pipeline/05_spatial_stats.py
python pipeline/06_qa_phase1b2.py
python pipeline/08_validate_inec.py --base data/interim/exact_public/counts/v1b1 --cross data/interim/cross_counts_v1b2 --write docs/qa/validacion_inec.md
```

`pytest` y Vitest comprueban la paridad Python/TypeScript de los 45 indicadores a 1e−9; el test de `min_n` confirma «pocos casos», exclusión de rankings y suavizado apagado por defecto. Los Parquet generados fueron revisados por esquema: no contienen identificadores ni columnas por persona.
