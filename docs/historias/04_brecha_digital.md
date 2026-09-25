# Guion de Scrollytelling: La brecha digital

**Identificador:** `04_brecha_digital`  
**Tema Central:** La desigualdad en la conectividad del siglo XXI: el espejismo de la telefonía móvil frente a la carencia de internet fijo en el hogar.  
**Número de pasos:** 7  
**Giro contraintuitivo clave:** *La trampa del celular prepago: el 69,40% de la población usa internet móvil, pero el internet fijo en el hogar apenas alcanza el 51,42% nacional y cae bajo el 35% en cantones rurales y suburbanos costeños (Balzar, El Empalme). Las familias sobreviven comprando recargas diarias de megas a costos elevados, sin red estable para educación o teletrabajo.*

---

## Paso 1: El espejismo de la sociedad hiperconectada

> **English Summary:** *While nearly 70% of Ecuadorians use the internet, half of all households lack a fixed home broadband connection.*

Casi siete de cada diez compatriotas de cinco años en adelante declaran utilizar internet en su vida habitual. A simple vista, el Ecuador aparenta ser una comunidad plenamente integrada al siglo digital. No obstante, al analizar la infraestructura que respalda esa conexión, el espejismo se disuelve: prácticamente la mitad de los hogares ecuatorianos carece de una red fija domiciliaria de banda ancha.

- **Cifra clave:** 69,40% de uso individual de internet, pero solo 51,42% de hogares con internet fijo propio (2.667.864 de 5.188.827 hogares).
- **Fuente oficial:** INEC, Censo 2022 (Boletín Nacional) / categories: canton (H0801)

### Consulta SQL Reproducible (DuckDB):
```sql
-- Internet fijo en el hogar a nivel nacional (H0801)
SELECT sum(n) FILTER (WHERE category = '1') AS hogares_con_internet_fijo,
       sum(n) AS hogares_clasificados,
       sum(n) FILTER (WHERE category = '1') * 100.0 / sum(n) AS pct_internet_fijo
FROM read_parquet('data/interim/full_aggregate_v1a/counts/v1a/categories/canton/**/*.parquet')
WHERE variable = 'H0801';
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

## Paso 2: Las cumbres digitales: Galápagos y los valles quiteños

> **English Summary:** *Galapagos and suburban Quito lead Ecuador's digital connectivity, reaching nearly 90% regular internet use.*

En la cúspide de la conectividad se hallan el archipiélago de Galápagos y los valles residenciales de Pichincha. En cantones como San Cristóbal o Rumiñahui, cerca del noventa por ciento de los habitantes navega cotidianamente y la brecha digital entre jóvenes y adultos es la menor del país. Sus comunidades disfrutan de alta velocidad para teletrabajo, educación virtual y comercio electrónico.

- **Cifra clave:** 89,60% de uso individual de internet en San Cristóbal (Galápagos) y 87,56% en Rumiñahui (Pichincha).
- **Fuente oficial:** INEC / cross_counts_v1b2/sector/data.parquet (canton_keys: '2001', '1705')

### Consulta SQL Reproducible (DuckDB):
```sql
-- Cantones líderes en uso individual de internet
SELECT substr(unit_key, 1, 4) AS canton_key,
       sum(internet_person_5) * 100.0 / NULLIF(sum(internet_response_5), 0) AS pct_internet
