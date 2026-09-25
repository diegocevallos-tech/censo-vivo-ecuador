# Guion de Scrollytelling: La brecha digital

**Identificador:** `04_brecha_digital`  
**Tema Central:** La disparidad de conectividad en el Ecuador: comparación en el mismo universo de hogares entre telefonía celular e internet fijo.  
**Número de pasos:** 7  
**Giro contraintuitivo comprobado:** *En cantones como Paján (Manabí) y El Empalme (Guayas), más del 80% al 87% de los hogares disponen de teléfono celular (H1002=1), pero solo entre el 22% y el 36% cuentan con servicio de internet fijo domiciliario (H1004=1): una brecha de más de 50 puntos porcentuales en el mismo universo censal de hogares.*

---

## Paso 1: Telefonía celular e internet fijo: dos realidades del hogar

> **English Summary:** *Nationwide, 86.98% of households have mobile phone service, while only 60.89% have fixed home internet.*

Al evaluar el equipamiento tecnológico en el mismo universo de 5.188.827 hogares clasificados en el Censo 2022, se observan diferencias sustanciales entre servicios. El 86,98% de los hogares ecuatorianos dispone de servicio de teléfono celular (variable H1002). En contraste, solo el 60,89% cuenta con servicio de internet fijo domiciliario (variable H1004).

- **Cifra clave:** 86,98% de hogares con teléfono celular (4.513.446) frente a 60,89% con internet fijo (3.159.588 de 5.188.827 hogares).
- **Fuente oficial:** INEC, Censo 2022 / categories: canton (H1002=1 y H1004=1) / indicators.yaml (id: fixed_internet)

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT sum(n) FILTER (WHERE variable = 'H1002' AND category = '1') AS hogares_con_celular,
       sum(n) FILTER (WHERE variable = 'H1004' AND category = '1') AS hogares_con_internet_fijo,
       sum(n) FILTER (WHERE variable = 'H1004') AS total_hogares_clasificados,
       sum(n) FILTER (WHERE variable = 'H1002' AND category = '1') * 100.0 / sum(n) FILTER (WHERE variable = 'H1002') AS pct_celular,
       sum(n) FILTER (WHERE variable = 'H1004' AND category = '1') * 100.0 / sum(n) FILTER (WHERE variable = 'H1004') AS pct_fijo
FROM read_parquet('data/interim/full_aggregate_v1a/counts/v1a/categories/canton/**/*.parquet')
WHERE variable IN ('H1002', 'H1004');
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
  "indicador": "fixed_internet",
  "filtro": "all",
  "capa_extra": "choropleth",
  "resaltados": [
    "EC"
  ]
}
```

---

## Paso 2: Las áreas con mayor penetración de internet fijo

> **English Summary:** *Cantons like Rumiñahui and Cuenca exceed 75% household fixed internet connectivity.*

A nivel cantonal, la cobertura de internet fijo en los hogares alcanza sus valores máximos en cantones como Rumiñahui (Pichincha) y Cuenca (Azuay), donde más del setenta y cinco por ciento de los hogares reporta el servicio. En estas demarcaciones, la brecha respecto a la tenencia de teléfono celular se reduce a menos de quince puntos porcentuales.

- **Cifra clave:** 78,24% de hogares con internet fijo en Rumiñahui y 75,30% en Cuenca (categoría H1004=1).
- **Fuente oficial:** INEC, Censo 2022 / categories: canton (variable='H1004', unit_keys: '1705', '0101')

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT unit_key,
       sum(n) FILTER (WHERE category = '1') AS hogares_fijo,
       sum(n) AS total_hogares,
       sum(n) FILTER (WHERE category = '1') * 100.0 / sum(n) AS pct_fixed_internet
FROM read_parquet('data/interim/full_aggregate_v1a/counts/v1a/categories/canton/**/*.parquet')
WHERE variable = 'H1004' AND unit_key IN ('1705', '0101')
GROUP BY unit_key;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -78.7,
    -1.5
  ],
  "zoom": 8.0,
  "indicador": "fixed_internet",
  "filtro": "unit_key IN ('1705', '0101')",
  "capa_extra": "choropleth",
  "resaltados": [
    "1705",
    "0101"
  ]
}
```

---

## Paso 3: Los cantones con menor cobertura de red fija domiciliaria

