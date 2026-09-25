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

## Cruces nuevos y validación externa de 1B-2

Los cruces de sexo, edad, parentesco, escolaridad, TIC y condición de actividad se calculan una vez en el entorno privado y se exportan **solo como sumas por unidad censal oficial**. Las cifras de 2022 se comparan con el [boletín nacional y tres fichas provinciales](qa/validacion_inec.md). La pirámide y los indicadores de cualquier selección se calculan sobre sumas de numeradores y denominadores. Los valores 888 del INEC no se reetiquetan ni imputan.

El puntaje de acceso digital compuesto suma tres respuestas válidas: alfabetismo digital (`ANALF_DIG=2`), uso de internet (`P2102=1`) y uso de computadora (`P2103=1`). Su denominador es tres veces el número de personas con las tres respuestas válidas. Las brechas por sexo y edad son diferencias entre esos puntajes, en puntos porcentuales. La maternidad adolescente usa mujeres de 15–19 con respuesta válida de hijos nacidos vivos; la paridez nueva usa mujeres de 15–49. El rezago escolar se aproxima con dos o más años aprobados por debajo de `edad−6` entre 8 y 17 años; no pretende reconstruir trayectorias educativas.

La migración interna neta por cantón es entradas menos salidas observadas en la pregunta de residencia hace cinco años (`P09C`). La suma nacional es cero por construcción. Excluye movilidad internacional y personas no nacidas cinco años antes. Los flujos de origen–destino se conservan como matriz agregada, sin registros personales.

## Clasificación, estadística espacial y gemelos

Se estandarizan [40 rasgos sectoriales](fase1b2_report.md) después de limitar extremos a percentiles 1 y 99 de sectores con al menos 100 personas. Las respuestas ausentes se sustituyen por la mediana de esos sectores **solo dentro del modelo**, nunca en los conteos publicados. Una muestra determinista compara `k∈{4,6,8,10}` con silhouette y gap. Se elige el mayor silhouette entre los modelos cuyo gap queda a menos de 0,1 unidades logarítmicas del mejor, con empate hacia el menor `k`. K-means nacional determina supergrupos y un segundo k-means divide cada uno en dos grupos. Los retratos muestran desviaciones estandarizadas respecto de la referencia nacional. Los sectores pequeños reciben grupo para el mapa pero quedan fuera de rankings y búsqueda de gemelos.

El SoVI es **exploratorio**: el primer componente principal de seis rasgos de vulnerabilidad, orientado para que mayor puntuación represente mayor rezago conjunto. No es un índice oficial del INEC. Los pesos, medias, escalas, límites de recorte y varianza explicada constan en `indicators.yaml` y `clusters.json`; para una selección arbitraria se recalculan las seis tasas desde sus conteos sumados y después se aplica la misma transformación en Python y TypeScript.

Moran global y LISA usan los centroides del Marco 2021 y ocho vecinos más cercanos dentro de cada cantón, ponderados por fila, con 99 permutaciones y semilla 2022. Se excluyen del análisis espacial sectores sin polígono o con denominador inferior a 30. Un grupo «alto-alto» significa valor alto rodeado de valores altos en el indicador elegido; el p de permutación es exploratorio y se realizan muchas pruebas locales. El índice de disimilitud educativa por cantón es `½ Σ|bajos_i/bajos_cantón − altos_i/altos_cantón|`, con escolaridad de personas 25+ (baja ≤9 años; alta ≥13). Valores cercanos a cero representan distribuciones sectoriales más parecidas.

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
| Jefatura femenina / Female household headship | 100 × female_heads / all_heads | manzana | 30 | P01, P02 |
| Soledad potencial 65+ / Potential solitude 65+ | 100 × solitary_65 / all_65 | manzana | 30 | P01, P03, TIPO_HOGAR |
| Escolaridad media 25+ / Mean schooling 25+ | 1 × school_years_25 / school_n_25 | manzana | 30 | P03, ESCOLA |
| Salto educativo generacional / Generational education jump | 1 × (school_years_25_34/school_n_25_34 − school_years_55_64/school_n_55_64) | manzana | 30 | P03, ESCOLA |
| Rezago escolar aproximado / Approximate school lag | 100 × school_lag / school_lag_n | manzana | 30 | P03, ESCOLA |
| Brecha digital por sexo / Digital gender gap | 100 × (digital_male_score/digital_male_max − digital_female_score/digital_female_max) | manzana | 30 | P02, P03, P2102, P2103, ANALF_DIG |
| Brecha digital por edad / Digital age gap | 100 × (digital_youth_score/digital_youth_max − digital_senior_score/digital_senior_max) | manzana | 30 | P03, P2102, P2103, ANALF_DIG |
| Brecha de empleo en fuerza laboral / Employment gender gap | 100 × (labour_male_employed/labour_male_force − labour_female_employed/labour_female_force) | manzana | 30 | P02, CONDACT1 |
| Maternidad adolescente 15–19 / Adolescent motherhood 15–19 | 100 × adolescent_mothers / adolescent_women | parroquia | 100 | P02, P03, P3203 |
| Hablantes de lengua indígena / Indigenous language speakers | 100 × indigenous_language / language_eligible | manzana | 30 | P1001, P03 |
| Analfabetismo 15+ / Illiteracy 15+ | 100 × illiterate_15 / literacy_response_15 | manzana | 30 | P03, ANALF |
| Uso individual de internet 5+ / Internet use 5+ | 100 × internet_person_5 / internet_response_5 | manzana | 30 | P03, P2102 |
| Paridez media de mujeres 15–49 / Mean parity women 15–49 | 1 × children_born_15_49 / women_children_response_15_49 | parroquia | 100 | P02, P03, P3203 |
| Migración interna neta entre cantones / Net inter-canton migration | 1000 × internal_net / population | canton | 1000 | P09C, I01, I02 |
| Vulnerabilidad sociodemográfica exploratoria / Exploratory sociodemographic vulnerability | Σ peso_j × (clip(tasa_j, p1, p99) − media_j) / desviación_j | sector | 100 | ESCOLA, ANALF, HAC, P01, P03, P3203, P2102, P02 |

### Indicadores descartados o pendientes

- `health_insurance_coverage`: El diccionario incluye P30 aportes a seguridad social, no cobertura de seguro de salud.
- `demographic_bonus_peak_distance`: Un solo censo no define el pico temporal nacional de la proporción 15–64.

<!-- INDICATOR_CATALOG_END -->
