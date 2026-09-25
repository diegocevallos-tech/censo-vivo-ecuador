# Guion de Scrollytelling: Los que se fueron

**Identificador:** `02_los_que_se_fueron`  
**Tema Central:** La geografía del éxodo internacional y la movilidad territorial que reconfigura los hogares y la composición por sexo y edad en el Ecuador.  
**Número de pasos:** 8  
**Giro contraintuitivo comprobado:** *La emigración internacional muestra una fuerte asimetría demográfica: en cantones de alta emigración del Austro como Santa Isabel (Azuay), la razón de masculinidad entre 20 y 39 años desciende a 69,99 varones por cada 100 mujeres en la población residente.*

---

## Paso 1: El registro de las ausencias en el hogar

> **English Summary:** *Households across Ecuador reported 96,825 international emigrants in the 2022 Census.*

El Censo 2022 incluyó un módulo específico para registrar a miembros del hogar que salieron a residir fuera del país. En total, los hogares empadronados reportaron 96.825 personas que emigraron al exterior. Este recuento directo documenta las ausencias familiares recientes a lo largo de las veinticuatro provincias del territorio nacional.

- **Cifra clave:** 96.825 personas reportadas como emigrantes internacionales por sus hogares de origen en el Ecuador.
- **Fuente oficial:** INEC, Censo 2022 / counts: nacion/data.parquet (columna: emigrants)

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT population, households, emigrants,
       emigrants * 1000.0 / NULLIF(population, 0) AS emig_rate_per_1000
FROM read_parquet('data/counts/v1b1/nacion/data.parquet');
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "nacion",
  "centro": [
    -78.5,
    -1.5
  ],
  "zoom": 6.8,
  "indicador": "emigrant_households",
  "filtro": "all",
  "capa_extra": "choropleth",
  "resaltados": [
    "EC"
  ]
}
```

---

## Paso 2: La concentración del éxodo en Azuay y Cañar

> **English Summary:** *Cañar (38.76 per 1,000) and Azuay (28.13 per 1,000) lead the nation in reported emigration rates.*

A escala provincial, las tasas más elevadas de emigración se localizan en el Austro. En Cañar se registraron 38,76 emigrantes por cada mil habitantes y en Azuay 28,13 por cada mil. Ambas provincias superan ampliamente la media nacional de 5,72 por mil, concentrando conjuntamente el 32,4% de todos los emigrantes reportados del país.

- **Cifra clave:** 38,76 emigrantes por cada 1.000 habitantes en Cañar (8.820 personas) y 28,13 en Azuay (22.550 personas).
- **Fuente oficial:** INEC, Censo 2022 / counts: provincia/data.parquet (unit_keys: '03', '01')

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT unit_key, population, emigrants,
       emigrants * 1000.0 / NULLIF(population, 0) AS rate_1000,
       emigrants * 100.0 / (SELECT sum(emigrants) FROM read_parquet('data/counts/v1b1/provincia/data.parquet')) AS pct_nacional
FROM read_parquet('data/counts/v1b1/provincia/data.parquet')
WHERE unit_key IN ('03', '01');
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "provincia",
  "centro": [
    -79.0,
    -2.8
  ],
  "zoom": 8.4,
  "indicador": "emigrant_households",
  "filtro": "unit_key IN ('01', '03')",
  "capa_extra": "choropleth",
  "resaltados": [
    "01",
    "03"
  ]
}
```

---

## Paso 3: Chunchi: el mayor porcentaje cantonal de emigrantes

> **English Summary:** *Chunchi in Chimborazo records Ecuador's highest canton emigration rate at 7.29% of its resident population.*

Entre los doscientos veintiún cantones del país, Chunchi, en la provincia de Chimborazo, presenta la mayor proporción de emigrantes respecto a su población residente. Con 775 personas reportadas fuera del país en una población censada de 10.635 habitantes, la tasa alcanza el 7,29%, superando a los cantones vecinos de Cañar y Azuay.

