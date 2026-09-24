# Fase 0: inventario preliminar y bloqueo

Fecha de comprobación: 2026-09-24. **La fase 0 no está terminada.** Se detuvo la adquisición al confirmar variables ausentes en el diccionario oficial de manzana/localidad. El archivo grande de microdatos no se terminó de descargar ni se publicó.

## Fuentes verificadas

El portal [Datos Censo Ecuador](https://www.censoecuador.gob.ec/data-censo-ecuador/) enlaza la base CSV de manzana/localidad, los diccionarios y la guía. El primer enlace del diccionario de manzana en `censoecuador.gob.ec/wp-content/uploads/2025/02/` devolvió HTTP 404 el 2026-09-24. El [enlace alternativo oficial del INEC](https://www.ecuadorencifras.gob.ec/documentos/web-inec/dicc-censo/2022/DICCIONARIO_BDD_MANLOC.xlsx) respondió HTTP 206 a una petición por rango y el archivo se descargó y verificó con SHA256. Los tamaños, hashes y fechas de cada descarga terminada están en [`data/MANIFEST.json`](../data/MANIFEST.json).

El [diccionario de manzana/localidad](https://www.ecuadorencifras.gob.ec/documentos/web-inec/dicc-censo/2022/DICCIONARIO_BDD_MANLOC.xlsx), hoja `5. Población`, fila 7, indica **16.938.986 registros y 91 variables** para la tabla Población. Es un registro por persona, no una tabla agregada. La [página oficial](https://www.censoecuador.gob.ec/data-censo-ecuador/) advierte que la base de manzana excluye identidad étnica, asistencia a educación especial y OSIG por confidencialidad.

## Matriz de disponibilidad en el diccionario de manzana/localidad

`Sí` significa que el código aparece en el diccionario; aún falta contrastarlo con los encabezados CSV y sus valores. Las variables `I01`–`I07` figuran en las cinco tablas.

| Grupo pedido | Estado | Códigos confirmados / motivo |
| --- | --- | --- |
| Geografía | Sí | `I01`–`I07` |
| Sexo, edad, parentesco | Sí | `P02`, `P03`, `P01` |
| Autoidentificación étnica | **No** | No aparece en Población de manzana ni en la hoja principal de sector; exclusión declarada por INEC |
| Idioma | Sí | `P1001`–`P1005`, `P1001I`, `P10R` |
| Lugar de nacimiento | Sí | `P08`, `P08P`, `P08C`, `P08Q` |
| Residencia hace cinco años | Sí | `P09`, `P09P`, `P09C`, `P09Q` |
| Nivel de instrucción y escolaridad | Sí | `P17R`, `P17_CINE`, `P18R`, `ESCOLA` |
| Alfabetismo y alfabetismo digital | Sí | `P19`, `ANALF`, `ANALF_DIG` |
| Asistencia escolar | Sí | `P15` |
| Condición de actividad | Sí | `P22`–`P26`, `CONDACT`, `CONDACT1` |
| Rama y ocupación | Sí | `P27`–`P29`, `RAMA1`, `GRUPO1` |
| Seguro de salud | **No** | No aparece una variable de cobertura de salud; `P30` pregunta por aportes y no equivale a seguro de salud |
| Discapacidad o dificultad funcional | Sí | `P0701`–`P0706`, `DFUNC`, `TDFUNC` |
| Hijos nacidos vivos | Sí | `P3201`–`P3203` |
| Uso de internet, computadora y celular | Sí | `P2101`–`P2103` |
| Condición de ocupación y tipo de vivienda | Sí | `V0201`, `V0202`, `V01` |
| Materiales y estado | Sí | `V03`–`V08` |
| Servicios básicos | Sí | `V09`–`V14`; algunos servicios del hogar en `H02`–`H06`, `H1001`–`H1005` |
| Dormitorios y tenencia | Sí | `H01`, `H09` |
| Emigración: destino, año, sexo, edad | Sí | `E04`, `E01`, `E02`, `E03` |
| Mortalidad: sexo y edad | Sí | `M04`, `M03` |

El diccionario de sector descargado tiene otra hoja llamada `Hoja4`; esta revisión usó su hoja formal `5. Población`. No se infiere disponibilidad por encima del nivel sector sin revisar el diccionario correspondiente.

## Efecto en los indicadores

- **Descartar en manzana y sector** la entropía de Shannon de autoidentificación. Ningún retrato geodemográfico fino ni componente de SoVI puede usar esa variable.
- **Descartar cualquier indicador de seguro de salud** construido desde estas bases. `P30` no debe usarse como sustituto.
- Mantener los demás indicadores como **pendientes de comprobación en CSV**. La presencia en el diccionario no prueba cobertura, valores válidos ni compatibilidad cartográfica.

## Incompatibilidad de publicación que requiere decisión

La instrucción de subir los originales al Release público `data-raw-v1` entra en conflicto con la regla de publicar solo agregados: el archivo `BDD_CPV2022_MANLOC_CSV.zip` contiene registros de personas y las otras cuatro tablas incluyen registros de viviendas, hogares, emigrantes y fallecidos. Subirlo a un Release del repositorio público sería distribuir microdatos. No se ha creado ese Release. Una alternativa compatible es un **repositorio privado** de la misma cuenta para los originales, con un Release privado y acceso autenticado desde `fetch_raw.py`; el repositorio público conservaría solo manifiesto, código y agregados. Requiere definir ese alcance antes de la fase 0.5.

## Verificaciones todavía pendientes

- Descargar y verificar los cinco CSV del ZIP de manzana/localidad, sin publicarlos.
- Confirmar el esquema real y muestras con DuckDB.
- Verificar cartografía de provincia, cantón, parroquia, zona, sector y manzana. El enlace oficial de 2023 conduce al geoportal; se localizó una capa de sectores anonimizados y una geodatabase nacional **2021** como respaldo, pero no se ha comprobado que cubran las unidades de 2022.
- Calcular el match de claves de manzana y sector por provincia y exigir >95%.
- Verificar totales poblacionales oficiales, permisos de redistribución y política CORS antes de publicar agregados.
