# Esquema de conteos geográficos · Fase 1A

Los archivos de `web/public/data/counts/v1a/` contienen **conteos agregados**. Se generan con [`01_filter_to_parquet.py`](../pipeline/01_filter_to_parquet.py), [`02_counts_by_unit.py`](../pipeline/02_counts_by_unit.py) y se verifican con [`07_qa.py`](../pipeline/07_qa.py). El Parquet intermedio de `data/interim/filtered/` sí contiene registros originales y permanece fuera de git y del sitio. Los códigos y categorías proceden de los [diccionarios oficiales registrados en el manifiesto](../data/MANIFEST.json).

## Niveles y claves

`finest/` combina manzanas con polígono y sectores para localidades dispersas, códigos ocultos `888` y las 1.852 manzanas sin polígono. `sector/`, `parroquia/`, `canton/`, `provincia/` y `nacion/` son sumas exactas del nivel fino. La longitud de `unit_key` es 15 para manzana, 12 para sector, 6 para parroquia, 4 para cantón, 2 para provincia y `EC` para nación. La clave une las estadísticas con la cartografía; ningún archivo de conteos contiene geometría. Todas las filas llevan `geom_version = "marco-2021"`. Una futura cartografía 2022 requerirá regenerar los tiles, no los conteos.

Las claves de sector con `888` se conservan en las sumas superiores aunque no tengan polígono. `asignado_a_sector` indica que alguna de las 1.852 manzanas reales sin polígono contribuye al sector. El visor debe indicar «población asignada a nivel de sector»; sus 36.040 personas y 18.701 viviendas están incluidas en todas las sumas superiores. `geografia_oculta` señala códigos `888`, sin crearles una geometría.

## Tabla ancha de conteos

Todas las columnas numéricas tienen tipo Parquet `BIGINT` y se suman al agregar cualquier conjunto de unidades. Las columnas de clave, nivel y versión son `VARCHAR`; los tres indicadores de calidad son `BOOLEAN`.

| Columna | Tipo | Población de referencia y significado | Variable fuente del diccionario |
| --- | --- | --- | --- |
| `unit_key` | VARCHAR | Clave de la unidad | `I01`–`I06` |
| `unit_level` | VARCHAR | `manzana`, `sector_disperso`, `sector`, `parroquia`, `canton`, `provincia` o `nacion` | `I01`–`I06` |
| `province_key` | VARCHAR | Provincia; nulo en nación | `I01` |
| `canton_key` | VARCHAR | Cantón; nulo por encima de cantón | `I01`, `I02` |
| `parish_key` | VARCHAR | Parroquia; nulo por encima de parroquia | `I01`–`I03` |
| `sector_key` | VARCHAR | Sector; nulo por encima de sector | `I01`–`I05` |
| `asignado_a_sector` | BOOLEAN | Unidad con población de manzanas sin polígono | Clave `I01`–`I06` contrastada con [QA de match](qa/manzanas_sin_match.csv) |
| `sector_disperso` | BOOLEAN | Unidad que incluye localidad rural sin manzana | `I06` vacío |
| `geografia_oculta` | BOOLEAN | Unidad que incluye clave de geografía reservada | `I04`–`I06` = `888` |
| `geom_version` | VARCHAR | Versión de la unión cartográfica por clave | Marco geográfico 2021 |
| `population` | BIGINT | Personas censadas | Número de registros de Población MANLOC |
| `dwellings` | BIGINT | Viviendas censadas | Número de registros de Vivienda MANLOC |
| `households` | BIGINT | Hogares censados | Número de registros de Hogar MANLOC |
| `emigrants` | BIGINT | Emigrantes registrados | Número de registros de Emigración MANLOC |
| `deaths` | BIGINT | Defunciones registradas | Número de registros de Mortalidad MANLOC |
| `assigned_population` | BIGINT | Personas en las 1.852 manzanas asignadas | Población MANLOC, clave `I01`–`I06` |
| `assigned_dwellings` | BIGINT | Viviendas en las 1.852 manzanas asignadas | Vivienda MANLOC, clave `I01`–`I06` |
| `assigned_households` | BIGINT | Hogares en las 1.852 manzanas asignadas | Hogar MANLOC, clave `I01`–`I06` |
| `assigned_emigrants` | BIGINT | Emigrantes en las 1.852 manzanas asignadas | Emigración MANLOC, clave `I01`–`I06` |
| `assigned_deaths` | BIGINT | Defunciones en las 1.852 manzanas asignadas | Mortalidad MANLOC, clave `I01`–`I06` |
| `assigned_manzanas` | BIGINT | Manzanas reales sin polígono asignadas | [QA de match](qa/manzanas_sin_match.csv) |
| `rural_population` | BIGINT | Personas de localidad rural sin manzana | Población MANLOC, `I06` vacío |
| `masked_population` | BIGINT | Personas con clave geográfica `888` | Población MANLOC, `I04`–`I06` |
| `sex_male` | BIGINT | Personas con sexo codificado `1` | Población MANLOC, `P02` |
| `sex_female` | BIGINT | Personas con sexo codificado `2` | Población MANLOC, `P02` |
| `sex_unknown` | BIGINT | Personas con otro código o sin sexo | Población MANLOC, `P02` |
| `age_sex_unknown` | BIGINT | Personas sin edad de 0 a 120 y sexo `1`/`2` válidos | Población MANLOC, `P03`, `P02` |

