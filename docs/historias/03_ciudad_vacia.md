# La ciudad vacía

**ID de la Historia:** `03_ciudad_vacia`  
**Descripción:** Distribución de viviendas particulares desocupadas en Ecuador, contrastes territoriales y segregación urbana.

---

## Paso 1: La escala nacional de la desocupación: 766.776 viviendas

**English Title:** *National Scale of Vacancy: 766,776 Dwellings*

El Censo 2022 empadronó 6.595.318 viviendas particulares con condición de ocupación válida. De ellas, 766.776 viviendas se clasificaron como desocupadas (V0201=4), lo que representa el 11,63% del parque habitacional particular del Ecuador. Más de una de cada nueve viviendas registradas por los censistas se encontraba completamente vacía al momento del levantamiento.

**Resumen en inglés:** Nationwide, 11.63% of private dwellings (766,776 out of 6,595,318) were recorded as vacant in CPV 2022.  

**Cifra clave:** `11.63 % del total de viviendas particulares` (Fuente: *INEC CPV 2022, categories/nacion/data.parquet (V0201=4)*)

```sql
SELECT category, n, n * 100.0 / sum(n) OVER () AS pct FROM 'data/derived/counts/v1b1/categories/nacion/data.parquet' WHERE variable = 'V0201';
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

## Paso 2: El récord cantonal: Cañar y Suscal

**English Title:** *Cantonal Peak: Cañar and Suscal*

Al analizar la distribución cantonal, la desocupación de viviendas particulares alcanza sus máximos en la provincia de Cañar. En el cantón Cañar, el 26,41% de las viviendas particulares está desocupada (2.621 viviendas desocupadas de 9.925 registradas). En Suscal la cifra se sitúa en 23,12% (567 de 2.452 viviendas). En ambos territorios, más de una de cada cuatro viviendas permanece vacía.

**Resumen en inglés:** Peak vacancy rates appear in cantons Cañar (26.41%) and Suscal (23.12%), where over one in four homes is vacant.  

**Cifra clave:** `26.41 % de viviendas particulares` (Fuente: *INEC CPV 2022, categories/canton/03.parquet (unit_keys: '0302', '0307')*)

```sql
SELECT unit_key, sum(CASE WHEN category = '4' THEN n ELSE 0 END) * 100.0 / sum(n) AS pct_vacant FROM 'data/derived/counts/v1b1/categories/canton/03.parquet' WHERE variable = 'V0201' AND unit_key IN ('0302', '0307') GROUP BY unit_key;
```

```json
{
  "nivel": "canton",
  "centro": [
    -78.95,
    -2.55
  ],
  "zoom": 9.5,
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

## Paso 3: El corredor del Austro: Biblián y Gualaceo

**English Title:** *The Austro Corridor: Biblián and Gualaceo*

El patrón de alta desocupación de viviendas particulares forma un corredor continuo en el Austro. En Biblián (Cañar), el 21,57% de las viviendas está desocupada (5.346 viviendas vacías de 24.785 totales). En Gualaceo (Azuay), la cifra alcanza el 19,88% (4.177 de 21.011 viviendas). En estos cantones con altas tasas de emigración histórica, una de cada cinco viviendas permanece deshabitada.

**Resumen en inglés:** A continuous vacancy belt spans across Biblián (21.57%) and Gualaceo (19.88%) in the southern Sierra.  

**Cifra clave:** `21.57 % de viviendas particulares` (Fuente: *INEC CPV 2022, categories/canton/03.parquet y 01.parquet*)

```sql
SELECT unit_key, sum(CASE WHEN category = '4' THEN n ELSE 0 END) * 100.0 / sum(n) AS pct_vacant FROM 'data/derived/counts/v1b1/categories/canton/03.parquet' WHERE variable = 'V0201' AND unit_key = '0303' GROUP BY unit_key;
```

```json
{
  "nivel": "canton",
  "centro": [
    -78.85,
    -2.85
  ],
  "zoom": 9.8,
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

## Paso 4: La vacancia urbana intraurbana: Quito centro vs periferia

**English Title:** *Intra-urban Vacancy: Quito Center vs Periphery*

La desocupación no es exclusiva de cantones rurales o expulsores. En el Distrito Metropolitano de Quito, el análisis espacial de autocorrelación local (Moran I global = 0,389, p < 0,001) identifica agrupamientos de alta vacancia en sectores centrales y áreas consolidadas, coexistiendo con sectores periféricos de rápido poblamiento donde la desocupación es casi inexistente.

**Resumen en inglés:** Within Quito, spatial autocorrelation (Moran's I = 0.389) reveals high-vacancy clusters in consolidated urban sectors.  

**Cifra clave:** `0.389 índice Moran's I (p < 0.001)` (Fuente: *INEC CPV 2022, matriz espacial analítica Fase 1B-2 (spatial_v1b2/moran_canton.parquet)*)

```sql
SELECT canton_key, moran_i, p_value FROM 'spatial_v1b2/moran_canton.parquet' WHERE indicator = 'vacancy' AND canton_key = '1701';
```

```json
{
  "nivel": "sector",
  "centro": [
    -78.48,
    -0.18
  ],
  "zoom": 12.0,
  "indicador": "vacant_private_dwellings",
  "filtro": "canton_key = '1701'",
  "capa_extra": "3d_extrusion",
  "resaltados": []
}
```

---

## Paso 5: La paradoja territorial: viviendas vacías frente a hacinamiento

**English Title:** *The Territorial Paradox: Vacant Dwellings vs Overcrowding*

El censo evidencia profundas asimetrías habitacionales: mientras en cantones del Austro una de cada cuatro viviendas particulares está desocupada, en sectores del noroeste de Guayaquil el hacinamiento supera el 40% de los hogares. La disponibilidad física de techos no coincide geográficamente con los centros de demanda residencial crítica.

**Resumen en inglés:** Sharp territorial contrast: massive vacancy in the Austro coexists with overcrowding exceeding 40% in northwest Guayaquil.  

**Cifra clave:** `40.0 % de hogares hacinados` (Fuente: *INEC CPV 2022, clusterización LISA Fase 1B-2 (spatial_v1b2/lisa_sector.parquet)*)

```sql
SELECT sector_key, overcrowding_pct FROM 'spatial_v1b2/lisa_sector.parquet' WHERE canton_key = '0901' AND lisa_cluster = 'HH' ORDER BY overcrowding_pct DESC LIMIT 10;
```

```json
{
  "nivel": "sector",
  "centro": [
    -79.95,
    -2.12
  ],
  "zoom": 11.5,
  "indicador": "overcrowding",
  "filtro": "canton_key = '0901'",
  "capa_extra": null,
  "resaltados": []
}
```

---

## Paso 6: El giro de la densidad: más viviendas que hogares

**English Title:** *The Density Twist: More Dwellings than Households*

El fenómeno de la desocupación produce un indicador contraintuitivo: la relación entre viviendas y hogares supera ampliamente la unidad. En el cantón Déleg (Cañar) existen 2,42 viviendas particulares por cada hogar censado (4.891 viviendas particulares para 2.017 hogares). En Sevilla de Oro (Azuay) la relación llega a 2,36 (2.101 viviendas para 890 hogares). Hay más del doble de estructuras habitacionales que familias.

**Resumen en inglés:** In Déleg (2.42) and Sevilla de Oro (2.36), there are more than twice as many dwellings as resident households.  

**Cifra clave:** `2.42 viviendas por cada hogar` (Fuente: *INEC CPV 2022, canton/data.parquet (unit_keys: '0306', '0112')*)

```sql
SELECT unit_key, dwellings, households, dwellings * 1.0 / households AS dwellings_per_household FROM 'data/derived/counts/v1b1/canton/data.parquet' WHERE unit_key IN ('0306', '0112');
```

```json
{
  "nivel": "canton",
  "centro": [
    -78.9,
    -2.78
  ],
  "zoom": 10.5,
  "indicador": "dwellings_per_household",
  "filtro": "unit_key IN ('0306', '0112')",
  "capa_extra": null,
  "resaltados": [
    "0306",
    "0112"
  ]
}
```

---

## Paso 7: ¿Viviendas sin gente o gente sin vivienda?

**English Title:** *Homes Without People or People Without Homes?*

Con más de 760.000 viviendas desocupadas a nivel nacional y cantones donde las casas duplican a los hogares, el censo plantea un desafío urbano de primer orden. Cuando la inversión habitacional no coincide con las necesidades de ocupación de las familias, ¿qué políticas de suelo y vivienda se requieren para mitigar este desbalance estructural?

**Resumen en inglés:** Open policy questions regarding spatial mismatches between housing investment and social demand.  

**Cifra clave:** `N/A reflexión analítica` (Fuente: *Censo Ecuador 2022*)

```json
{
  "nivel": "canton",
  "centro": [
    -78.1834,
    -1.8312
  ],
  "zoom": 6.8,
  "indicador": "vacant_private_dwellings",
  "filtro": null,
  "capa_extra": null,
  "resaltados": []
}
```

---
