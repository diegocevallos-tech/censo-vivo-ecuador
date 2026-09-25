# Metodología de conteos y control estadístico · Fase 1A

## Fuentes y universo

Los conteos proceden de las cinco tablas MANLOC del CPV 2022 del INEC. Las filas originales se convierten a Parquet privado por provincia; solo las sumas geográficas se preparan para publicación. La base SECTOR aporta `P11R` para autoidentificación étnica, cuyo nivel mínimo es sector. El [manifiesto de originales](../data/MANIFEST.json) registra origen, tamaño y SHA256. El [esquema](schema.md) relaciona cada columna publicada con la variable del diccionario oficial.

La cartografía de referencia es el Marco 2021. Los conteos no incorporan polígonos: se unen a las geometrías solo por clave y llevan `geom_version: marco-2021`. Las 1.852 manzanas reales sin polígono, con 36.040 personas, se asignan a su sector censal; sus personas y viviendas permanecen en todos los niveles superiores. Las localidades rurales dispersas usan sector como unidad fina.

## Conteos y aditividad

Las tablas completas se calculan en privado por unidad fina, sector, parroquia, cantón, provincia y nación. Se almacenan numeradores y denominadores enteros; ningún porcentaje se promedia al agregar. Los 42 grupos de edad y sexo se suman a la población, incluyendo una celda separada para edades o sexos no clasificables. Las categorías se guardan en formato largo con códigos numéricos de unidad, variable y categoría; un pequeño codebook Parquet recupera sus etiquetas oficiales. Los conteos densos quedan en formato ancho. Cada columna entera usa `uint8`, `uint16` o `uint32` según su máximo comprobado, y los Parquet usan zstd.

La QA compara cada campo y categoría entre niveles completos, y contrasta población y viviendas de los 221 cantones y 24 provincias con los CSV oficiales de desagregación CANTÓN. La publicación puede ocultar detalle fino; los conteos completos de sector, parroquia, cantón, provincia y nación permanecen idénticos a los calculados en privado. Git conserva una [muestra agregada de cantones](../web/public/data/sample/canton.parquet) para pruebas; el conjunto nacional se sirve desde Pages tras comprobar el [manifiesto derivado](../data/DERIVED_MANIFEST.json).

## Regla de publicación para manzanas pequeñas

Una manzana con **menos de 10 personas** o **menos de 3 viviendas ocupadas** publica únicamente población, viviendas y hogares totales. Todos sus campos de edad, sexo, eventos y categorías se dejan sin valor en ese nivel, permanecen en el sector y la manzana lleva `detalle_en_sector = true`. Un valor nulo indica **detalle retenido en el sector**, no cero. Para viviendas particulares se cuentan como ocupadas `V0201 = 1` (personas presentes) o `2` (personas ausentes); para viviendas colectivas, `V0202 = 1` (residentes habituales), según el diccionario MANLOC del INEC. Las viviendas con otros códigos no cuentan hacia el umbral de ocupación.

Además, una celda positiva con conteo **1 o 2** en cualquier manzana se suprime en ese nivel y se conserva en el total del sector. La regla abarca categorías y campos desagregados del formato ancho, incluida la pirámide de edad y sexo. Las celdas cero pueden conservarse como cero; una categoría ausente en el formato largo nunca se interpreta como cero cuando `detalle_en_sector = true`.

Los **sectores dispersos** son ya unidades de escala sectorial, aunque aparezcan en la tabla de unidades finas para completar la cobertura geográfica. Sus categorías se conservan en esa tabla y en la tabla sectorial; el umbral de celdas de manzana no se aplica a ellas. La QA de empaquetado contrasta explícitamente el número y la suma de sus categorías antes y después de publicar.

## Supresión secundaria y límites

La supresión primaria sola permite recuperar un valor por diferencia si el total sectorial y todos los demás valores de sus manzanas están visibles. Por eso **sí hace falta supresión secundaria**. Cuando una combinación sector–variable–categoría, o sector–campo ancho, tiene exactamente una celda positiva retenida y al menos otra manzana con celda positiva publicable, se retiene también la menor de estas últimas. Así quedan al menos dos celdas positivas desconocidas en la resta. Los totales sectoriales no se alteran.

Cuando no existe una segunda celda positiva, no puede aplicarse esa regla manteniendo a la vez el total sectorial solicitado. El portal debe presentar esos datos como **estadística de sector**, sin atribuir el valor retenido a una manzana ni tratar ausencias como ceros. Incluso con dos celdas ocultas, las restricciones de enteros y otros totales visibles pueden permitir algunas inferencias: esta supresión reduce la reconstrucción directa, pero no equivale a una garantía de anonimato matemático. Los sectores con una sola manzana requieren especial cautela interpretativa: compartir límites no convierte el detalle suprimido en una observación publicable de manzana. El [informe de Fase 1A](fase1a_report.md) cuantifica las manzanas y personas afectadas por provincia y las celdas retenidas.

## Alcance

Estos umbrales son controles de publicación, no intervalos de confianza ni suavizado estadístico. El suavizado Empirical Bayes y la incertidumbre para áreas pequeñas corresponden a la Fase 1B. La coincidencia de claves con el Marco 2021 tampoco prueba identidad de límites con 2022; las interpretaciones espaciales finas deben indicar la versión cartográfica.
