# Fase 1A: conteos geográficos

## Fuentes y proceso

Los cinco CSV oficiales MANLOC del CPV 2022 se restauran desde el Release `data-raw-v1` del [almacén privado](https://github.com/diegocevallos-tech/censo-vivo-ecuador-raw), con verificación SHA256 contra [`data/MANIFEST.json`](../data/MANIFEST.json). [`01_filter_to_parquet.py`](../pipeline/01_filter_to_parquet.py) convierte los registros originales en Parquet privado particionado por provincia. Esos intermedios contienen registros individuales, quedan en `data/interim/` ignorado por git y nunca se suben al repositorio público ni a Pages.

[`02_counts_by_unit.py`](../pipeline/02_counts_by_unit.py) publica únicamente conteos. La unidad fina es manzana cuando existe polígono; para sectores rurales dispersos, códigos ocultos `888` y las 1.852 manzanas reales sin polígono, es sector. Las manzanas sin polígono contribuyen 36.040 personas y 18.701 viviendas al sector respectivo y se identifican con `asignado_a_sector`. No se pierde ninguna persona. La versión `geom_version: "marco-2021"` se graba en cada salida. La estadística se une a los tiles solo por clave: si llega cartografía 2022, se regeneran tiles sin recalcular los conteos.

El [esquema documentado](schema.md) incluye 42 grupos de edad por sexo, conteos de los cinco archivos, banderas de asignación, 145 variables categóricas a escala fina, 8 variables de origen geográfico desde cantón y autoidentificación `P11R` desde sector. Los nulos de una categoría no generan fila; ninguna salida publica IDs de persona, hogar o vivienda ni categorías cruzadas por individuo.

| Nivel | Unidades de la tabla ancha | Archivos Parquet de tabla ancha |
| --- | ---: | ---: |
| Fino, manzana o sector | 231.464 | 24 |
| Sector | 53.513 | 24 |
| Parroquia | 1.042 | 1 |
| Cantón | 221 | 1 |
| Provincia | 24 | 1 |
| Nación | 1 | 1 |

Los 275 assets públicos de la fase, incluidos esquemas JSON y QA, ocupan **470.499.294 bytes** en el artifact privado promovido. El mayor archivo Parquet ocupa **57.795.539 bytes**; el sitio queda por debajo de 900 MB de datos y cada archivo del repositorio por debajo de 100 MB. La ejecución local produjo archivos más grandes por diferencias de compresión; una comparación de número de filas, sumas y huellas agregadas de filas coincidió en cada nivel.

## Control de calidad

[`07_qa.py`](../pipeline/07_qa.py) compara la suma de cada uno de los 59 campos numéricos entre todos los niveles y contrasta población y viviendas de los 221 cantones y 24 provincias con los CSV oficiales de desagregación CANTÓN. Comprueba también cada categoría publicada, la pirámide por edad y sexo y `geom_version`. El resultado reproducible está en [`web/public/data/counts/v1a/qa.json`](../web/public/data/counts/v1a/qa.json).

| Comprobación | Resultado |
| --- | ---: |
| Población nacional | 16.938.986 |
| Viviendas nacionales | 6.611.555 |
| Manzanas asignadas al sector | 1.852 |
| Población asignada al sector | 36.040 |
| Viviendas asignadas al sector | 18.701 |
| Diferencia de campos numéricos entre niveles | 0 |
| Diferencia de categorías entre niveles | 0 |
| Cantones y provincias distintos de los CSV oficiales | 0 |
| Unidades cuya pirámide no suma la población | 0 |

La categoría de control `AUR` suma exactamente las filas fuente de Población (16.938.986), Vivienda (6.611.555), Hogar (5.193.548), Emigración (124.992) y Mortalidad (250.746). También se comprobó `P02` para población, `V01` para vivienda y `P11R` para la base SECTOR: todos suman sus respectivos universos completos.

La comparación independiente con CANTÓN cubre población y viviendas. Los conteos de hogares, emigración y mortalidad se validan por aditividad y total de filas fuente; no se afirma aquí una comparación con totales oficiales externos para esas tablas.

El [workflow privado verificado](https://github.com/diegocevallos-tech/censo-vivo-ecuador-raw/actions/runs/36079183320) construyó los mismos agregados, publicó un artifact de siete días y el Release privado [`data-derived-v1a`](https://github.com/diegocevallos-tech/censo-vivo-ecuador-raw/releases/tag/data-derived-v1a). La creación inicial del Release recibió HTTP 403 con el `GITHUB_TOKEN` de Actions; se creó vacío con la sesión local del mantenedor y se repitió solo el job de publicación, que subió el paquete correctamente. No se usó un token entre repositorios. El PR público incorpora únicamente el paquete agregado tras verificar columnas, tamaños y ausencia de microdatos con [`verify_public_artifacts.py`](../pipeline/verify_public_artifacts.py). Los workflows públicos no leen originales ni datos privados.
