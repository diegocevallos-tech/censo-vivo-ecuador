# Los que se fueron

**ID de la Historia:** `02_los_que_se_fueron`  
**Descripción:** Geografía de la emigración internacional reciente, asimetría de género en edades activas y concentración en el Austro.

---

## Paso 1: El registro censal de la ausencia: 96.825 emigrantes

**English Title:** *The Census Record of Absence: 96,825 Emigrants*

El Censo 2022 registró 96.825 personas que emigraron del Ecuador en el periodo intercensal reciente, reportadas de forma directa por los hogares que permanecen en el país. Esta cifra censal refleja la magnitud de las familias con ausencias internacionales y constituye el punto de partida para examinar la distribución territorial de los hogares con migrantes.

**Resumen en inglés:** 96,825 emigrants were reported by remaining resident households nationwide in CPV 2022.  

**Cifra clave:** `96825 personas` (Fuente: *INEC CPV 2022, nacion/data.parquet (sum(emigrants))*)

```sql
SELECT sum(emigrants) AS total_emigrants FROM 'data/derived/counts/v1b1/nacion/data.parquet';
```

```json
{
  "nivel": "nacion",
  "centro": [
    -78.1834,
    -1.8312
  ],
  "zoom": 6.2,
  "indicador": "emigrant_households",
  "filtro": null,
  "capa_extra": null,
  "resaltados": [
    "EC"
  ]
}
```

---

## Paso 2: El epicentro del Austro: Cañar y Azuay

**English Title:** *The Austro Epicenter: Cañar and Azuay*

La concentración geográfica de la emigración se localiza con nitidez en las provincias del Austro. Cañar registra una tasa provincial de 38,76 emigrantes por cada mil habitantes (8.820 personas sobre 227.578 residentes). En Azuay, la tasa alcanza 28,13 por mil (22.550 emigrantes sobre 801.609 personas), conformando el núcleo de mayor intensidad emigratoria del país.

**Resumen en inglés:** Cañar (38.76 per thousand) and Azuay (28.13 per thousand) concentrate the highest emigration rates in Ecuador.  

**Cifra clave:** `38.76 emigrantes por 1.000 habitantes` (Fuente: *INEC CPV 2022, provincia/data.parquet (unit_keys: '03', '01')*)

```sql
SELECT province_key, sum(emigrants) * 1000.0 / sum(population) AS rate_per_1000 FROM 'data/derived/counts/v1b1/provincia/data.parquet' WHERE province_key IN ('03', '01') GROUP BY province_key;
```

```json
{
  "nivel": "provincia",
  "centro": [
    -78.95,
    -2.75
  ],
  "zoom": 8.5,
  "indicador": "emigrant_households",
  "filtro": "province_key IN ('03', '01')",
  "capa_extra": null,
  "resaltados": [
    "03",
    "01"
  ]
}
```

---

## Paso 3: Intensidad cantonal máxima: Chunchi, Chimborazo

**English Title:** *Maximum Cantonal Intensity: Chunchi, Chimborazo*

En el cantón Chunchi, provincia de Chimborazo, el 7,29% de la población censada fue reportada como emigrante en el exterior (775 personas frente a 10.635 habitantes residentes). Es la tasa cantonal de salida relativa más elevada del Ecuador, evidenciando que el fenómeno migratorio también impacta con severidad a cantones rurales de la Sierra centro.

**Resumen en inglés:** Chunchi (Chimborazo) registers Ecuador's highest cantonal emigration rate at 7.29% of its census population.  

**Cifra clave:** `7.29 % de emigrantes sobre población residente` (Fuente: *INEC CPV 2022, canton/data.parquet (unit_key='0605')*)

```sql
SELECT unit_key, emigrants, population, emigrants * 100.0 / population AS pct_emigrants FROM 'data/derived/counts/v1b1/canton/data.parquet' WHERE unit_key = '0605';
```

```json
{
  "nivel": "canton",
  "centro": [
    -78.91,
    -2.29
  ],
  "zoom": 10.0,
  "indicador": "emigrant_households",
  "filtro": "unit_key = '0605'",
  "capa_extra": null,
  "resaltados": [
    "0605"
  ]
}
```

---

## Paso 4: Perfil de salida: edad, género y destinos principales

**English Title:** *Departure Profile: Age, Gender, and Key Destinations*

La emigración censal captura la salida de población en edades activas hacia destinos tradicionales. En cantones como Santa Isabel y Biblián, la información censal de salida detalla los países de destino y los tramos de edad. La disponibilidad de estos agregados cruzados permite desagregar los flujos por cohortes quinquenales en los tabulados especializados.

**Resumen en inglés:** Detailed cross-tabulation of emigrants by age of departure, sex, and destination country in Santa Isabel and Biblián.  

**Cifra clave:** `[PENDIENTE: agregado de Emigración por cantón × sexo × edad de salida × país de destino] personas emigrantes` (Fuente: *INEC CPV 2022, Cuestionario Censal Sección 4 (E01-E04)*)

```sql
-- [PENDIENTE: agregado de Emigración por cantón × sexo × edad de salida × país de destino]
SELECT canton_key, count(*) FROM emigracion_microdatos GROUP BY canton_key;
```

```json
{
  "nivel": "canton",
  "centro": [
    -79.15,
    -3.05
  ],
  "zoom": 9.2,
  "indicador": "emigrant_households",
  "filtro": "unit_key IN ('0109', '0303')",
  "capa_extra": "arcos_migratorios",
  "resaltados": [
    "0109",
    "0303"
  ]
}
```

---

## Paso 5: El giro demográfico: la asimetría de género en edades productivas

**English Title:** *The Demographic Twist: Gender Asymmetry in Productive Ages*

