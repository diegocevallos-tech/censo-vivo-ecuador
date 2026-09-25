# Guion de Scrollytelling: Los que se fueron

**Identificador:** `02_los_que_se_fueron`  
**Tema Central:** La geografía del éxodo internacional y la movilidad territorial que reconfigura las comunidades ecuatorianas.  
**Número de pasos:** 7  
**Giro contraintuitivo clave:** *La emigración no vacía a las comunidades de forma homogénea: amputa selectivamente a los hombres jóvenes. En cantones del Austro como Santa Isabel (Azuay), la razón de masculinidad entre 20 y 39 años se derrumba a apenas 69,99 varones por cada 100 mujeres, dejando comunidades sostenidas primordialmente por mujeres jefas de hogar y abuelas.*

---

## Paso 1: La huella invisible de las ausencias

> **English Summary:** *Census records reveal nearly one hundred thousand recent emigrants reported by households across Ecuador.*

Cada censo registra puntualmente a quienes habitan las viviendas de una nación, pero también guarda el eco conmovedor de quienes partieron. En el Censo 2022, casi cien mil hogares ecuatorianos reportaron con nombre y memoria que al menos uno de sus seres queridos había emigrado recientemente al extranjero, configurando un mapa de ausencias que atraviesa de norte a sur el territorio nacional.

- **Cifra clave:** 96.825 emigrantes internacionales reportados directamente por sus hogares de origen.
- **Fuente oficial:** INEC, Censo de Población y Vivienda 2022 / counts: nacion/data.parquet

### Consulta SQL Reproducible (DuckDB):
```sql
-- Emigrantes internacionales reportados a nivel nacional
SELECT population, households, emigrants, 
       emigrants * 1000.0 / population AS rate_per_1000
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
  "indicador": "emigrants",
  "filtro": "all",
  "capa_extra": "choropleth",
  "resaltados": [
    "EC"
  ]
}
```

---

## Paso 2: El corazón histórico del éxodo: Azuay y Cañar

> **English Summary:** *In the southern Andes, Cañar and Azuay concentrate the highest rates of international emigration in Ecuador.*

La migración hacia el exterior no brota de forma homogénea en el mapa: hunde raíces seculares en el Austro andino. En Cañar y Azuay, la intensidad del éxodo prácticamente triplica el promedio de la República. Décadas de redes transnacionales consolidadas hacia Norteamérica y Europa han arraigado una cultura migratoria donde viajar al norte constituye el rito de paso obligado para generaciones de jóvenes.

- **Cifra clave:** 38,76 emigrantes por cada mil habitantes en Cañar (8.820 personas) y 28,13 en Azuay (22.550 personas).
- **Fuente oficial:** INEC, Censo 2022 / counts: provincia/data.parquet (unit_keys: '03', '01')

### Consulta SQL Reproducible (DuckDB):
```sql
-- Tasa de emigración por provincia
SELECT unit_key, population, emigrants,
       emigrants * 1000.0 / population AS emig_rate_1000
FROM read_parquet('data/counts/v1b1/provincia/data.parquet')
ORDER BY emig_rate_1000 DESC
LIMIT 5;
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
  "indicador": "emigrants",
  "filtro": "unit_key IN ('01', '03')",
  "capa_extra": "choropleth",
  "resaltados": [
    "01",
    "03"
  ]
}
```

---

## Paso 3: Chunchi: el récord nacional del desarraigo

> **English Summary:** *Chunchi in Chimborazo holds Ecuador's record with over 7% of its resident population having emigrated.*

Si existe un lugar donde la partida de los suyos se palpa en cada rincón, es Chunchi, en el austro de Chimborazo. Más del siete por ciento de toda la población censada en el cantón cuenta con parientes directos que marcharon al extranjero en los últimos años. Las calles empinadas y los campos labrados exhiben una sangría continua de brazos laborales indispensables.

- **Cifra clave:** 7,29% de emigración sobre la población residente en Chunchi (775 emigrantes en un cantón de 10.635 hab).
- **Fuente oficial:** INEC, Censo 2022 / counts: canton/data.parquet (unit_key='0605')

### Consulta SQL Reproducible (DuckDB):
```sql
-- Cantón Chunchi y top cantones con mayor porcentaje de emigrantes
SELECT unit_key, population, households, emigrants,
       emigrants * 100.0 / population AS pct_emig
FROM read_parquet('data/counts/v1b1/canton/data.parquet')
ORDER BY pct_emig DESC
LIMIT 5;
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
  "indicador": "emigrants",
  "filtro": "province_key = '06'",
  "capa_extra": "choropleth",
  "resaltados": [
    "0605"
  ]
}
```

---

## Paso 4: El giro demográfico: la amputación de los varones jóvenes

> **English Summary:** *Migration selectively extracts working-age men: Santa Isabel has only 70 men per 100 women aged 20-39.*

Se asume con frecuencia que la emigración desplaza a familias de manera uniforme. Los datos revelan una distorsión profunda y dolorosa: el viaje es marcadamente selectivo por edad y sexo. En Santa Isabel (Azuay), la razón de masculinidad entre veinte y treinta y nueve años se derrumba a setenta varones por cada cien mujeres. Faltan tres de cada diez hombres jóvenes del cantón.

