# Guion de Scrollytelling: La ciudad vacía

**Identificador:** `03_ciudad_vacia`  
**Tema Central:** El parque habitacional desocupado según la definición del catálogo censal frente a las zonas con mayor hacinamiento de hogares.  
**Número de pasos:** 7  
**Giro contraintuitivo comprobado:** *La mayor tasa cantonal de viviendas desocupadas (V0201=4) no se sitúa en urbes densas sino en cantones andinos de la provincia de Cañar: en el cantón Cañar alcanza el 26,41% y en Suscal el 23,12%, mientras en el noroeste de Guayaquil el hacinamiento supera el 40%.*

---

## Paso 1: La magnitud nacional de las viviendas desocupadas

> **English Summary:** *Ecuador records 766,776 vacant private dwellings, a national vacancy rate of 11.63%.*

El Censo 2022 clasificó la condición de ocupación de 6.595.318 viviendas particulares en el territorio ecuatoriano. De ese total, 766.776 unidades se encontraron completamente desocupadas al momento del empadronamiento (categoría V0201=4). De acuerdo con el indicador oficial vacant_private_dwellings del catálogo, la tasa de desocupación habitacional nacional se sitúa en el 11,63%.

- **Cifra clave:** 11,63% de viviendas particulares desocupadas a nivel nacional (766.776 de 6.595.318 viviendas particulares válidas).
- **Fuente oficial:** INEC, Censo 2022 / indicators.yaml (id: vacant_private_dwellings) / categories: canton (V0201=4)

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT sum(n) FILTER (WHERE category = '4') AS viviendas_desocupadas,
       sum(n) AS viviendas_particulares_validas,
       sum(n) FILTER (WHERE category = '4') * 100.0 / sum(n) AS pct_desocupadas
FROM read_parquet('data/interim/full_aggregate_v1a/counts/v1a/categories/canton/**/*.parquet')
WHERE source_table = 'vivienda' AND variable = 'V0201';
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
  "indicador": "vacant_private_dwellings",
  "filtro": "all",
  "capa_extra": "choropleth",
  "resaltados": [
    "EC"
  ]
}
```

---

## Paso 2: El giro del Austro: Cañar y Suscal a la cabeza de la desocupación

> **English Summary:** *Under official catalog metrics, Cañar (26.41%) and Suscal (23.12%) record Ecuador's highest dwelling vacancy rates.*

Al analizar la desocupación habitacional a nivel cantonal bajo la definición estricta del catálogo, las mayores tasas del país se concentran en la provincia de Cañar. En el cantón Cañar, el 26,41% de las viviendas particulares están desocupadas (2.621 de 9.925 unidades), y en Suscal el 23,12% (567 de 2.452).

> **Hipótesis:** La elevada desocupación de viviendas en cantones con tradición migratoria suele vincularse en estudios sociales a inversión de ahorros en construcción residencial de uso ocasional (el censo no indaga financiamiento de la obra ni planes de uso futuro). Fuente: [FLACSO Ecuador, Migración y Territorio](https://biblio.flacsoandes.edu.ec/) (el censo no lo mide).

- **Cifra clave:** 26,41% de desocupación habitacional en Cañar y 23,12% en Suscal (categoría V0201=4).
- **Fuente oficial:** INEC, Censo 2022 / categories: canton (variable='V0201', unit_keys: '0302', '0307')

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT unit_key,
       sum(n) FILTER (WHERE category = '4') AS desocupadas,
       sum(n) AS total_validas,
       sum(n) FILTER (WHERE category = '4') * 100.0 / sum(n) AS pct_vacant
FROM read_parquet('data/interim/full_aggregate_v1a/counts/v1a/categories/canton/**/*.parquet')
WHERE source_table = 'vivienda' AND variable = 'V0201' AND unit_key IN ('0302', '0307')
GROUP BY unit_key
ORDER BY pct_vacant DESC;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -78.95,
    -2.55
  ],
  "zoom": 10.5,
  "indicador": "vacant_private_dwellings",
  "filtro": "province_key = '03'",
  "capa_extra": "choropleth",
  "resaltados": [
    "0302",
    "0307"
  ]
}
```

---

## Paso 3: Biblián y Gualaceo: la persistencia de la vacancia en el Austro

> **English Summary:** *In Biblián and Gualaceo, one out of every five private dwellings is unoccupied.*

El patrón de alta desocupación se extiende a otros cantones de Cañar y Azuay. En Biblián, el 21,57% de las viviendas particulares están desocupadas (5.346 de 24.785), y en Gualaceo la tasa alcanza el 19,88% (4.177 de 21.011). En ambos cantones, una de cada cinco viviendas particulares censadas no tenía residentes habituales.

- **Cifra clave:** 21,57% de viviendas desocupadas en Biblián (Cañar) y 19,88% en Gualaceo (Azuay).
- **Fuente oficial:** INEC, Censo 2022 / categories: canton (variable='V0201', unit_keys: '0303', '0103')

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT unit_key,
       sum(n) FILTER (WHERE category = '4') AS desocupadas,
       sum(n) AS total_validas,
       sum(n) FILTER (WHERE category = '4') * 100.0 / sum(n) AS pct_vacant
