# Guion de Scrollytelling: La ciudad vacía

**Identificador:** `03_ciudad_vacia`  
**Tema Central:** La paradoja del parque habitacional desocupado frente a la precariedad y el hacinamiento en el Ecuador.  
**Número de pasos:** 7  
**Giro contraintuitivo clave:** *Frente al supuesto de que las viviendas vacías son chozas rurales derruidas, cantones de emigración como Déleg (Cañar) exhiben un 57,58% de viviendas desocupadas o temporales: imponentes mansiones de remesas construidas con dólares de Nueva York que permanecen cerradas con candado, mientras en los márgenes de Guayaquil el hacinamiento crítico supera el 40%.*

---

## Paso 1: La paradoja de los techos deshabitados

> **English Summary:** *Ecuador presents a striking housing paradox: nearly 900,000 dwellings sit vacant or temporarily occupied.*

En un país donde cientos de miles de familias se hacinan en cuartos precarios o carecen de vivienda digna, el Censo 2022 constató una realidad perturbadora: existen casi novecientas mil viviendas que no cuentan con residentes permanentes. Aproximadamente una de cada seis estructuras habitacionales del Ecuador permanece completamente desocupada o se utiliza únicamente de manera temporal.

- **Cifra clave:** 13,92% de viviendas desocupadas o en construcción a nivel nacional; más de 700.000 viviendas desocupadas (V0201=4).
- **Fuente oficial:** INEC, Censo 2022 (Boletín Nacional) / tabulados: vivienda.xlsx

### Consulta SQL Reproducible (DuckDB):
```sql
-- Viviendas por condición de ocupación a nivel nacional
SELECT category,
       CASE category WHEN '1' THEN 'Ocupada con personas presentes'
                     WHEN '2' THEN 'Ocupada con personas ausentes'
                     WHEN '3' THEN 'Temporal / Vacacional'
                     WHEN '4' THEN 'Desocupada'
                     WHEN '5' THEN 'En construcción' END AS estado_vivienda,
       sum(n) AS total_viviendas,
       sum(n) * 100.0 / sum(sum(n)) OVER () AS porcentaje
FROM read_parquet('data/interim/full_aggregate_v1a/counts/v1a/categories/canton/**/*.parquet')
WHERE source_table = 'vivienda' AND variable = 'V0201'
GROUP BY category
ORDER BY category;
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
  "indicador": "vacant_dwellings",
  "filtro": "all",
  "capa_extra": "choropleth",
  "resaltados": [
    "EC"
  ]
}
```

---

## Paso 2: Los balnearios del litoral: pueblos fantasma diez meses al año

> **English Summary:** *Coastal resort cantons like Atacames see over 40% of their housing stock sit empty most of the year.*

A lo largo de la costa del Pacífico, la desocupación adquiere la forma del turismo y la segunda residencia de fin de semana. En cantones balnearios como Atacames en Esmeraldas o Salinas en Santa Elena, más del cuarenta por ciento del parque inmobiliario pasa desierto la mayor parte del año, mientras las poblaciones nativas padecen desabastecimiento de agua potable.

- **Cifra clave:** 41,33% de viviendas desocupadas o temporales en Atacames (11.029 de 26.688 unidades censadas).
- **Fuente oficial:** INEC, Censo 2022 / categories: canton (variable='V0201', unit_key='0806')

### Consulta SQL Reproducible (DuckDB):
```sql
-- Atacames: viviendas desocupadas y temporales
SELECT unit_key,
       sum(n) FILTER (WHERE category = '4') AS vacant,
       sum(n) FILTER (WHERE category = '3') AS seasonal,
       sum(n) AS total_dwellings,
       (sum(n) FILTER (WHERE category IN ('3', '4'))) * 100.0 / sum(n) AS pct_unoccupied
FROM read_parquet('data/interim/full_aggregate_v1a/counts/v1a/categories/canton/**/*.parquet')
WHERE variable = 'V0201' AND unit_key = '0806'
GROUP BY unit_key;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -79.84,
    0.86
  ],
  "zoom": 11.2,
  "indicador": "vacant_dwellings",
  "filtro": "unit_key = '0806'",
  "capa_extra": "choropleth",
  "resaltados": [
    "0806"
  ]
}
```