FROM read_parquet('data/interim/cross_counts_v1b2/sector/data.parquet')
GROUP BY canton_key
ORDER BY pct_internet DESC
LIMIT 5;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -90.5,
    -0.6
  ],
  "zoom": 8.0,
  "indicador": "internet_person_5",
  "filtro": "canton_key IN ('2001', '1705')",
  "capa_extra": "choropleth",
  "resaltados": [
    "2001",
    "1705"
  ]
}
```

---

## Paso 3: El apagón informativo: la Amazonía profunda y el norte costero

> **English Summary:** *In isolated areas like Taisha and Eloy Alfaro, under 30% of citizens have ever accessed the internet.*

Al descender hacia los cantones más rezagados de la Amazonía y del norte de Esmeraldas, el panorama muta a un aislamiento digital casi absoluto. En Taisha o Eloy Alfaro, menos de tres de cada diez personas han navegado alguna vez por internet. Para las infancias rurales de estas comarcas, las bibliotecas virtuales y las clases remotas pertenecen a un planeta inalcanzable.

- **Cifra clave:** Apenas 19,74% de uso individual de internet en Taisha (Morona Santiago) y 28,26% en Eloy Alfaro (Esmeraldas).
- **Fuente oficial:** INEC / cross_counts_v1b2/sector/data.parquet (canton_keys: '1409', '0802')

### Consulta SQL Reproducible (DuckDB):
```sql
-- Cantones con menor acceso individual a internet
SELECT substr(unit_key, 1, 4) AS canton_key,
       sum(internet_person_5) * 100.0 / NULLIF(sum(internet_response_5), 0) AS pct_internet
FROM read_parquet('data/interim/cross_counts_v1b2/sector/data.parquet')
GROUP BY canton_key
ORDER BY pct_internet ASC
LIMIT 5;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -77.5,
    -2.4
  ],
  "zoom": 8.5,
  "indicador": "internet_person_5",
  "filtro": "canton_key IN ('1409', '0802')",
  "capa_extra": "choropleth",
  "resaltados": [
    "1409",
    "0802"
  ]
}
```

---

## Paso 4: El giro de la precariedad: la trampa de los megas prepago

> **English Summary:** *Mobile phones mask deep inequality: millions rely on costly prepaid daily megabytes with no home broadband.*

Existe el mito de que poseer un celular básico resuelve la brecha de conectividad. Los microdatos revelan una trampa silenciosa: en cantones rurales y suburbanos de la Costa, más del sesenta por ciento de la población usa internet móvil, pero menos del treinta y cinco por ciento cuenta con red fija domiciliaria. Familias enteras gastan diariamente en recargas costosas que impiden el estudio simultáneo.

- **Cifra clave:** Brecha de más de 30 puntos entre uso móvil e internet fijo domiciliario en cantones como Balzar o El Empalme.
- **Fuente oficial:** INEC / cross_counts_v1b2 vs categories: canton (H0801)

### Consulta SQL Reproducible (DuckDB):
```sql
-- Disparidad entre uso personal de internet y red fija en cantones costeros
SELECT c.canton_key,
       c.pct_internet_person,
       f.pct_fixed_internet,
       (c.pct_internet_person - f.pct_fixed_internet) AS brecha_prepago
FROM (
    SELECT substr(unit_key, 1, 4) AS canton_key,
           sum(internet_person_5) * 100.0 / NULLIF(sum(internet_response_5), 0) AS pct_internet_person
    FROM read_parquet('data/interim/cross_counts_v1b2/sector/data.parquet')
    GROUP BY canton_key
) c
JOIN (
    SELECT unit_key AS canton_key,
           sum(n) FILTER (WHERE category = '1') * 100.0 / sum(n) AS pct_fixed_internet
    FROM read_parquet('data/interim/full_aggregate_v1a/counts/v1a/categories/canton/**/*.parquet')
    WHERE variable = 'H0801'
    GROUP BY unit_key
) f USING (canton_key)
WHERE c.canton_key IN ('0903', '0908', '0916')
ORDER BY brecha_prepago DESC;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -79.9,
    -1.6
  ],
  "zoom": 9.5,
  "indicador": "fixed_internet",
  "filtro": "province_key = '09'",
  "capa_extra": "choropleth",
  "resaltados": [
    "0903",
    "0908",
    "0916"
  ]
}
```

---

## Paso 5: La fractura invisible dentro de Quito

> **English Summary:** *Inside Quito itself, connectivity plunges from 92% in Iñaquito to barely 50% in rural Pacto.*

No es necesario internarse en la selva para encontrar la brecha digital. En el Distrito Metropolitano de Quito, mientras las parroquias urbanas como Iñaquito o Cumbayá rozan el noventa y dos por ciento de penetración, las parroquias del noroccidente rural como Pacto apenas alcanzan el cincuenta por ciento. En una misma jurisdicción municipal conviven la economía del conocimiento y la exclusión de red.

- **Cifra clave:** 91,99% de conectividad en Iñaquito frente a 50,54% en Pacto dentro del mismo cantón Quito.
- **Fuente oficial:** INEC / cross_counts_v1b2/sector/data.parquet (parish_keys: '170157', '170161')

### Consulta SQL Reproducible (DuckDB):
```sql
-- Brecha intra-cantonal de internet en el Distrito Metropolitano de Quito
SELECT substr(unit_key, 1, 6) AS parish_key,
       sum(internet_person_5) * 100.0 / NULLIF(sum(internet_response_5), 0) AS pct_internet