FROM read_parquet('data/interim/full_aggregate_v1a/counts/v1a/categories/canton/**/*.parquet')
WHERE source_table = 'vivienda' AND variable = 'V0201' AND unit_key IN ('0303', '0103')
GROUP BY unit_key;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -78.85,
    -2.8
  ],
  "zoom": 10.2,
  "indicador": "vacant_private_dwellings",
  "filtro": "unit_key IN ('0303', '0103')",
  "capa_extra": "choropleth",
  "resaltados": [
    "0303",
    "0103"
  ]
}
```

---

## Paso 4: La concentración espacial de la vacancia en Quito

> **English Summary:** *Dwelling vacancy in Quito displays statistically significant spatial clustering (Moran's I = 0.389, p < 0.001).*

En las áreas urbanas metropolitanas, la desocupación presenta una clara estructura espacial. En el cantón Quito, el análisis de autocorrelación espacial reporta un índice de Moran de 0,389 con significancia estadística confirmada (p < 0,001), constatando que los sectores censales con mayor porcentaje de viviendas desocupadas tienden a agruparse en zonas urbanas específicas.

- **Cifra clave:** Índice de Moran I de 0,389 (p < 0,001) para desocupación de viviendas en el cantón Quito.
- **Fuente oficial:** INEC / pipeline analitica: spatial_v1b2/moran_canton.parquet (unit_key='1701', indicator='vacancy')

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT unit_key, indicator, moran_i, permutation_p, sectors
FROM read_parquet('data/interim/spatial_v1b2/moran_canton.parquet')
WHERE unit_key = '1701' AND indicator = 'vacancy';
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "sector",
  "centro": [
    -78.5,
    -0.2
  ],
  "zoom": 13.0,
  "indicador": "vacant_private_dwellings",
  "filtro": "canton_key = '1701'",
  "capa_extra": "choropleth",
  "resaltados": [
    "170150001001",
    "170150002002"
  ]
}
```

---

## Paso 5: El contraste del hacinamiento en Guayaquil

> **English Summary:** *In contrast with high vacancy, northwest Guayaquil sectors suffer overcrowding rates exceeding 40%.*

Frente a las zonas con alta desocupación habitacional, el censo identifica sectores con hacinamiento crítico de hogares (más de tres personas por dormitorio exclusivo). En el cantón Guayaquil, el análisis LISA identifica conglomerados significativos de tipo Alto-Alto en el noroeste urbano, donde más del cuarenta por ciento de los hogares habitan en condiciones de hacinamiento.

- **Cifra clave:** Sectores censales en el noroeste de Guayaquil con más del 40% de hogares hacinados (cluster Alto-Alto significativo).
- **Fuente oficial:** INEC / spatial_v1b2/lisa_sector.parquet (canton_key='0901', indicator='overcrowding')

### Consulta SQL Reproducible (DuckDB):
```sql
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

## Paso 6: La relación cantonal entre viviendas y hogares

> **English Summary:** *Ratios of dwellings to households range from 2.4 in rural Austro cantons to 1.05 in coastal urban areas.*

La comparación entre el total de viviendas y los hogares empadronados evidencia asimetrías territoriales marcadas. En cantones como Déleg (Cañar) o Sevilla de Oro (Azuay), la relación supera 2,3 viviendas por cada hogar censado, mientras que en cantones urbanos centrales del litoral la relación se aproxima a 1,05 viviendas por hogar clasificado.

- **Cifra clave:** 2,42 viviendas por hogar en Déleg (4.891 viviendas frente a 2.017 hogares) y 2,36 en Sevilla de Oro.
- **Fuente oficial:** INEC, Censo 2022 / counts: canton/data.parquet

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT unit_key, population, dwellings, households,
       dwellings * 1.0 / NULLIF(households, 0) AS ratio_viv_hog
FROM read_parquet('data/counts/v1b1/canton/data.parquet')
WHERE unit_key IN ('0306', '0112', '0901')
ORDER BY ratio_viv_hog DESC;
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
  "indicador": "vacant_private_dwellings",
  "filtro": "all",
  "capa_extra": "choropleth",
  "resaltados": [
    "0306",
    "0112"
  ]
}
```

---

## Paso 7: ¿Cómo se distribuyen las viviendas en su localidad?

> **English Summary:** *Dwelling occupancy guides housing policy: explore the map to evaluate vacancy and crowding in your area.*

La condición de ocupación de las viviendas constituye un indicador central para planificar la infraestructura de servicios y el acceso habitacional. A través del visualizador cartográfico es posible explorar la tasa de desocupación particular y los niveles de hacinamiento por cantón y sector. ¿Qué porcentaje de viviendas desocupadas registra su entorno censal cercano?

- **Cifra clave:** 766.776 viviendas desocupadas registradas en el censo frente a 458.468 hogares en hacinamiento a nivel nacional.
- **Fuente oficial:** CPV 2022 INEC / indicators.yaml (id: vacant_private_dwellings)

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT sum(n) FILTER (WHERE variable = 'V0201' AND category = '4') AS desocupadas_nacional,
       sum(n) FILTER (WHERE variable = 'HAC' AND category = '1') AS hogares_hacinados_nacional
FROM read_parquet('data/interim/full_aggregate_v1a/counts/v1a/categories/canton/**/*.parquet')
WHERE variable IN ('V0201', 'HAC');
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
  "indicador": "vacant_private_dwellings",
  "filtro": "all",
  "capa_extra": "interactive_explorer",
  "resaltados": []
}
```

---