---

## Paso 3: El giro del Austro: las mansiones de remesas con candado

> **English Summary:** *Contrary to expectations, Cañar's vacant homes are large remittance-funded houses sitting locked and empty.*

Suele asumirse que una casa desocupada es una choza ruinosa en un caserío abandonado. Los datos muestran la realidad opuesta: en cantones como Déleg, en Cañar, casi el cincuenta y ocho por ciento de las viviendas están vacías. Son imponentes construcciones de ladrillo y hormigón levantadas con remesas de emigrantes en Nueva York, cerradas a cal y canto esperando un retorno esquivo.

- **Cifra clave:** 57,58% de viviendas desocupadas o temporales en Déleg (2.816 de 4.891 viviendas totales).
- **Fuente oficial:** INEC, Censo 2022 / categories: canton (variable='V0201', unit_key='0306')

### Consulta SQL Reproducible (DuckDB):
```sql
-- Cantón Déleg (Cañar): récord de viviendas desocupadas y temporales
SELECT unit_key,
       sum(n) FILTER (WHERE category = '4') AS desocupadas,
       sum(n) FILTER (WHERE category = '3') AS temporales,
       sum(n) AS total_viviendas,
       (sum(n) FILTER (WHERE category IN ('3', '4'))) * 100.0 / sum(n) AS pct_vacias_o_temporales
FROM read_parquet('data/interim/full_aggregate_v1a/counts/v1a/categories/canton/**/*.parquet')
WHERE variable = 'V0201' AND unit_key = '0306'
GROUP BY unit_key;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -78.92,
    -2.78
  ],
  "zoom": 11.5,
  "indicador": "vacant_dwellings",
  "filtro": "unit_key = '0306'",
  "capa_extra": "choropleth",
  "resaltados": [
    "0306"
  ]
}
```

---

## Paso 4: El vaciamiento de los centros metropolitanos

> **English Summary:** *Historical city centers in Quito and Guayaquil face depopulation as residents move to suburban valleys.*

La desocupación también erosiona las áreas centrales de las grandes metrópolis. En el Centro Histórico y en barrios residenciales consolidados de Quito y Guayaquil, departamentos enteros se deshabitan por el traslado de familias acomodadas hacia los valles suburbanos. La ciudad desaprovecha redes de agua, transporte y alumbrado público ya instaladas, mientras expande su mancha urbana de forma desordenada.

- **Cifra clave:** Autocorrelación espacial significativa de vacancia urbana en Quito (Moran I = 0,389, p < 0,001).
- **Fuente oficial:** INEC / pipeline analitica: spatial_v1b2/moran_canton.parquet (unit_key='1701')

### Consulta SQL Reproducible (DuckDB):
```sql
-- Estadísticas de autocorrelación espacial de vacancia en Quito
SELECT unit_key, indicator, moran_i, permutation_p
FROM read_parquet('data/interim/spatial_v1b2/moran_canton.parquet')
WHERE unit_key = '1701' AND indicator = 'vacancy';
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "sector",
  "centro": [
    -78.514,
    -0.222
  ],
  "zoom": 13.8,
  "indicador": "vacancy",
  "filtro": "parish_key = '170150'",
  "capa_extra": "choropleth",
  "resaltados": [
    "170150001001",
    "170150002002"
  ]
}
```

---

## Paso 5: La otra cara de la moneda: el hacinamiento periférico

> **English Summary:** *In sharp contrast, informal peripheries of Guayaquil suffer severe overcrowding exceeding 40%.*

