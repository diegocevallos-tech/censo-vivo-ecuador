# Fase 0: fuentes, cobertura y acceso

Comprobación: 24 de septiembre de 2026. Los resultados proceden de archivos oficiales del INEC y son reproducibles con [`pipeline/00_check.py`](../pipeline/00_check.py). El tamaño, SHA256 y origen constan en [`data/MANIFEST.json`](../data/MANIFEST.json). Los originales permanecen en el Release privado; el repositorio público contiene solo código, documentación y agregados.

## Fuentes y esquema

Se contrastaron los encabezados de cinco tablas MANLOC con el diccionario oficial. DuckDB leyó 100 filas por tabla: Población 91 columnas, Vivienda 38, Hogar 53, Emigración 20 y Mortalidad 22; los encabezados coinciden exactamente. Se inspeccionaron también las cinco tablas SECTOR y CANTÓN y sus diccionarios: Población tiene 92 y 100 columnas respectivamente. Los tres ZIP superaron la comprobación de integridad.

## Matriz de disponibilidad por desagregación

`Sí` indica presencia en encabezado y diccionario, sin garantizar observaciones válidas en cada unidad. MANLOC llega a manzana/localidad, SECTOR a sector y CANTÓN a cantón. El nivel mínimo de cada indicador queda en [`indicators.yaml`](../indicators.yaml).

| Grupo | MANLOC | SECTOR | CANTÓN | Variables y decisión |
| --- | --- | --- | --- | --- |
| Geografía | Sí | Sí | Sí | MANLOC `I01`–`I07`; SECTOR `I01`–`I05`; CANTÓN `I01`–`I02` |
| Sexo, edad, parentesco | Sí | Sí | Sí | `P02`, `P03`, `P01` |
| Autoidentificación étnica | No | **Sí** | **Sí** | `P11R`; entropía desde sector |
| Idioma | Sí | Sí | Sí | `P1001`–`P1005`, `P10R` |
| Lugar de nacimiento | Sí | Sí | Sí | `P08` y códigos asociados |
| Residencia hace cinco años | Sí | Sí | Sí | `P09` y códigos asociados |
| Instrucción y escolaridad | Sí | Sí | Sí | `P17R`, `P18R`, `ESCOLA` |
| Alfabetismo y alfabetismo digital | Sí | Sí | Sí | `P19`, `ANALF`, `ANALF_DIG` |
| Asistencia escolar | Sí | Sí | Sí | `P15` |
| Condición de actividad | Sí | Sí | Sí | `CONDACT`, `CONDACT1` |
| Rama y ocupación | Sí | Sí | Sí | `RAMA1`, `GRUPO1` |
| Seguro de salud | **No** | **No** | **No** | `P30` mide aportes a seguridad social, no cobertura de salud |
| Dificultad funcional | Sí | Sí | Sí | `P0701`–`P0706`, `DFUNC` |
| Hijos nacidos vivos | Sí | Sí | Sí | `P3201`–`P3203` |
| Internet, computadora, celular | Sí | Sí | Sí | `P2101`–`P2103` |
| Ocupación y tipo de vivienda | Sí | Sí | Sí | `V0201`, `V0202`, `V01` |
| Materiales y estado | Sí | Sí | Sí | `V03`–`V08` |
| Servicios básicos | Sí | Sí | Sí | `V09`–`V14`, `H02`–`H06` |
| Dormitorios y tenencia | Sí | Sí | Sí | `H01`, `H09` |
| Emigración: destino, año, sexo, edad | Sí | Sí | Sí | `E04`, `E01`, `E02`, `E03` |
| Mortalidad: sexo y edad | Sí | Sí | Sí | `M04`, `M03` |

La diversidad étnica se conserva desde **sector**; el visor deberá deshabilitarla en manzana y explicar el motivo. Se descarta cualquier indicador de cobertura de seguro de salud basado en estas fuentes. Los demás índices requieren pruebas de denominadores en fase 1.