- **Cifra clave:** 69,99 hombres por cada 100 mujeres de 20 a 39 años en Santa Isabel (2.628 varones frente a 3.755 mujeres).
- **Fuente oficial:** INEC, Censo 2022 / counts: canton/data.parquet (unit_key='0109')

### Consulta SQL Reproducible (DuckDB):
```sql
-- Razón de masculinidad en edades laborales jóvenes (20 a 39 años)
SELECT unit_key, population, emigrants,
       (age_20_24_m::BIGINT + age_25_29_m::BIGINT + age_30_34_m::BIGINT + age_35_39_m::BIGINT) AS men_20_39,
       (age_20_24_f::BIGINT + age_25_29_f::BIGINT + age_30_34_f::BIGINT + age_35_39_f::BIGINT) AS women_20_39,
       men_20_39 * 100.0 / NULLIF(women_20_39, 0) AS sex_ratio_20_39
FROM read_parquet('data/counts/v1b1/canton/data.parquet')
WHERE population >= 5000 AND emigrants * 100.0 / population >= 4.0
ORDER BY sex_ratio_20_39 ASC
LIMIT 5;
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
    "0109",
    "0103"
  ]
}
```

---

## Paso 5: La nueva frontera amazónica de la migración

> **English Summary:** *Morona Santiago now ranks as Ecuador's third highest province in emigration rate, defying expectations.*

Un fenómeno contemporáneo que desafía las lecturas tradicionales es la inserción de la Amazonía en las rutas migratorias globales. Morona Santiago se sitúa hoy como la tercera provincia con mayor tasa de emigración del Ecuador, rebasando a bastiones históricos como Loja o Tungurahua. Comunidades rurales enteras financian peligrosos viajes irregulares, transformando la dinámica económica y social de la selva.

- **Cifra clave:** Tasa provincial de 16,94 emigrantes por cada mil habitantes en Morona Santiago (3.261 personas censadas).
- **Fuente oficial:** INEC, Censo 2022 / counts: provincia/data.parquet (unit_key='14')

### Consulta SQL Reproducible (DuckDB):
```sql
-- Emigración en la provincia de Morona Santiago
SELECT unit_key, population, emigrants,
       emigrants * 1000.0 / population AS rate_1000
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
  "indicador": "emigrants",
  "filtro": "unit_key = '14'",
  "capa_extra": "choropleth",
  "resaltados": [
    "14"
  ]
}
```

---

## Paso 6: El reflejo interior: las ciudades satélite receptoras

> **English Summary:** *Domestically, bedroom cantons like Daule absorb massive waves of internal migrants seeking opportunity.*

Al tiempo que los campos se desangran hacia el exterior, la geografía nacional se reordena puertas adentro. Cantones periféricos y ciudades dormitorio como Daule en Guayas crecieron exponencialmente debido a oleadas de migración interna. Familias procedentes de diversas provincias se instalan en urbanizaciones y barrios suburbanos buscando refugio, empleo y conectividad en las coronas metropolitanas del país.

- **Cifra clave:** Más del 15% de los residentes en cantones periféricos provienen de otro cantón en los últimos cinco años.
- **Fuente oficial:** INEC / cross_counts_v1b2 (residence_other_canton_5)

### Consulta SQL Reproducible (DuckDB):
```sql
-- Migración interna reciente (últimos 5 años) en Daule
SELECT unit_key,
       sum(residence_other_canton_5) AS personas_otro_canton,
       sum(birth_other_canton) AS nacidos_otro_canton
FROM read_parquet('data/interim/cross_counts_v1b2/sector/data.parquet')
WHERE unit_key LIKE '0906%'
GROUP BY unit_key;
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
  "indicador": "internal_arrivals_5y",
  "filtro": "province_key = '09'",
  "capa_extra": "flow_arrows",
  "resaltados": [
    "0906",
    "0916"
  ]
}
```

---

## Paso 7: ¿Qué vacío dejó la partida en tu comunidad?

> **English Summary:** *Migration shapes communities at home and abroad: explore the map to uncover the migration balance in your town.*

La migración sostiene la economía nacional mediante un caudaloso flujo de remesas, pero su costo social no se compensa con dólares: familias divididas por océanos y territorios sin brazos productivos. ¿Cuál es la realidad de tu entorno? ¿Has visto partir a tus vecinos hacia destinos lejanos o convives con nuevos vecinos llegados desde otras provincias ecuatorianas?

- **Cifra clave:** Cerca de 100.000 hogares con ausencias directas narran la historia viva de la movilidad en el Ecuador.
- **Fuente oficial:** CPV 2022 INEC / Explorador interactivo Censo Vivo

### Consulta SQL Reproducible (DuckDB):
```sql
-- Resumen general de movilidad por provincia
SELECT unit_key, population, emigrants,
       emigrants * 100.0 / population AS pct_emig
FROM read_parquet('data/counts/v1b1/provincia/data.parquet')
ORDER BY pct_emig DESC;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "provincia",
  "centro": [
    -78.5,
    -1.5
  ],
  "zoom": 7.0,
  "indicador": "emigrants",
  "filtro": "all",
  "capa_extra": "interactive_explorer",
  "resaltados": []
}
```

---