> **English Summary:** *In Taisha (14.8%) and Paján (22.6%), fewer than one in four households has fixed internet.*

En el extremo opuesto, en cantones amazónicos y rurales de la Costa, menos de uno de cada cuatro hogares cuenta con internet fijo. En el cantón Taisha (Morona Santiago) la penetración se sitúa en el 14,8%, y en Paján (Manabí) en el 22,6%, evidenciando marcadas disparidades en la infraestructura fija de telecomunicaciones instalada en los hogares.

- **Cifra clave:** 14,82% de hogares con internet fijo en Taisha y 22,64% en Paján (variable H1004).
- **Fuente oficial:** INEC, Censo 2022 / categories: canton (variable='H1004', unit_keys: '1409', '1310')

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT unit_key,
       sum(n) FILTER (WHERE category = '1') AS hogares_fijo,
       sum(n) AS total_hogares,
       sum(n) FILTER (WHERE category = '1') * 100.0 / sum(n) AS pct_fixed_internet
FROM read_parquet('data/interim/full_aggregate_v1a/counts/v1a/categories/canton/**/*.parquet')
WHERE variable = 'H1004' AND unit_key IN ('1409', '1310')
GROUP BY unit_key;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -78.5,
    -2.0
  ],
  "zoom": 8.0,
  "indicador": "fixed_internet",
  "filtro": "unit_key IN ('1409', '1310')",
  "capa_extra": "choropleth",
  "resaltados": [
    "1409",
    "1310"
  ]
}
```

---

## Paso 4: El giro de denominadores homogéneos: celular frente a red fija

> **English Summary:** *Comparing households with households: Paján shows an 80.48% mobile vs 22.64% fixed internet gap (57.84 points).*

Al contrastar ambos servicios sobre el mismo denominador de hogares, se aprecia la magnitud de la brecha tecnológica. En Paján (Manabí), el 80,48% de los hogares dispone de teléfono celular, pero solo el 22,64% cuenta con internet fijo: una brecha de 57,84 puntos porcentuales. En El Empalme (Guayas), la brecha alcanza 51,71 puntos porcentuales.

> **Hipótesis:** La brecha entre teléfono celular e internet fijo en hogares rurales suele atribuirse a la disponibilidad de redes de fibra óptica y a la modalidad prepago en telefonía móvil (el censo no mide planes tarifarios ni cobertura de redes externas). Fuente: [ARCOTEL, Estadísticas del Sector](https://www.arcotel.gob.ec/) (el censo no lo mide).

- **Cifra clave:** Brecha de 57,84 puntos en Paján (80,48% celular vs 22,64% internet fijo) y 51,71 en El Empalme.
- **Fuente oficial:** INEC, Censo 2022 / categories: canton (H1002 vs H1004, unit_keys: '1310', '0908')

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT unit_key,
       sum(n) FILTER (WHERE variable = 'H1002' AND category = '1') * 100.0 / sum(n) FILTER (WHERE variable = 'H1002') AS pct_celular,
       sum(n) FILTER (WHERE variable = 'H1004' AND category = '1') * 100.0 / sum(n) FILTER (WHERE variable = 'H1004') AS pct_fijo,
       (sum(n) FILTER (WHERE variable = 'H1002' AND category = '1') * 100.0 / sum(n) FILTER (WHERE variable = 'H1002')) -
       (sum(n) FILTER (WHERE variable = 'H1004' AND category = '1') * 100.0 / sum(n) FILTER (WHERE variable = 'H1004')) AS brecha_puntos
FROM read_parquet('data/interim/full_aggregate_v1a/counts/v1a/categories/canton/**/*.parquet')
WHERE variable IN ('H1002', 'H1004') AND unit_key IN ('1310', '0908')
GROUP BY unit_key;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -80.1,
    -1.3
  ],
  "zoom": 9.5,
  "indicador": "fixed_internet",
  "filtro": "unit_key IN ('1310', '0908')",
  "capa_extra": "choropleth",
  "resaltados": [
    "1310",
    "0908"
  ]
}
```

---

## Paso 5: La brecha intra-cantonal entre parroquias de Quito

> **English Summary:** *Inside canton Quito, internet usage ranges from 91.99% in Iñaquito to 50.54% in rural parish Pacto.*