- **Cifra clave:** 7,29% de emigrantes sobre la población censada en Chunchi (775 emigrantes en 10.635 habitantes).
- **Fuente oficial:** INEC, Censo 2022 / counts: canton/data.parquet (unit_key='0605')

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT unit_key, population, households, emigrants,
       emigrants * 100.0 / NULLIF(population, 0) AS pct_emig
FROM read_parquet('data/counts/v1b1/canton/data.parquet')
WHERE unit_key = '0605';
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -78.91,
    -2.29
  ],
  "zoom": 11.2,
  "indicador": "emigrant_households",
  "filtro": "unit_key = '0605'",
  "capa_extra": "choropleth",
  "resaltados": [
    "0605"
  ]
}
```

---

## Paso 4: La tabla de emigración: perfil por sexo, edad y destino

> **English Summary:** *Detailed emigrant departure breakdowns require an upcoming cross-tabulation table [PENDING: Emigration aggregate].*

El cuestionario censal recabó para cada persona emigrante su sexo, año y edad de salida y país de residencia actual. Sin embargo, en el Release público agregado actual data-derived-v1b1 únicamente se dispone del conteo total de emigrantes por unidad territorial [PENDIENTE: agregado de Emigración por cantón × sexo × edad de salida × país de destino].

- **Cifra clave:** [PENDIENTE: agregado de Emigración por cantón × sexo × edad de salida × país de destino (variables E01, E02, E03, E04)].
- **Fuente oficial:** INEC, Censo 2022, Formulario Censal sección Emigración / [PENDIENTE]

### Consulta SQL Reproducible (DuckDB):
```sql
-- [PENDIENTE: requiere cruce público de tabla Emigración: E02 (sexo) x E03 (edad salida) x E04 (país destino)]
-- Consulta prevista una vez integrado el agregado en pipeline/:
-- SELECT canton_key, sex, departure_age_group, destination_country, COUNT(*) as emigrants
-- FROM read_parquet('data/counts/v1b2/emigration_by_canton.parquet')
-- WHERE canton_key IN ('0109', '0303')
-- GROUP BY ALL;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -79.1,
    -2.9
  ],
  "zoom": 9.2,
  "indicador": "emigrant_households",
  "filtro": "unit_key IN ('0109', '0303')",
  "capa_extra": "choropleth",
  "resaltados": [
    "0109",
    "0303"
  ]
}
```

---

## Paso 5: El giro de la pirámide: la razón de masculinidad en jóvenes

> **English Summary:** *In high-emigration Santa Isabel, resident sex ratio plunges to 69.99 men per 100 women aged 20-39.*

La estructura por sexo de la población residente refleja la selectividad de los desplazamientos. En el cantón Santa Isabel (Azuay), la razón de masculinidad entre las edades de veinte a treinta y nueve años desciende a 69,99 varones por cada cien mujeres. En Biblián (Cañar), la relación es de 76,07 varones por cada cien mujeres.

> **Hipótesis:** La menor presencia censal de varones jóvenes en cantones con elevada emigración se relaciona en la literatura demográfica con mayor participación masculina inicial en rutas migratorias laborales (el censo no indaga causas individuales del traslado). Fuente: [OIM Ecuador, Perfil Migratorio](https://ecuador.iom.int/es/recursos) (el censo no lo mide).

- **Cifra clave:** 69,99 varones por cada 100 mujeres entre 20 y 39 años en Santa Isabel (2.628 hombres y 3.755 mujeres).
- **Fuente oficial:** INEC, Censo 2022 / counts: canton/data.parquet (unit_key='0109')

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT unit_key, population,
       (age_20_24_m::BIGINT + age_25_29_m::BIGINT + age_30_34_m::BIGINT + age_35_39_m::BIGINT) AS men_20_39,
       (age_20_24_f::BIGINT + age_25_29_f::BIGINT + age_30_34_f::BIGINT + age_35_39_f::BIGINT) AS women_20_39,
       men_20_39 * 100.0 / NULLIF(women_20_39, 0) AS sex_ratio_20_39
FROM read_parquet('data/counts/v1b1/canton/data.parquet')
WHERE unit_key = '0109';
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -79.31,
    -3.27
  ],
  "zoom": 10.5,
  "indicador": "male_ratio",
  "filtro": "province_key = '01'",
  "capa_extra": "choropleth",
  "resaltados": [
    "0109"
  ]
}
```

