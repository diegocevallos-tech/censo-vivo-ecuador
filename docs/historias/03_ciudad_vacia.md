# La ciudad vacía

**ID de la Historia:** `03_ciudad_vacia`  
**Descripción:** Distribución de viviendas particulares desocupadas en Ecuador, contrastes territoriales y segregación urbana.

---

## Paso 1: La radiografía habitacional: 11,63% de viviendas desocupadas

**English Title:** *Housing Diagnostic: 11.63% Vacant Dwellings*

El Censo 2022 registró 6.595.318 viviendas particulares con condición de ocupación válida en el Ecuador. De ellas, 766.776 se encontraban desocupadas, lo que representa una tasa nacional de desocupación habitacional del 11,63% (V0201=4). Esta cifra excluye a las viviendas colectivas y constituye el parámetro de comparación en todo el territorio.

**Resumen en inglés:** Nationally, 766,776 private dwellings are vacant, representing 11.63% of all valid private dwellings.  

**Cifra clave:** `11.63 % de viviendas particulares válidas` (Fuente: *INEC CPV 2022, categories/nacion/data.parquet (V0201)*)

```sql
SELECT sum(n) FILTER (WHERE category='4') * 100.0 / sum(n) AS vacant_rate FROM 'data/derived/counts/v1b1/categories/nacion/data.parquet' WHERE variable='V0201';
```

```json
{
  "nivel": "nacion",
  "centro": [
    -78.1834,
    -1.8312
  ],
  "zoom": 6.2,
  "indicador": "vacant_private_dwellings",
  "filtro": null,
  "capa_extra": null,
  "resaltados": [
    "EC"
  ]
}
```

---

## Paso 2: El récord nacional de desocupación: Cañar y Suscal

**English Title:** *National Vacancy Record: Cañar and Suscal*

A escala cantonal, la mayor concentración de viviendas desocupadas se localiza en la provincia de Cañar. El cantón Cañar lidera el país con un 26,41% de desocupación (2.621 viviendas desocupadas sobre 9.925 particulares). En el vecino cantón Suscal, la tasa asciende a 23,12% (567 de 2.452), más del doble del promedio nacional.

**Resumen en inglés:** Cañar (26.41%) and Suscal (23.12%) exhibit Ecuador's highest cantonal private dwelling vacancy rates.  

**Cifra clave:** `26.41 % de viviendas particulares` (Fuente: *INEC CPV 2022, categories/canton/03.parquet (unit_keys: '0302', '0307')*)

```sql
SELECT canton_key, sum(n) FILTER (WHERE category='4') * 100.0 / sum(n) AS vacant_rate FROM 'data/derived/counts/v1b1/categories/canton/03.parquet' WHERE variable='V0201' AND canton_key IN ('0302', '0307') GROUP BY canton_key;
```

```json
{
  "nivel": "canton",
  "centro": [
    -78.93,
    -2.56
  ],
  "zoom": 10.0,
  "indicador": "vacant_private_dwellings",
  "filtro": "unit_key IN ('0302', '0307')",
  "capa_extra": null,
  "resaltados": [
    "0302",
    "0307"
  ]
}
```

---

## Paso 3: El cinturón de vivienda deshabitada del Austro

**English Title:** *The Southern Sierra Vacant Housing Belt*

El fenómeno de desocupación residencial abarca de forma continua a múltiples cantones de la Sierra austral. En Biblián, el 21,57% de las viviendas particulares está desocupado (5.346 unidades). En Gualaceo (Azuay), la cifra alcanza el 19,88% (4.177 unidades). En ambos cantones, una de cada cinco viviendas particulares registradas no contaba con ocupantes habituales durante el censo.

**Resumen en inglés:** Biblián (21.57%) and Gualaceo (19.88%) form a continuous cluster of high housing vacancy in the southern Andes.  

**Cifra clave:** `21.57 % de viviendas particulares` (Fuente: *INEC CPV 2022, categories/canton/03.parquet y 01.parquet*)

```sql
SELECT canton_key, sum(n) FILTER (WHERE category='4') * 100.0 / sum(n) AS vacant_rate FROM 'data/derived/counts/v1b1/categories/canton/*.parquet' WHERE variable='V0201' AND canton_key IN ('0303', '0103') GROUP BY canton_key;
```

```json
{
  "nivel": "canton",
  "centro": [
    -78.9,
    -2.8
  ],
  "zoom": 9.5,
  "indicador": "vacant_private_dwellings",
  "filtro": "unit_key IN ('0303', '0103')",
  "capa_extra": null,
  "resaltados": [
    "0303",
    "0103"
  ]
}
```

---

## Paso 4: La segregación urbana en Quito: vacancia residencial agrupada

**English Title:** *Urban Segregation in Quito: Clustered Housing Vacancy*