Cada fila siguiente identifica **dos columnas `BIGINT` distintas**, una con sufijo `_m` y otra `_f`. La población de referencia es personas con edad en el intervalo y sexo `1` o `2`; las fuentes son `P03` y `P02` de Población MANLOC.

| Columnas | Edades |
| --- | --- |
| `age_00_04_m`, `age_00_04_f` | 0–4 |
| `age_05_09_m`, `age_05_09_f` | 5–9 |
| `age_10_14_m`, `age_10_14_f` | 10–14 |
| `age_15_19_m`, `age_15_19_f` | 15–19 |
| `age_20_24_m`, `age_20_24_f` | 20–24 |
| `age_25_29_m`, `age_25_29_f` | 25–29 |
| `age_30_34_m`, `age_30_34_f` | 30–34 |
| `age_35_39_m`, `age_35_39_f` | 35–39 |
| `age_40_44_m`, `age_40_44_f` | 40–44 |
| `age_45_49_m`, `age_45_49_f` | 45–49 |
| `age_50_54_m`, `age_50_54_f` | 50–54 |
| `age_55_59_m`, `age_55_59_f` | 55–59 |
| `age_60_64_m`, `age_60_64_f` | 60–64 |
| `age_65_69_m`, `age_65_69_f` | 65–69 |
| `age_70_74_m`, `age_70_74_f` | 70–74 |
| `age_75_79_m`, `age_75_79_f` | 75–79 |
| `age_80_84_m`, `age_80_84_f` | 80–84 |
| `age_85_89_m`, `age_85_89_f` | 85–89 |
| `age_90_94_m`, `age_90_94_f` | 90–94 |
| `age_95_99_m`, `age_95_99_f` | 95–99 |
| `age_100_120_m`, `age_100_120_f` | 100–120 |

## Tabla larga de categorías

`categories/finest/` conserva los códigos categóricos disponibles en MANLOC; `categories/sector_only/` añade `P11R` desde SECTOR, por lo que **no** se presenta a escala de manzana. Variables geográficas de alta cardinalidad (`P08P`, `P08C`, `P08Q`, `P0803A`, `P09P`, `P09C`, `P09Q`, `P1001I`) se publican desde cantón en `categories/canton_only/` para contener el tamaño. `categories/sector/`, `parroquia/`, `canton/`, `provincia/` y `nacion/` suman los conteos de sus fuentes pertinentes. [`categories/schema.json`](../web/public/data/counts/v1a/categories/schema.json) enumera los nombres exactos de variables incluidas por tabla y nivel mínimo.

| Columna | Tipo | Población de referencia y significado | Variable fuente del diccionario |
| --- | --- | --- | --- |
| `unit_key`, `unit_level`, `province_key`, `canton_key`, `parish_key`, `sector_key` | VARCHAR | Mismas claves de la tabla ancha | `I01`–`I06` |
| `source_table` | VARCHAR | `poblacion`, `vivienda`, `hogar`, `emigracion`, `mortalidad` o `poblacion_sector`; define el universo del conteo | Tabla homónima del CPV 2022 |
| `variable` | VARCHAR | Nombre exacto de la columna categórica oficial | Variable homónima del diccionario MANLOC o `P11R` del diccionario SECTOR |
| `category` | VARCHAR | Código de categoría observado, sin etiqueta inventada | Valor de `variable`; los nulos no generan fila |
| `n` | BIGINT | Registros del universo de `source_table` en la categoría | Conteo de la variable indicada |
| `geom_version` | VARCHAR | Versión de la unión cartográfica por clave | Marco geográfico 2021 |

Una fila de categoría con `n = 1` sigue siendo un **conteo por geografía y categoría**, no un registro individual. No hay identificadores de persona, hogar ni vivienda, ni combinaciones de categorías cruzadas. Antes de publicar, [`verify_public_artifacts.py`](../pipeline/verify_public_artifacts.py) comprueba extensiones, columnas prohibidas, archivos de 100 MB o más y total de datos del sitio inferior a 900 MB.