---

## Paso 6: La tasa migratoria en Morona Santiago

> **English Summary:** *Morona Santiago ranks third nationally in emigration rate with 16.94 per 1,000 residents.*

En la región amazónica, Morona Santiago se sitúa como la tercera provincia con mayor tasa de emigrantes reportados respecto a su población: 16,94 por cada mil habitantes, con 3.261 personas censadas en el módulo de emigración. Esta tasa supera a las observadas en provincias andinas como Loja (8,67 por mil) o Tungurahua (14,03).

- **Cifra clave:** Tasa provincial de 16,94 emigrantes por cada mil habitantes en Morona Santiago (3.261 personas reportadas).
- **Fuente oficial:** INEC, Censo 2022 / counts: provincia/data.parquet (unit_key='14')

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT unit_key, population, emigrants,
       emigrants * 1000.0 / NULLIF(population, 0) AS rate_1000
FROM read_parquet('data/counts/v1b1/provincia/data.parquet')
WHERE unit_key = '14';
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "provincia",
  "centro": [
    -78.1,
    -2.3
  ],
  "zoom": 8.0,
  "indicador": "emigrant_households",
  "filtro": "unit_key = '14'",
  "capa_extra": "choropleth",
  "resaltados": [
    "14"
  ]
}
```

---

## Paso 7: La movilidad interna hacia cantones satélite

> **English Summary:** *Internal mobility expands peripheral cantons: 15.6% of Daule's population moved from another canton recently.*

De forma complementaria al desplazamiento externo, el censo mide la migración interna mediante la residencia cinco años antes. En el cantón Daule (Guayas), 34.664 personas declararon residir en otro cantón en 2017, lo que equivale al 15,6% de su población censada de cinco años y más, reflejando dinámicas de atracción residencial periurbana.

- **Cifra clave:** 34.664 personas residentes en Daule habitaban en otro cantón cinco años antes del censo.
- **Fuente oficial:** INEC, Censo 2022 / cross_counts_v1b2/sector/data.parquet (residence_other_canton_5)

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT substr(unit_key, 1, 4) AS canton_key,
       sum(residence_other_canton_5) AS residentes_otro_canton_5y
FROM read_parquet('data/interim/cross_counts_v1b2/sector/data.parquet')
WHERE unit_key LIKE '0906%'
GROUP BY canton_key;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -79.98,
    -1.98
  ],
  "zoom": 10.8,
  "indicador": "magnet_index",
  "filtro": "unit_key = '0906'",
  "capa_extra": "choropleth",
  "resaltados": [
    "0906"
  ]
}
```

---

## Paso 8: ¿Cómo se manifiesta la movilidad en su territorio?

> **English Summary:** *Migration shapes communities: explore the interactive map to inspect local mobility indicators.*

Los flujos de salida y llegada transforman la composición familiar, la estructura productiva y el relevo generacional en cada localidad. A través del mapa interactivo es posible consultar la cantidad de hogares con emigrantes y la proporción de residentes llegados recientemente. ¿Presenta su cantón un saldo de expulsión hacia el exterior o de atracción interna?

- **Cifra clave:** 96.825 personas emigrantes registradas en 5.188.827 hogares a nivel nacional.
- **Fuente oficial:** CPV 2022 INEC / indicators.yaml (id: emigrant_households)

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT sum(emigrants) AS total_emigrantes,
       sum(population) AS total_poblacion,
       sum(emigrants) * 1000.0 / sum(population) AS tasa_nacional_por_mil
FROM read_parquet('data/counts/v1b1/nacion/data.parquet');
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -78.5,
    -1.5
  ],
  "zoom": 7.0,
  "indicador": "emigrant_households",
  "filtro": "all",
  "capa_extra": "interactive_explorer",
  "resaltados": []
}
```

---