Las diferencias en conectividad también se manifiestan al interior de un mismo cantón. En el Distrito Metropolitano de Quito, mientras el uso individual de internet entre personas de cinco años y más supera el 91% en Iñaquito y Cumbayá, en parroquias rurales noroccidentales como Pacto se sitúa en 50,54%, constatando una distancia de cuarenta y un puntos porcentuales.

- **Cifra clave:** 91,99% de uso de internet en Iñaquito (parish_key='170157') frente a 50,54% en Pacto ('170161').
- **Fuente oficial:** INEC, Censo 2022 / cross_counts_v1b2/sector/data.parquet (internet_person_5)

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT substr(unit_key, 1, 6) AS parish_key,
       sum(internet_person_5) * 100.0 / NULLIF(sum(internet_response_5), 0) AS pct_internet
FROM read_parquet('data/interim/cross_counts_v1b2/sector/data.parquet')
WHERE unit_key LIKE '1701%' AND substr(unit_key, 1, 6) IN ('170157', '170161')
GROUP BY parish_key;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "parroquia",
  "centro": [
    -78.5,
    -0.05
  ],
  "zoom": 10.2,
  "indicador": "fixed_internet",
  "filtro": "canton_key = '1701'",
  "capa_extra": "choropleth",
  "resaltados": [
    "170157",
    "170161"
  ]
}
```

---

## Paso 6: La brecha generacional entre jóvenes y personas mayores

> **English Summary:** *Digital exclusion disproportionately impacts seniors: 88.85% youth vs 53.42% seniors in Quito, falling to 8.72% in Eloy Alfaro.*

Al evaluar el uso individual de herramientas digitales por grupos de edad, se evidencia una brecha generacional. En el cantón Quito, el 88,85% de los jóvenes entre quince y veinticuatro años utiliza internet, frente al 53,42% de personas mayores de sesenta y cinco años. En cantones como Eloy Alfaro, el uso en personas mayores desciende al 8,72%.

- **Cifra clave:** 88,85% de jóvenes conectados en Quito frente a 8,72% de adultos mayores en Eloy Alfaro.
- **Fuente oficial:** INEC, Censo 2022 / cross_counts_v1b2 (digital_youth_yes, digital_senior_yes)

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT substr(unit_key, 1, 4) AS canton_key,
       sum(digital_youth_yes) * 100.0 / NULLIF(sum(digital_youth_n), 0) AS pct_jovenes_conectados,
       sum(digital_senior_yes) * 100.0 / NULLIF(sum(digital_senior_n), 0) AS pct_mayores_conectados
FROM read_parquet('data/interim/cross_counts_v1b2/sector/data.parquet')
WHERE substr(unit_key, 1, 4) IN ('1701', '0802')
GROUP BY canton_key;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -78.5,
    -0.5
  ],
  "zoom": 7.5,
  "indicador": "digital_exclusion",
  "filtro": "canton_key IN ('1701', '0802')",
  "capa_extra": "choropleth",
  "resaltados": [
    "1701",
    "0802"
  ]
}
```

---

## Paso 7: ¿Qué nivel de conectividad registra su cantón?

> **English Summary:** *Internet connectivity shapes economic opportunity: explore your canton's household digital metrics on the map.*

La disponibilidad de servicios de internet fijo y telefonía celular en los hogares define las oportunidades de educación, trabajo y comunicación en cada comunidad. A través del mapa interactivo se pueden contrastar las coberturas domiciliarias a nivel de cantón y sector censal. ¿Qué porcentaje de hogares con internet fijo y celular reporta su área residencial?

- **Cifra clave:** 2.029.239 hogares sin servicio de internet fijo domiciliario en el territorio nacional.
- **Fuente oficial:** CPV 2022 INEC / indicators.yaml (id: fixed_internet)

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT sum(n) FILTER (WHERE category = '1') AS hogares_con_internet_fijo,
       sum(n) FILTER (WHERE category = '2') AS hogares_sin_internet_fijo
FROM read_parquet('data/interim/full_aggregate_v1a/counts/v1a/categories/canton/**/*.parquet')
WHERE variable = 'H1004';
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
  "indicador": "fixed_internet",
  "filtro": "all",
  "capa_extra": "interactive_explorer",
  "resaltados": []
}
```

---