La huella más nítida de la emigración se observa en la estructura etaria local. En el cantón Santa Isabel (Azuay), la razón de masculinidad para el grupo de 20 a 39 años desciende a 69,99 varones por cada 100 mujeres (2.628 hombres frente a 3.755 mujeres). En Biblián se ubica en 76,07, confirmando un déficit pronunciado de población masculina en edad laboral.

> **Hipótesis:** En cantones con marcada pérdida de población masculina en edades productivas, las familias receptoras de remesas concentran la jefatura de hogar y las responsabilidades del cuidado en mujeres y abuelos. (el censo no lo mide). [Banco Central del Ecuador (BCE), 2024, pág. 8](https://contenido.bce.fin.ec/documentos/Estadisticas/SectorExterno/BalanzaPagos/Remesas/ere2023IV.pdf).
>
> *Cita textual:* «Esta participación se atribuye a la presencia de un considerable número de hogares beneficiarios en estas áreas geográficas, así como a la disponibilidad de entidades financieras y empresas remesadoras que ofrecen servicios de pago de remesas en dichas localidades contribuyó a la consolidación de estas provincias como centros clave en la recepción de remesas, con base a la investigación de campo efectuada por el Banco Central del Ecuador.»

**Resumen en inglés:** In Santa Isabel (Azuay), sex ratio for ages 20-39 drops to 69.99 males per 100 females (2,628 vs 3,755).  

**Cifra clave:** `69.99 hombres por cada 100 mujeres` (Fuente: *INEC CPV 2022, canton/data.parquet (unit_keys: '0109', '0303')*)

```sql
SELECT unit_key, (age_20_24_m + age_25_29_m + age_30_34_m + age_35_39_m) * 100.0 / (age_20_24_f + age_25_29_f + age_30_34_f + age_35_39_f) AS male_ratio_20_39 FROM 'data/derived/counts/v1b1/canton/data.parquet' WHERE unit_key IN ('0109', '0303');
```

```json
{
  "nivel": "canton",
  "centro": [
    -79.31,
    -3.27
  ],
  "zoom": 10.0,
  "indicador": "male_ratio",
  "filtro": "unit_key IN ('0109', '0303')",
  "capa_extra": null,
  "resaltados": [
    "0109",
    "0303"
  ]
}
```

---

## Paso 6: La frontera migratoria amazónica: Morona Santiago

**English Title:** *The Amazonian Migration Frontier: Morona Santiago*

La salida internacional no es exclusiva de los Andes. En la provincia amazónica de Morona Santiago, la tasa de emigración alcanza 16,94 por mil habitantes (3.261 emigrantes sobre 192.508 habitantes), superando a provincias serranas como Tungurahua (14,64) y Pichincha (7,72). Este dato corrobora la extensión del fenómeno hacia la cuenca oriental.

**Resumen en inglés:** Morona Santiago records 16.94 emigrants per thousand (3,261 total), surpassing central Sierra provinces.  

**Cifra clave:** `16.94 emigrantes por 1.000 habitantes` (Fuente: *INEC CPV 2022, provincia/data.parquet (unit_key='14')*)

```sql
SELECT province_key, emigrants * 1000.0 / population AS rate_per_1000 FROM 'data/derived/counts/v1b1/provincia/data.parquet' WHERE province_key = '14';
```

```json
{
  "nivel": "provincia",
  "centro": [
    -78.11,
    -2.55
  ],
  "zoom": 8.0,
  "indicador": "emigrant_households",
  "filtro": "province_key = '14'",
  "capa_extra": null,
  "resaltados": [
    "14"
  ]
}
```

---

## Paso 7: La contrapartida interna: Daule y los que llegan

**English Title:** *The Domestic Counterpart: Daule and Inward Migration*

Frente a las zonas de expulsión internacional, cantones periurbanos actúan como receptores internos de población. En el cantón Daule (Guayas), 34.664 personas reportaron residir en otro cantón hace cinco años. La dinámica demográfica ecuatoriana combina simultáneamente salidas internacionales en zonas rurales y traslados internos hacia periferias metropolitanas de la Costa.

**Resumen en inglés:** While the Sierra expels population abroad, coastal cantons like Daule receive 34,664 internal migrants.  

**Cifra clave:** `34664 personas` (Fuente: *INEC CPV 2022, interim cross_counts (unit_key='0906')*)

```sql
SELECT canton_key, sum(residence_other_canton_5) AS internal_migrants FROM cross_counts_v1b2 WHERE canton_key = '0906' GROUP BY canton_key;
```

```json
{
  "nivel": "canton",
  "centro": [
    -79.98,
    -1.98
  ],
  "zoom": 10.5,
  "indicador": "emigrant_households",
  "filtro": "unit_key = '0906'",
  "capa_extra": null,
  "resaltados": [
    "0906"
  ]
}
```

---

## Paso 8: ¿Cómo sostener comunidades con vacíos generacionales?

**English Title:** *How Can Communities With Generational Voids Be Sustained?*

Los datos censales confirman pérdidas de hasta un tercio de la población masculina joven en cantones del Austro andino. Ante este escenario, ¿cómo deben adaptarse las políticas de empleo rural, los sistemas de cuidados y la educación para comunidades donde faltan generaciones intermedias completas?

**Resumen en inglés:** Policy dilemma regarding economic viability and local care structures in cantons with pronounced demographic imbalances.  

**Cifra clave:** `N/A reflexión analítica` (Fuente: *Censo Ecuador 2022*)

```json
{
  "nivel": "canton",
  "centro": [
    -78.95,
    -2.75
  ],
  "zoom": 8.0,
  "indicador": "male_ratio",
  "filtro": null,
  "capa_extra": null,
  "resaltados": []
}
```

---
