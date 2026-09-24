# Fase 0: fuentes, variables y compatibilidad geográfica

Comprobación: 2026-09-24. Todos los números de este informe proceden de archivos oficiales del INEC. Los originales y los resultados intermedios con posible detalle individual permanecen fuera del repositorio público. La procedencia, el tamaño y el SHA256 de cada original constan en [`data/MANIFEST.json`](../data/MANIFEST.json).

## Fuentes y esquema

Se descargó el [ZIP oficial de manzana/localidad](https://www.ecuadorencifras.gob.ec/documentos/web-inec/bd-censo/manzana/BDD_CPV2022_MANLOC_CSV.zip), con los CSV de Población, Vivienda, Hogar, Emigración y Mortalidad. Se contrastaron sus encabezados con las cinco hojas del [diccionario oficial](https://www.ecuadorencifras.gob.ec/documentos/web-inec/dicc-censo/2022/DICCIONARIO_BDD_MANLOC.xlsx) y se leyeron 100 filas de cada CSV con DuckDB. Los encabezados coinciden exactamente:

| Tabla | Columnas CSV y diccionario | Muestra DuckDB |
| --- | ---: | ---: |
| Población | 91 | 100 |
| Vivienda | 38 | 100 |
| Hogar | 53 | 100 |
| Emigración | 20 | 100 |
| Mortalidad | 22 | 100 |

La suma de personas por provincia obtenida del CSV completo es **16.938.986**, igual al total nacional publicado por el INEC y al número de registros descrito en el diccionario. Esta es una comprobación nacional; la tolerancia de <0,5 % por provincia y cantón corresponde al QA de la fase 1. Los procesos reproducibles están en [`pipeline/00_validate_sources.py`](../pipeline/00_validate_sources.py) y [`pipeline/00_geography_keys.py`](../pipeline/00_geography_keys.py).

El enlace del diccionario en `censoecuador.gob.ec` devolvió 404 y el de la guía PDF devolvió 403 desde GitHub Actions. Se usaron copias oficiales verificadas en `ecuadorencifras.gob.ec` cuando estuvieron disponibles. La guía original, descargada localmente y verificada, se recupera del Release privado durante la reproducción.

## Matriz de disponibilidad

`Sí` significa presencia simultánea en el diccionario y en el encabezado del CSV correspondiente. No implica que todas las categorías tengan observaciones válidas en cada unidad pequeña. `I01`–`I07` aparecen en las cinco tablas.

| Grupo pedido | Estado | Códigos confirmados / observación |
| --- | --- | --- |
| Geografía | Sí | `I01`–`I07` |
| Sexo, edad, parentesco | Sí | `P02`, `P03`, `P01` |
| Autoidentificación étnica | **No** | Excluida de la base de manzana/localidad por confidencialidad |
| Idioma | Sí | `P1001`–`P1005`, `P1001I`, `P10R` |
| Lugar de nacimiento | Sí | `P08`, `P08P`, `P08C`, `P08Q` |
| Residencia hace cinco años | Sí | `P09`, `P09P`, `P09C`, `P09Q` |
| Nivel de instrucción y escolaridad | Sí | `P17R`, `P17_CINE`, `P18R`, `ESCOLA` |
| Alfabetismo y alfabetismo digital | Sí | `P19`, `ANALF`, `ANALF_DIG` |
| Asistencia escolar | Sí | `P15` |
| Condición de actividad | Sí | `P22`–`P26`, `CONDACT`, `CONDACT1` |
| Rama y ocupación | Sí | `P27`–`P29`, `RAMA1`, `GRUPO1` |
| Seguro de salud | **No** | `P30` registra aportes y no equivale a cobertura de seguro de salud |
| Discapacidad o dificultad funcional | Sí | `P0701`–`P0706`, `DFUNC`, `TDFUNC` |
| Hijos nacidos vivos | Sí | `P3201`–`P3203` |
| Internet, computadora y celular | Sí | `P2101`–`P2103` |
| Ocupación y tipo de vivienda | Sí | `V0201`, `V0202`, `V01` |
| Materiales y estado | Sí | `V03`–`V08` |
| Servicios básicos | Sí | `V09`–`V14`, `H02`–`H06`, `H1001`–`H1005` |
| Dormitorios y tenencia | Sí | `H01`, `H09` |
| Emigración: destino, año, sexo, edad | Sí | `E04`, `E01`, `E02`, `E03` |
| Mortalidad: sexo y edad | Sí | `M04`, `M03` |

Se **descarta la entropía de autoidentificación étnica** a nivel de manzana y sector, así como su uso en los retratos geodemográficos finos o en SoVI. Se **descarta cualquier indicador de seguro de salud** basado en estos CSV. Las demás propuestas de indicadores quedan sujetas a definiciones de denominador, valores válidos y umbrales en la fase 1. La [página de datos del INEC](https://www.censoecuador.gob.ec/data-censo-ecuador/) declara expresamente la exclusión de identidad étnica en la base de manzana.

## Compatibilidad de claves con la cartografía

Se usó la [capa oficial de sectores anonimizados](https://www.ecuadorencifras.gob.ec/documentos/web-inec/capa/CapaSectores.zip) para sectores y la [geodatabase nacional 2021](https://www.ecuadorencifras.gob.ec/documentos/web-inec/Geografia_Estadistica/Documentos/GEODATABASE_NACIONAL_2021.zip) para manzanas. Esta última es el respaldo indicado para la fase 0; sus polígonos son anteriores al censo 2022. Contiene capas `zon_a`, `sec_a` y `man_a`, pero no capas administrativas independientes de provincia, cantón y parroquia. Estas pueden derivarse por disolución de sectores según el clasificador 2022, con validación posterior. El [servicio oficial de cartografía censal 2022](https://idgn.ecuadorencifras.gob.ec/server/rest/services/Cartografia_Censal_WMS_2022/MapServer) anuncia todos los niveles, incluida manzana, pero devolvió HTTP 500 en las consultas de metadatos y conteo realizadas el 2026-09-24. No se trató como descarga validada.

El [manual oficial](https://www.ecuadorencifras.gob.ec/documentos/web-inec/bd-censo/5.GUIA_BASE_CPV_2022_v6.pdf) explica que `888` es una clave geográfica ocultada por confidencialidad. Tales claves no representan un polígono recuperable: se contabilizan por separado y se excluyen del denominador del match. No se fabricaron geometrías para ellas. Para manzanas se evalúan solo registros con `I06` de manzana; las localidades rurales (`I07`) no son manzanas. La tabla cuenta claves distintas del censo, no filas de personas.

| Provincia (código) | Sectores encontrados / comparables | Match sector | Manzanas encontradas / comparables | Match manzana | Claves manzana ocultas |
| --- | ---: | ---: | ---: | ---: | ---: |
| 01 | 3290 / 3290 | 100,000 % | 7212 / 7243 | 99,572 % | 128 |
| 02 | 866 / 866 | 100,000 % | 1964 / 1973 | 99,544 % | 33 |
| 03 | 1085 / 1085 | 100,000 % | 3118 / 3127 | 99,712 % | 74 |
| 04 | 563 / 563 | 100,000 % | 2442 / 2447 | 99,796 % | 37 |
| 05 | 1951 / 1951 | 100,000 % | 3557 / 3578 | 99,413 % | 60 |
| 06 | 2172 / 2172 | 100,000 % | 5601 / 5616 | 99,733 % | 88 |
| 07 | 2115 / 2115 | 100,000 % | 12079 / 12264 | 98,492 % | 177 |
| 08 | 1747 / 1747 | 100,000 % | 7057 / 7106 | 99,310 % | 102 |
| 09 | 11457 / 11457 | 100,000 % | 52185 / 52476 | 99,445 % | 480 |
| 10 | 1426 / 1426 | 100,000 % | 6257 / 6273 | 99,745 % | 106 |
| 11 | 1849 / 1849 | 100,000 % | 6346 / 6392 | 99,280 % | 114 |
| 12 | 2697 / 2697 | 100,000 % | 10762 / 10847 | 99,216 % | 136 |
| 13 | 4788 / 4788 | 100,000 % | 21826 / 22065 | 98,917 % | 376 |
| 14 | 882 / 882 | 100,000 % | 2708 / 2746 | 98,616 % | 85 |
| 15 | 470 / 470 | 100,000 % | 1579 / 1589 | 99,371 % | 35 |
| 16 | 431 / 431 | 100,000 % | 1191 / 1220 | 97,623 % | 28 |
| 17 | 8465 / 8465 | 100,000 % | 27794 / 27895 | 99,638 % | 197 |
| 18 | 2222 / 2222 | 100,000 % | 5350 / 5367 | 99,683 % | 61 |
| 19 | 466 / 466 | 100,000 % | 1890 / 1930 | 97,927 % | 61 |
| 20 | 114 / 114 | 100,000 % | 706 / 706 | 100,000 % | 14 |
| 21 | 723 / 723 | 100,000 % | 3116 / 3131 | 99,521 % | 71 |
| 22 | 649 / 649 | 100,000 % | 2907 / 2944 | 98,743 % | 65 |
| 23 | 1435 / 1435 | 100,000 % | 7118 / 7142 | 99,664 % | 83 |
| 24 | 1040 / 1040 | 100,000 % | 9281 / 9336 | 99,411 % | 288 |
| **Nacional** | **52.903 / 52.903** | **100,000 %** | **204.046 / 205.413** | **99,335 %** | **2.899** |

El mínimo provincial es **97,623 %** de manzanas comparables (código 16); se cumple el objetivo de >95 % en las 24 provincias. La coincidencia de clave no prueba que los límites poligonales 2021 sean idénticos a 2022. En fase 1 habrá que cuantificar el impacto espacial, decidir cómo representar las 1.367 manzanas comparables sin polígono y preservar los conteos agregados de claves ocultas en unidades mayores sin revelar localizaciones.

## Reproducción y límites

Los originales se almacenan en el Release privado `data-raw-v1` del repositorio `diegocevallos-tech/censo-vivo-ecuador-raw`, autorizado por el propietario. El repositorio público guarda únicamente manifiesto y código de descarga. [`pipeline/fetch_raw.py`](../pipeline/fetch_raw.py) usa `gh release download`, verifica tamaño y SHA256, y recompone el ZIP de geodatabase dividido en dos partes menores de 2 GiB. Los CSV individuales, el GPKG extraído y la base DuckDB permanecen en rutas ignoradas por Git. El ZIP de geodatabase nunca entra en el historial de git ni en LFS.

El extracto OSM de Geofabrik queda registrado para contexto visual posterior y la base CPV 2010 para la fase 5 opcional; ninguno interviene en los cálculos ni en el match de esta fase. Sus URLs se registran como fuentes diferidas en el manifiesto, sin atribuirles tamaño, hash o fecha de descarga inexistentes.

Se verificó la restricción CORS con una petición `GET` de rango `bytes=0-0` y cabecera `Origin: https://diegocevallos-tech.github.io` a un [asset público de GitHub Releases](https://github.com/duckdb/duckdb/releases/download/v1.5.5/duckdb_cli-linux-amd64.zip). La redirección respondió `302` y el asset respondió `206 Partial Content`, sin cabecera `Access-Control-Allow-Origin` en ninguna respuesta. No se usarán assets de Releases como fuente del navegador; los agregados que cargue la web se alojarán en GitHub Pages. El Release privado tampoco es accesible de forma anónima.

Entorno de comprobación: Python 3.12 local para validación; Codespaces configura Python 3.11 y Node 20. Se comprobaron `npm run build`, `npm audit` (0 vulnerabilidades) y `python -m compileall`; el devcontainer completo no se pudo iniciar en este equipo por falta de Docker.
