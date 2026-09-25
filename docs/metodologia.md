# Metodología · conteos censales e indicadores

## Fuente y unidades: datos abiertos del INEC, unidades censales oficiales, sin modificación

El portal publica únicamente conteos agregados del VIII Censo de Población y VII de Vivienda 2022 del INEC. Las unidades son manzana, sector censal, parroquia, cantón, provincia y nación. No se crean microzonas ni se aplican supresión, ruido o perturbación. Nunca se publican filas por persona, hogar o vivienda. Los códigos geográficos `888` se respetan tal como vienen del INEC.

La geometría de referencia es el Marco 2021, unido a las estadísticas solo por clave (`geom_version: marco-2021`). Las 1.852 manzanas censales sin polígono se conservan como conteos en su sector; no se les atribuye geometría. El visor debe indicarlas como «población asignada a nivel de sector». La [QA cartográfica](fase0_report.md) documenta su cobertura y la diferencia de versiones.

## Agregación y fiabilidad

Todos los numeradores y denominadores son conteos. Una selección de unidades completas suma los conteos directamente y se etiqueta «exacto». Cuando el borde de un círculo o lazo corta una manzana, solo esa fracción se pondera por su proporción de área y el resultado se etiqueta «estimado», con el porcentaje de población procedente de cortes. Los porcentajes e índices se calculan después de sumar numeradores y denominadores; no se promedian tasas de manzanas.

El `min_n` de cada indicador está en [`indicators.yaml`](../indicators.yaml). Un valor con denominador menor a ese umbral muestra «pocos casos» y se excluye de rankings, percentiles y el buscador de gemelos. La opción de suavizado Empirical Bayes es visible como toggle y está **apagada por defecto**; los conteos publicados nunca se alteran por ese cálculo.

## Almacenamiento e integridad

Los Parquet usan zstd y tipos enteros sin signo mínimos según máximos reales. Las categorías originales se guardan en formato largo; los 42 conteos de edad × sexo y los totales geográficos, en ancho. Para no duplicar unos 50 MB, las categorías de sector se obtienen como suma exacta de las categorías de sus manzanas y sectores dispersos. `P11R`, disponible solo desde sector, se guarda aparte en `categories/sector_only/`. Las tablas anchas de sector y los demás niveles se publican directamente. Esta deduplicación cambia el almacenamiento, no el valor de ningún conteo.

[`verify_release_integrity.py`](../pipeline/verify_release_integrity.py) comprueba la suma exacta de manzana a sector y de cada nivel al siguiente; [`verify_public_artifacts.py`](../pipeline/verify_public_artifacts.py) rechaza columnas que puedan identificar registros personales. El [manifiesto derivado](../data/DERIVED_MANIFEST.json) contiene tamaño y SHA256 de cada archivo. El [informe de Fase 1B-1](fase1b1_report.md) registra el tamaño y las pruebas del paquete exacto.
