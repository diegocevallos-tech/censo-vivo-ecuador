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

<!-- INDICATOR_CATALOG_START -->
## Catálogo de indicadores

Generado desde [`indicators.yaml`](../indicators.yaml). `min_n` es el denominador mínimo para rankings, percentiles y gemelos.

| Indicador (ES / EN) | Fórmula | Nivel mínimo | `min_n` | Fuente |
| --- | --- | --- | ---: | --- |
| Edad mediana aproximada / Approximate median age | Interpolación lineal dentro del grupo quinquenal mediano | manzana | 30 | P03, P02 |
| Índice de envejecimiento / Ageing index | 100 × población 65+ / población 0–14 | manzana | 30 | P03, P02 |
| Dependencia juvenil / Youth dependency | 100 × población 0–14 / población 15–64 | manzana | 30 | P03, P02 |
| Dependencia de mayores / Old-age dependency | 100 × población 65+ / población 15–64 | manzana | 30 | P03, P02 |
| Razón de masculinidad / Sex ratio | 100 × hombres / mujeres | manzana | 30 | P02 |
| Proporción de mujeres / Female share | 100 × mujeres / (mujeres + hombres) | manzana | 30 | P02 |
| Ventana de edad activa / Working-age share | 100 × población 15–64 / población con edad válida | manzana | 30 | P03, P02 |
| Hogares unipersonales / Single-person households | 100 × hogares unipersonales / hogares con tipo válido | manzana | 30 | TIPO_HOGAR |
| Personas por hogar / People per household | Población censada / hogares censados | manzana | 30 | P02, H01 |
| Hacinamiento / Overcrowding | 100 × hogares HAC=1 / hogares HAC válidos | manzana | 30 | HAC |
| Déficit habitacional cualitativo / Qualitative housing deficit | 100 × viviendas DEF_HAB=2 / viviendas clasificadas | manzana | 30 | DEF_HAB |
| Ciudad vacía: viviendas desocupadas / Vacant private dwellings | 100 × V0201=4 / V0201 válido | manzana | 30 | V0201 |
| Tenencia propia / Owner tenure | 100 × H09∈{1,2,3} / H09 válido | manzana | 30 | H09 |
| Tenencia arrendada / Rented tenure | 100 × H09=4 / H09 válido | manzana | 30 | H09 |
| Hogares con internet fijo / Households with fixed internet | 100 × H1004=1 / H1004 válido | manzana | 30 | H1004 |
| Hogares con computadora / Households with a computer | 100 × H1005=1 / H1005 válido | manzana | 30 | H1005 |
| Analfabetismo digital / Digital exclusion | 100 × ANALF_DIG=1 / ANALF_DIG válido | manzana | 30 | ANALF_DIG |
| Ocupación en la fuerza de trabajo / Employment among labour force | 100 × CONDACT1=2 / CONDACT1∈{2,3} | manzana | 30 | CONDACT1 |
| Desocupación / Unemployment rate | 100 × CONDACT1=3 / CONDACT1∈{2,3} | manzana | 30 | CONDACT1 |
| Llegados de otro lugar del país / Domestic arrivals in five years | 100 × P09=2 / P09∈{1,2,3} | manzana | 30 | P09 |
| Índice imán: llegados en cinco años / Magnet index: recent arrivals | 100 × P09∈{2,3} / P09∈{1,2,3} | manzana | 30 | P09 |
| Hogares con emigrantes / Households with emigrants | 100 × H12=1 / H12∈{1,2} | manzana | 30 | H12 |
| Emigrantes por 1.000 habitantes / Emigrants per 1,000 residents | 1.000 × emigrantes / población censada | manzana | 100 | E01, P02 |
| Emigrantes mujeres / Female share among emigrants | 100 × E02=2 / E02∈{1,2} | manzana | 30 | E02 |
| Diversidad de edades / Age diversity | Entropía Shannon normalizada de 21 grupos de edad | manzana | 100 | P03, P02 |
| Diversidad de autoidentificación cultural / Cultural self-identification diversity | Entropía Shannon normalizada de P11R 1–6 | sector | 100 | P11R |
| Paisaje lingüístico / Linguistic landscape | Entropía Shannon normalizada de P10R 1–9 | manzana | 100 | P10R |
| Paridez media registrada / Mean lifetime live births | Σ(k × P3203=k) / Σ(P3203=0..20) | parroquia | 100 | P3203 |
| Defunciones reportadas por 1.000 habitantes / Reported deaths per 1,000 residents | 1.000 × defunciones reportadas / población censada | canton | 1000 | M03, P02 |
| Edad media al morir (reportada) / Mean reported age at death | Σ(k × M03=k) / Σ(M03=0..120) | canton | 30 | M03 |

### Indicadores descartados o pendientes

- `health_insurance_coverage`: El diccionario incluye P30 aportes a seguridad social, no cobertura de seguro de salud.
- `female_headship`: Requiere cruce parentesco de jefatura × sexo; el agregado actual conserva marginales.
- `potential_solitude_65`: Requiere edad × hogar unipersonal; el agregado actual conserva marginales.
- `mean_schooling_25_plus`: Requiere edad × ESCOLA y universo 25+; no existe ese cruce agregado.
- `generational_education_jump`: Requiere edad × ESCOLA para 25–34 y 55–64; no existe ese cruce agregado.
- `school_lag`: Requiere edad × asistencia/nivel escolar; no existe ese cruce agregado.
- `digital_gap_by_sex_age`: Requiere TIC × sexo/edad; no existe ese cruce agregado.
- `labour_gender_gap`: Requiere CONDACT1 × sexo; no existe ese cruce agregado.
- `internal_net_migration`: Requiere matriz origen-destino por cantón; el agregado actual contiene marginales y códigos previos.
- `canton_origin_destination`: Requiere extracción explícita de flujos origen-destino del microdato privado.
- `adolescent_motherhood`: Requiere edad × hijos nacidos vivos; no existe ese cruce agregado.
- `sovi_pca`: Pesos PCA y estandarización nacional corresponden a 1B-2.
- `demographic_bonus_peak_distance`: Un solo censo no define el pico temporal nacional de la proporción 15–64.
- `indigenous_language_speakers`: P10R=9 agrupa combinaciones no separables en el agregado; requiere reconstrucción del indicador desde microdato.

<!-- INDICATOR_CATALOG_END -->