En las áreas metropolitanas, la desocupación no se distribuye al azar, sino en conglomerados espaciales definidos. El análisis de autocorrelación espacial en Quito arroja un índice I de Moran de 0,389 (p < 0,001), confirmando la concentración de manzanas con alta desocupación en sectores consolidados del norte y centro norte de la ciudad.

**Resumen en inglés:** Spatial autocorrelation in Quito confirms significant spatial clustering of vacant housing (Moran's I = 0.389).  

**Cifra clave:** `0.389 coeficiente de autocorrelación espacial (p < 0,001)` (Fuente: *Analítica 1B-2, spatial_v1b2/moran_canton.parquet (canton='1701')*)

```sql
SELECT canton_key, indicator, moran_i, p_value FROM 'pipeline/analitica/moran_canton.parquet' WHERE canton_key = '1701' AND indicator = 'vacant_private_dwellings';
```

```json
{
  "nivel": "sector",
  "centro": [
    -78.485,
    -0.19
  ],
  "zoom": 13.0,
  "indicador": "vacant_private_dwellings",
  "filtro": "canton_key = '1701'",
  "capa_extra": "lisa_clusters",
  "resaltados": [
    "1701"
  ]
}
```

---

## Paso 5: La paradoja territorial: vacancia austral frente a hacinamiento en Guayaquil

**English Title:** *The Territorial Paradox: Southern Vacancy vs Guayaquil Overcrowding*

La geografía habitacional ecuatoriana expone un marcado desbalance. Mientras Cañar y Biblián superan el 20% de viviendas particulares desocupadas, sectores del noroeste de Guayaquil registran tasas de hacinamiento superiores al 40% en hogares particulares. En un mismo territorio coexisten viviendas deshabitadas en unas provincias y sobreocupación crítica en otras.

**Resumen en inglés:** The contrast between southern vacancy (>20%) and Guayaquil northwestern overcrowding (>40%) reveals stark spatial disparities.  

**Cifra clave:** `40.0 % de hogares con > 3 personas por dormitorio` (Fuente: *Analítica 1B-2 / CPV 2022, lisa_sector.parquet (canton='0901')*)

```sql
SELECT canton_key, round(avg(pct_overcrowding), 2) FROM 'pipeline/analitica/lisa_sector.parquet' WHERE canton_key = '0901' GROUP BY canton_key;
```

```json
{
  "nivel": "canton",
  "centro": [
    -79.92,
    -2.15
  ],
  "zoom": 11.0,
  "indicador": "overcrowding",
  "filtro": "canton_key IN ('0302', '0901')",
  "capa_extra": "split_view",
  "resaltados": [
    "0302",
    "0901"
  ]
}
```

---

## Paso 6: La densidad de viviendas por hogar: el indicador estructural

**English Title:** *Dwellings per Household: The Structural Indicator*

Al cruzar el número total de viviendas particulares con el número de hogares residentes, cantones como Déleg registran 2,42 viviendas por cada hogar (4.891 viviendas frente a 2.017 hogares). En Sevilla de Oro, la relación es de 2,36 viviendas por hogar (2.101 viviendas y 890 hogares), reflejando un parque edificado que duplica al número de familias residentes.

**Resumen en inglés:** In Déleg (2.42) and Sevilla de Oro (2.36), total dwellings double the number of resident households.  

**Cifra clave:** `2.42 viviendas por cada hogar residente` (Fuente: *INEC CPV 2022, canton/data.parquet (unit_keys: '0306', '0112')*)

```sql
SELECT unit_key, dwellings, households, dwellings * 1.0 / households AS ratio FROM 'data/derived/counts/v1b1/canton/data.parquet' WHERE unit_key IN ('0306', '0112');
```

```json
{
  "nivel": "canton",
  "centro": [
    -78.92,
    -2.78
  ],
  "zoom": 10.5,
  "indicador": "vacant_private_dwellings",
  "filtro": "unit_key IN ('0306', '0112')",
  "capa_extra": null,
  "resaltados": [
    "0306",
    "0112"
  ]
}
```

---

## Paso 7: ¿Cómo planificar ciudades e infraestructuras con viviendas vacías?

**English Title:** *How Can Cities and Infrastructure Be Planned With Vacant Housing?*

Cuando miles de viviendas permanecen desocupadas en cantones rurales y pequeñas ciudades, el costo de mantener redes de agua, vialidad y electricidad recae sobre una población residente reducida. ¿Cómo deben articularse las políticas fiscales municipales y de vivienda pública frente a esta asimetría entre edificaciones deshabitadas y necesidades habitacionales insatisfechas?

**Resumen en inglés:** Fiscal and urban planning dilemmas when infrastructure must serve a substantial volume of unoccupied housing units.  

**Cifra clave:** `N/A reflexión analítica` (Fuente: *Censo Ecuador 2022*)

```json
{
  "nivel": "canton",
  "centro": [
    -78.95,
    -2.75
  ],
  "zoom": 8.0,
  "indicador": "vacant_private_dwellings",
  "filtro": null,
  "capa_extra": null,
  "resaltados": []
}
```

---