## Cobertura de polígonos y conteos

Se cotejaron sectores con la capa oficial de sectores anonimizados y manzanas con la geodatabase 2021 de respaldo. Primero se probó el [servicio ArcGIS REST oficial de 2022](https://idgn.ecuadorencifras.gob.ec/server/rest/services/Cartografia_Censal_WMS_2022/MapServer): metadatos `MapServer?f=json` y consultas GeoJSON paginadas de parroquia, zona, sectores y manzana (`where=1=1`, `outFields=*`, `returnGeometry=true`, `resultOffset`, `resultRecordCount`). [`pipeline/00b_fetch_carto2022.py`](../pipeline/00b_fetch_carto2022.py) registró cinco intentos por petición con backoff exponencial: **35 de 35 recibieron HTTP 500; cero páginas descargadas**. El detalle está en [`docs/qa/carto2022_attempts.csv`](qa/carto2022_attempts.csv). La [issue #42](https://github.com/diegocevallos-tech/censo-vivo-ecuador/issues/42) queda abierta.

El sector tuvo **52.946/52.946 claves comparables con match (100 %)**. Se contaron manzanas con personas y manzanas que solo figuran en Vivienda. La cobertura usa 211.225 claves comparables y excluye 2.899 claves `888` ocultas por el INEC. Los porcentajes ponderados tienen como denominador todas las personas o viviendas con registro de manzana, incluidas las claves `888`, para no exagerar la cobertura. Las localidades rurales no se tratan como manzanas.

| Provincia | Manzanas con match | Población con match | Viviendas con match | Manzanas sin polígono |
| --- | ---: | ---: | ---: | ---: |
| 01 | 99.324 % | 99.544 % | 99.539 % | 51 |
| 02 | 99.554 % | 99.322 % | 99.461 % | 9 |
| 03 | 99.283 % | 99.345 % | 99.384 % | 24 |
| 04 | 99.677 % | 99.719 % | 99.755 % | 8 |
| 05 | 99.429 % | 99.475 % | 99.621 % | 21 |
| 06 | 99.725 % | 99.652 % | 99.779 % | 16 |
| 07 | 97.811 % | 99.286 % | 99.144 % | 276 |
| 08 | 99.282 % | 99.251 % | 99.248 % | 52 |
| 09 | 99.161 % | 99.727 % | 99.614 % | 449 |
| 10 | 99.72 % | 99.677 % | 99.771 % | 18 |
| 11 | 99.277 % | 99.306 % | 99.499 % | 48 |
| 12 | 98.962 % | 99.44 % | 99.196 % | 114 |
| 13 | 98.623 % | 99.337 % | 99.289 % | 314 |
| 14 | 98.576 % | 97.843 % | 98.686 % | 42 |
| 15 | 99.215 % | 99.336 % | 99.527 % | 13 |
| 16 | 97.381 % | 97.81 % | 98.115 % | 33 |
| 17 | 99.599 % | 99.821 % | 99.809 % | 113 |
| 18 | 99.69 % | 99.789 % | 99.828 % | 17 |
| 19 | 96.964 % | 98.46 % | 98.192 % | 62 |
| 20 | 100.0 % | 99.623 % | 99.779 % | 0 |
| 21 | 99.534 % | 99.004 % | 99.231 % | 15 |
| 22 | 98.779 % | 98.071 % | 98.619 % | 37 |
| 23 | 99.64 % | 99.722 % | 99.759 % | 26 |
| 24 | 99.089 % | 99.134 % | 99.023 % | 94 |
| **Nacional** | **99.123 %** | **99.573 %** | **99.541 %** | **1852** |

Las **1.852 manzanas reales sin polígono** están en [`docs/qa/manzanas_sin_match.csv`](qa/manzanas_sin_match.csv), con clave de manzana, sector y población agregada. Todas tienen polígono de sector. En fase 1, sus 36.040 personas y 18.701 viviendas se asignarán al sector correspondiente y el visor mostrará **«población asignada a nivel de sector»**. Otras 20.221 personas y 4.595 viviendas figuran en claves de manzana `888`; se conservan como agregado de sector, sin manzana inventada. Las claves de sector `888` se conservan agregadas para niveles superiores sin polígono sectorial inventado. Ninguna población se descarta. Los conteos nacionales de sectores dan **16.938.986 personas y 6.611.555 viviendas**, exactamente los totales oficiales; los roll-ups de parroquia, cantón y provincia conservan esos totales. La fase 1 verificará cada unidad frente a su total oficial.

La coincidencia de claves no demuestra identidad de límites entre 2021 y 2022. Toda interpretación espacial fina debe indicar la versión cartográfica.

## Verificación del entorno y acceso

El flujo y los permisos se explican en [`docs/data-access.md`](data-access.md). El repositorio público no usa un secret de acceso al almacén privado ni un PAT. El `GITHUB_TOKEN` automático del workflow privado lee `data-raw-v1`; solo su job de publicación escribe en el Release propio. Los workflows públicos leen únicamente `web/public/data/` versionado. El [run privado exitoso](https://github.com/diegocevallos-tech/censo-vivo-ecuador-raw/actions/runs/36052695468) restauró y verificó los 12 assets, ejecutó `00_check.py --sample` y el QA completo, pasó el control de publicación y produjo [`web/public/data/fase0_qa.json`](../web/public/data/fase0_qa.json). El artifact retiene agregados siete días; el mismo archivo se publicó en el Release privado `data-derived-v0`. Se descargó localmente, se comprobó su SHA256 `b283c4fcee85c686b75daad25950bc2bd23b9596b9ac1d34a6e8c2aa157dbd87`, su esquema agregado (24 filas provinciales) y sus totales antes de incorporarlo al PR público.

Se auditó `git log --all --stat` y los blobs alcanzables con `git rev-list --objects --all` y `git cat-file -s`: **cero archivos `.csv`, `.sav`, `.zip` o `.parquet` mayores de 1 MiB** en el historial público. Los únicos dos blobs de esas extensiones son los CSV de QA de 2.077 y 58.458 bytes. `data/raw/` y `data/interim/` permanecen ignorados. [`pipeline/verify_public_artifacts.py`](../pipeline/verify_public_artifacts.py) rechaza archivos crudos, columnas de registro y assets de 100 MB o más. Los Releases no se usan en el navegador: una prueba `GET` con `Origin` y rango sobre un asset público recibió 302/206 sin `Access-Control-Allow-Origin`; además, el almacén original es privado.

Docker Desktop no estaba instalado en el equipo local (`docker version` no existía). La prueba equivalente se hizo con **devcontainer CLI en el [CI público](https://github.com/diegocevallos-tech/censo-vivo-ecuador/actions/runs/36051163826)** y un Codespace de tipo `basicLinux32gb` (**2 CPU, 8 GB RAM, 32 GB de almacenamiento**). El Codespace se creó a las 19:53:24 UTC y completó configuración, comprobación de versiones, cinco tests Python y build web a las 20:02:24 UTC: **9 minutos en total**. Versiones comprobadas dentro del contenedor: Python 3.11.13, Node 20.20.2, DuckDB CLI 1.5.5, tippecanoe 2.79.0, PMTiles 1.31.2 y mapshaper 0.7.67. El build web produjo 0,89 kB de JavaScript inicial. La prueba de Codespaces queda **equivalente validada por devcontainer CLI** y ejecución en el Codespace. Los originales no se introdujeron en el workflow ni el Codespace públicos; `fetch_raw.py`, `00_check.py --sample` y el QA completo se ejecutan en el workflow privado con el token automático de ese repositorio. No se transfirió un token personal.

El extracto OSM y CPV 2010 quedan diferidos según el manifiesto. No se simularon datos.
