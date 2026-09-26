# FASE 2C · Variables del censo — revisión del PR

## Fuente y cobertura

[`variables.json`](../web/public/meta/variables.json) se genera con
[`16_variable_catalog.py`](../pipeline/16_variable_catalog.py) desde los tres
diccionarios XLSX del INEC y el clasificador geográfico 2022, todos cotejados
contra [`MANIFEST.json`](../data/MANIFEST.json). Las categorías publicadas se
contrastan con el codebook de agregados del Release. La pregunta española
mantiene el texto del diccionario; los nombres y etiquetas cortas en inglés
se documentan en [`variables_en.tsv`](../pipeline/variables_en.tsv).

| Tabla INEC | Variables con agregado | Sin agregado |
| --- | ---: | ---: |
| Población | 61 | 10 |
| Vivienda | 20 | 0 |
| Hogar | 35 | 0 |
| Emigración | 4 | 0 |
| Mortalidad | 6 | 0 |
| **Total** | **126** | **10** |

Las 10 entradas sin agregado público (`P0402`, `P0403`, `P11`, `P1108`,
`P12`, `P14`, `P17`, `P18`, `P36`, `P37`) aparecen deshabilitadas. No se
presentan como cero. `P11R` se consulta desde sector; las variables de lugar
de nacimiento o residencia de alta cardinalidad se consultan desde cantón.
El clasificador geográfico aporta nombres a las categorías DPA. Para los
códigos de país, ocupación y rama que no traen un catálogo de etiquetas en
las fuentes verificadas, la interfaz conserva el código oficial y lo declara;
no asigna nombres supuestos.

La edad `P03` se entrega en 21 grupos oficiales de cinco años agregados por
unidad. Su media usa puntos medios y se rotula **aproximada**. Los demás
promedios numéricos omiten códigos especiales como `888` del numerador y del
denominador, sin modificar los conteos publicados.

## Entrega bajo demanda y presupuesto

[`17_variable_bundles.py`](../pipeline/17_variable_bundles.py) reemplaza el
Parquet fino que mezclaba todas las variables por 24 archivos provinciales con
bloques gzip consultables mediante HTTP Range. Un índice registra el offset y
longitud de cada variable. La página solicita solo el bloque de la variable
activa y la tabla de claves de su provincia. Los conteos son los agregados
exactos en las unidades oficiales; el roll-up se hace sumando por clave.

| Componente | Antes v2d | Después v2e |
| --- | ---: | ---: |
| Categorías finas mezcladas, Parquet | 122.687.539 B | 0 B |
| Bloques por variable y provincia + índice | 0 B | 99.217.596 B |
| Conteos y Parquet, incluidos otros niveles | 149.529.581 B | 126.059.638 B |
| Tiles | 164.125.611 B | 164.125.611 B |
| Chunks de análisis e indicadores | 134.293.256 B | 134.293.256 B |
| **Datos del sitio** | **447.948.448 B** | **424.478.505 B** |

El bloque mayor de una variable en una provincia es **1.171.306 B**
(Guayas), inferior a 2 MB. En el E2E de `V03` en Quito se descargaron
**575,6 KB** entre índice, tres tablas provinciales de claves y bloques de
variable; las seis respuestas binarias fueron HTTP 206 y la mayor tuvo
**134.357 B**. El bloque mayor de `V03` fue **76,3 KB/provincia**. Una segunda
categoría reutiliza los conteos en caché.

## QA

[`verify_variable_bundles.py`](../pipeline/verify_variable_bundles.py) elige
con semilla 2022 dos variables de cada una de las cinco tablas: `E03`, `E02`,
`H15`, `H1005`, `M05`, `M0201`, `P18R`, `P3201`, `V12`, `V09`. En 24 provincias,
los bloques reproducen sus celdas exactas de manzana y su suma sectorial
contra los agregados intermedios verificados; también se suman a la parroquia
(o al cantón para la variable de esa escala) y reproducen el Parquet exacto y
cada categoría nacional. Controles adicionales: `P11R` sector, `P08P` cantón y `P03` frente a
los 21 grupos nacionales. **Diferencia nacional: cero**; 1.854.649
observaciones de unidad/categoría comprobadas. La QA de conteos conserva
diferencia cero desde sector hasta nación y la auditoría de esquemas rechaza
identificadores de persona.

El E2E local busca “techo”, elige `V03`, cambia la categoría, dibuja un círculo
y comprueba las seis barras de distribución sin errores de consola:
[resultado](capturas/fase2c_variables_e2e.json) ·
[captura](capturas/fase2c_variables_techo.png).
La prueba adicional de `P08P` confirma que un zoom de sector pasa
automáticamente a cantón con aviso visible; `P03` muestra la nota de media
aproximada [captura](capturas/fase2c_min_level_canton.png). Ninguna de las dos
pruebas produjo excepciones JavaScript.

La publicación en Pages espera la aprobación del PR de producto. El
[prerelease público `data-derived-v2e`](https://github.com/diegocevallos-tech/censo-vivo-ecuador/releases/tag/data-derived-v2e)
contiene únicamente agregados. Sus cinco assets se descargaron de nuevo y
restauraron con SHA256 correcto: 398 archivos, 424.478.505 B. La auditoría de
esquemas y la QA aditiva pasaron sobre esta copia descargada.