FROM read_parquet('data/interim/cross_counts_v1b2/sector/data.parquet')
WHERE unit_key LIKE '1701%'
GROUP BY parish_key
HAVING sum(internet_response_5) >= 1000
ORDER BY pct_internet DESC;
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
  "indicador": "internet_person_5",
  "filtro": "canton_key = '1701'",
  "capa_extra": "choropleth",
  "resaltados": [
    "170157",
    "170161"
  ]
}
```

---

## Paso 6: El analfabetismo digital de nuestros mayores

> **English Summary:** *A generational divide leaves rural seniors digitally illiterate: under 10% can navigate online services.*

La fractura no es exclusivamente territorial; también es dolorosamente generacional. En sectores campesinos, mientras casi tres de cada cuatro jóvenes dominan el entorno web, menos del diez por ciento de los adultos mayores sabe interactuar con herramientas informáticas. En un Estado que digitaliza progresivamente trámites bancarios y médicos, nuestros abuelos rurales quedan sumidos en una silenciosa orfandad cívica.

- **Cifra clave:** 88,85% de jóvenes conectados en Quito frente a solo 8,72% de adultos mayores conectados en Eloy Alfaro.
- **Fuente oficial:** INEC / cross_counts_v1b2 (digital_senior_yes / digital_youth_yes)

### Consulta SQL Reproducible (DuckDB):
```sql
-- Brecha generacional digital: jóvenes (15-24) vs adultos mayores (65+)
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
  "indicador": "digital_senior_yes",
  "filtro": "canton_key IN ('1701', '0802')",
  "capa_extra": "choropleth",
  "resaltados": [
    "1701",
    "0802"
  ]
}
```

---

## Paso 7: ¿Qué tan libre es tu acceso al futuro?

> **English Summary:** *Internet access is a basic modern right: explore your parish on the map to evaluate digital equity.*

En la sociedad del conocimiento, carecer de internet no significa únicamente estar desconectado: significa estar privado de telemedicina, educación de calidad y empleo productivo. ¿Cómo se navega en tu barrio o recinto? ¿Cuenta tu familia con una red fija estable para prosperar, o depende la comunidad de recargas transitorias para no quedar al margen del mundo contemporáneo?

- **Cifra clave:** 2,5 millones de hogares ecuatorianos sin internet fijo esperan políticas públicas de inclusión digital.
- **Fuente oficial:** CPV 2022 INEC / Explorador interactivo Censo Vivo

### Consulta SQL Reproducible (DuckDB):
```sql
-- Consulta abierta: resumen nacional de brecha digital por hogares
SELECT sum(n) FILTER (WHERE category = '1') AS hogares_conectados,
       sum(n) FILTER (WHERE category = '2') AS hogares_desconectados
FROM read_parquet('data/interim/full_aggregate_v1a/counts/v1a/categories/canton/**/*.parquet')
WHERE variable = 'H0801';
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