La injusticia habitacional se manifiesta en toda su crudeza al mirar la otra orilla urbana. Mientras miles de departamentos permanecen desocupados en las zonas céntricas, en los asentamientos periféricos de Guayaquil el hacinamiento supera el cuarenta por ciento. Familias enteras comparten un solo dormitorio improvisado en caña guadúa o bloque, sin ventilación adecuada ni servicios sanitarios básicos.

- **Cifra clave:** Clusters Alto-Alto de hacinamiento en el noroeste de Guayaquil con tasas superiores al 40% de hogares.
- **Fuente oficial:** INEC / spatial_v1b2/lisa_sector.parquet (cluster='alto-alto', canton_key='0901')

### Consulta SQL Reproducible (DuckDB):
```sql
-- Sectores con clusters significativos de hacinamiento Alto-Alto en Guayaquil
SELECT unit_key, canton_key, value AS pct_hacinamiento, cluster, permutation_p
FROM read_parquet('data/interim/spatial_v1b2/lisa_sector.parquet')
WHERE canton_key = '0901' AND indicator = 'overcrowding' AND cluster = 'alto-alto'
ORDER BY value DESC
LIMIT 5;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "sector",
  "centro": [
    -79.96,
    -2.14
  ],
  "zoom": 12.8,
  "indicador": "overcrowding",
  "filtro": "canton_key = '0901'",
  "capa_extra": "choropleth",
  "resaltados": [
    "090150030001",
    "090150031002"
  ]
}
```

---

## Paso 6: La brecha territorial entre casas y hogares

> **English Summary:** *Comparing homes to households reveals a distorted map: excess housing where few live, severe deficit where crowds reside.*

Al confrontar el número de viviendas existentes contra los hogares reales en cada cantón, el mapa nacional evidencia un grave descalce territorial. Existen cantones con más de dos viviendas por cada hogar habitado, frente a cantones urbanos populares donde la presión habitacional es asfixiante. El país edifica techos donde no vive la gente y descuida donde la gente urge refugio.

- **Cifra clave:** Relación de hasta 2,4 viviendas por hogar en cantones de retiro/migración frente a 1,02 en urbes obreras.
- **Fuente oficial:** INEC, Censo 2022 / counts: canton/data.parquet

### Consulta SQL Reproducible (DuckDB):
```sql
-- Ratio de viviendas por hogar a nivel cantonal
SELECT unit_key, population, dwellings, households,
       dwellings * 1.0 / NULLIF(households, 0) AS dwellings_per_hh
FROM read_parquet('data/counts/v1b1/canton/data.parquet')
ORDER BY dwellings_per_hh DESC
LIMIT 5;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -78.5,
    -1.5
  ],
  "zoom": 7.2,
  "indicador": "dwellings",
  "filtro": "all",
  "capa_extra": "choropleth",
  "resaltados": [
    "0306",
    "0112",
    "0806"
  ]
}
```

---

## Paso 7: ¿Cómo habitamos nuestro territorio?

> **English Summary:** *With surplus empty houses alongside homelessness, explore the map to see how housing occupancy behaves in your city.*

Si sobran casas sin gente y abunda gente sin techo adecuado, el debate urbano no radica únicamente en construir más, sino en democratizar el acceso y regular el uso social del suelo. ¿Cuántas viviendas vacías hay en tu cantón o manzana? ¿Coexisten en tu barrio el confort de residencias vacantes con la precariedad de familias sin espacio?

- **Cifra clave:** 900.000 viviendas deshabitadas esperan un debate de fondo sobre justicia urbana en el Ecuador.
- **Fuente oficial:** CPV 2022 INEC / Explorador interactivo Censo Vivo

### Consulta SQL Reproducible (DuckDB):
```sql
-- Consulta abierta: resumen nacional de condición de vivienda
SELECT sum(dwellings) AS total_viviendas,
       sum(households) AS total_hogares,
       sum(dwellings) - sum(households) AS excedente_viviendas_bruto
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
  "indicador": "vacant_dwellings",
  "filtro": "all",
  "capa_extra": "interactive_explorer",
  "resaltados": []
}
```

---

