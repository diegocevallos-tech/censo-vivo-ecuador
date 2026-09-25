# Guion de Scrollytelling: El Ecuador que envejece

**Identificador:** `01_ecuador_envejece`  
**Tema Central:** La transición demográfica nacional y la fractura generacional entre la Amazonía joven y los enclaves urbanos y rurales envejecidos.  
**Número de pasos:** 7  
**Giro contraintuitivo clave:** *El envejecimiento extremo no es exclusivo de aldeas rurales despobladas: en las torres residenciales de alta plusvalía de Quito (Iñaquito, González Suárez), el envejecimiento supera los 135 adultos mayores por cada 100 niños, con alta prevalencia de personas mayores viviendo solas, a escasos diez kilómetros de la marea infantil de Calderón.*

---

## Paso 1: El punto de quiebre demográfico nacional

> **English Summary:** *Ecuador marks an irreversible demographic turning point with over 35 seniors per 100 children nationwide.*

Durante generaciones crecimos pensando en el Ecuador como un país eminentemente joven y vital. Los resultados del Censo 2022 confirman un punto de inflexión histórico e irreversible: por cada cien menores de quince años ya habitan más de treinta y cinco adultos mayores. La base de la pirámide poblacional se estrecha aceleradamente, anticipando el fin del bono demográfico antes de haber alcanzado el desarrollo social pleno.

- **Cifra clave:** 35,26 adultos mayores por cada 100 niños (1.520.590 personas de 65+ frente a 4.312.989 de 0 a 14 años sobre 16.938.986 habitantes censados).
- **Fuente oficial:** INEC, Censo de Población y Vivienda 2022 (Boletín Nacional) / counts: nacion/data.parquet

### Consulta SQL Reproducible (DuckDB):
```sql
-- Consulta en DuckDB: Índice de envejecimiento nacional
SELECT 
    population,
    (age_00_04_m::BIGINT + age_00_04_f::BIGINT + age_05_09_m::BIGINT + age_05_09_f::BIGINT + age_10_14_m::BIGINT + age_10_14_f::BIGINT) AS pop_0_14,
    (age_65_69_m::BIGINT + age_65_69_f::BIGINT + age_70_74_m::BIGINT + age_70_74_f::BIGINT + age_75_79_m::BIGINT + age_75_79_f::BIGINT + 
     age_80_84_m::BIGINT + age_80_84_f::BIGINT + age_85_89_m::BIGINT + age_85_89_f::BIGINT + age_90_94_m::BIGINT + age_90_94_f::BIGINT + 
     age_95_99_m::BIGINT + age_95_99_f::BIGINT + age_100_120_m::BIGINT + age_100_120_f::BIGINT) AS pop_65_plus,
    pop_65_plus * 100.0 / NULLIF(pop_0_14, 0) AS aging_index
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
  "indicador": "aging_index",
  "filtro": "all",
  "capa_extra": "choropleth",
  "resaltados": [
    "EC"
  ]
}
```

---

## Paso 2: La Amazonía: el último bastión de la juventud

> **English Summary:** *Deep in the southern Amazon, cantons like Taisha remain vibrantly young with only 5 seniors per 100 children.*

Al adentrarnos en las selvas de la Amazonía sur, la geografía humana cambia por completo de compás. En cantones selváticos como Taisha o Tiwintza, casi la mitad de los habitantes son niñas y niños, mientras los adultos mayores apenas rozan el dos por ciento. Aquí la vitalidad biológica permanece vigorosa, contrastando de forma dramática con la tendencia general que ya predomina en el resto del territorio ecuatoriano.

- **Cifra clave:** Índice de envejecimiento de 5,15 en Taisha (12.981 niños vs 669 ancianos en 26.700 habitantes).
- **Fuente oficial:** INEC, Censo de Población y Vivienda 2022 / counts: canton/data.parquet (unit_key='1409')

### Consulta SQL Reproducible (DuckDB):
```sql
-- Cantones amazónicos más jóvenes
SELECT 
    unit_key, population,
    (age_00_04_m::BIGINT + age_00_04_f::BIGINT + age_05_09_m::BIGINT + age_05_09_f::BIGINT + age_10_14_m::BIGINT + age_10_14_f::BIGINT) AS pop_0_14,
    (age_65_69_m::BIGINT + age_65_69_f::BIGINT + age_70_74_m::BIGINT + age_70_74_f::BIGINT + age_75_79_m::BIGINT + age_75_79_f::BIGINT + 
     age_80_84_m::BIGINT + age_80_84_f::BIGINT + age_85_89_m::BIGINT + age_85_89_f::BIGINT + age_90_94_m::BIGINT + age_90_94_f::BIGINT + 
     age_95_99_m::BIGINT + age_95_99_f::BIGINT + age_100_120_m::BIGINT + age_100_120_f::BIGINT) AS pop_65_plus,
    pop_65_plus * 100.0 / NULLIF(pop_0_14, 0) AS aging_index
FROM read_parquet('data/counts/v1b1/canton/data.parquet')
WHERE unit_key = '1409';
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -77.5,
    -2.38
  ],
  "zoom": 8.5,
  "indicador": "aging_index",
  "filtro": "province_key = '14'",
  "capa_extra": "choropleth",
  "resaltados": [
    "1409",
    "1412"
  ]
}
```

---

## Paso 3: La Sierra austral: cuando los abuelos superan a los nietos

> **English Summary:** *In southern Andean cantons like Olmedo and Sevilla de Oro, seniors now outnumber children.*

Al ascender por los valles andinos del Austro, el mapa poblacional da un vuelco radical. En cantones como Olmedo y Chaguarpamba en Loja, o Sevilla de Oro en Azuay, la pirámide ya se invirtió: existen más personas de la tercera edad que infancias menores de quince años. El éxodo migratorio histórico y la caída de la natalidad convirtieron a estas poblaciones en oasis de retiro campesino.

- **Cifra clave:** Índice de envejecimiento de 103,98 en Olmedo (Loja), 103,16 en Sevilla de Oro (Azuay) y 102,80 en Chaguarpamba (Loja).
- **Fuente oficial:** INEC, Censo 2022 / counts: canton/data.parquet (unit_keys: '1115', '0112', '1116')

### Consulta SQL Reproducible (DuckDB):
```sql
-- Cantones donde los adultos mayores superan a los menores de 15 años
SELECT 
    unit_key, population,
    (age_00_04_m::BIGINT + age_00_04_f::BIGINT + age_05_09_m::BIGINT + age_05_09_f::BIGINT + age_10_14_m::BIGINT + age_10_14_f::BIGINT) AS pop_0_14,
    (age_65_69_m::BIGINT + age_65_69_f::BIGINT + age_70_74_m::BIGINT + age_70_74_f::BIGINT + age_75_79_m::BIGINT + age_75_79_f::BIGINT + 
     age_80_84_m::BIGINT + age_80_84_f::BIGINT + age_85_89_m::BIGINT + age_85_89_f::BIGINT + age_90_94_m::BIGINT + age_90_94_f::BIGINT + 
     age_95_99_m::BIGINT + age_95_99_f::BIGINT + age_100_120_m::BIGINT + age_100_120_f::BIGINT) AS pop_65_plus,
    pop_65_plus * 100.0 / NULLIF(pop_0_14, 0) AS aging_index
FROM read_parquet('data/counts/v1b1/canton/data.parquet')
WHERE pop_65_plus > pop_0_14
ORDER BY aging_index DESC;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "canton",
  "centro": [
    -79.4,
    -3.85
  ],
  "zoom": 8.8,
  "indicador": "aging_index",
  "filtro": "province_key IN ('01', '11')",
  "capa_extra": "choropleth",
  "resaltados": [
    "1115",
    "0112",
    "1116"
  ]
}
```

---

## Paso 4: Palmira: el epicentro parroquial de la longevidad

> **English Summary:** *At the parish level, Palmira in Chimborazo records an extreme 226 seniors per 100 children.*

Si afinamos la escala al nivel parroquial, emergen realidades todavía más sobrecogedoras. En Palmira, una parroquia andina de Chimborazo erosionada por la emigración juvenil, viven más de doscientos veintiséis ancianos por cada centenar de infantes. Las faenas agrarias y el cuidado cotidiano descansan hoy sobre espaldas mayores que sostienen la vida comunitaria en condiciones de severa precariedad económica y aislamiento institucional.

- **Cifra clave:** Índice de envejecimiento récord de 226,22 en Palmira (1.070 adultos mayores vs 473 niños en 3.188 habitantes).
- **Fuente oficial:** INEC, Censo 2022 / counts: parroquia/data.parquet (unit_key='060354')

### Consulta SQL Reproducible (DuckDB):
```sql
-- Parroquia Palmira (Guamote, Chimborazo)
SELECT 
    unit_key, population,
    (age_00_04_m::BIGINT + age_00_04_f::BIGINT + age_05_09_m::BIGINT + age_05_09_f::BIGINT + age_10_14_m::BIGINT + age_10_14_f::BIGINT) AS pop_0_14,
    (age_65_69_m::BIGINT + age_65_69_f::BIGINT + age_70_74_m::BIGINT + age_70_74_f::BIGINT + age_75_79_m::BIGINT + age_75_79_f::BIGINT + 
     age_80_84_m::BIGINT + age_80_84_f::BIGINT + age_85_89_m::BIGINT + age_85_89_f::BIGINT + age_90_94_m::BIGINT + age_90_94_f::BIGINT + 
     age_95_99_m::BIGINT + age_95_99_f::BIGINT + age_100_120_m::BIGINT + age_100_120_f::BIGINT) AS pop_65_plus,
    pop_65_plus * 100.0 / NULLIF(pop_0_14, 0) AS aging_index
FROM read_parquet('data/counts/v1b1/parroquia/data.parquet')
WHERE unit_key = '060354';
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "parroquia",
  "centro": [
    -78.75,
    -2.1
  ],
  "zoom": 10.5,
  "indicador": "aging_index",
  "filtro": "canton_key = '0603'",
  "capa_extra": "choropleth",
  "resaltados": [
    "060354"
  ]
}
```

---

## Paso 5: El giro urbano: la vejez en las torres de alta plusvalía

> **English Summary:** *Debunking common assumptions, Quito's wealthiest high-rise districts match rural areas in extreme aging.*

Existe la convicción generalizada de que la senectud es un fenómeno propio de aldeas rurales abandonadas. Los datos desmienten el mito de raíz: los barrios más ricos y cotizados de Quito muestran niveles de envejecimiento idénticos a los del campo andino. En Iñaquito y González Suárez abundan edificios modernos habitados casi exclusivamente por jubilados y hogares unipersonales de avanzada edad.

- **Cifra clave:** Índice de envejecimiento superior a 135 mayores por cada 100 niños en sectores de Iñaquito y González Suárez, con alta soledad en 65+.
- **Fuente oficial:** INEC / pipeline analitica: sector_clusters.parquet y cross_counts_v1b2 (solitary_65)

### Consulta SQL Reproducible (DuckDB):
```sql
-- Sectores residenciales urbanos de Quito con alto envejecimiento
SELECT 
    c.unit_key, c.population,
    c.pop_65_plus * 100.0 / NULLIF(c.pop_0_14, 0) AS aging_index,
    x.solitary_65 * 100.0 / NULLIF(x.all_65, 0) AS pct_solitude_65
FROM (
    SELECT unit_key, population,
        (age_00_04_m::BIGINT + age_00_04_f::BIGINT + age_05_09_m::BIGINT + age_05_09_f::BIGINT + age_10_14_m::BIGINT + age_10_14_f::BIGINT) AS pop_0_14,
        (age_65_69_m::BIGINT + age_65_69_f::BIGINT + age_70_74_m::BIGINT + age_70_74_f::BIGINT + age_75_79_m::BIGINT + age_75_79_f::BIGINT + 
         age_80_84_m::BIGINT + age_80_84_f::BIGINT + age_85_89_m::BIGINT + age_85_89_f::BIGINT + age_90_94_m::BIGINT + age_90_94_f::BIGINT + 
         age_95_99_m::BIGINT + age_95_99_f::BIGINT + age_100_120_m::BIGINT + age_100_120_f::BIGINT) AS pop_65_plus
    FROM read_parquet('data/counts/v1b1/sector/17.parquet')
) c
JOIN read_parquet('data/interim/cross_counts_v1b2/sector/data.parquet') x USING (unit_key)
WHERE c.unit_key LIKE '170150%' AND c.population >= 300
ORDER BY aging_index DESC
LIMIT 5;
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "sector",
  "centro": [
    -78.482,
    -0.188
  ],
  "zoom": 13.8,
  "indicador": "aging_index",
  "filtro": "parish_key = '170150'",
  "capa_extra": "3D_extrusion",
  "resaltados": [
    "170150004001",
    "170150005002"
  ]
}
```

---

## Paso 6: La fractura metropolitana: dos mundos a diez kilómetros

> **English Summary:** *Only 10 kilometers apart, Quito splits between senior-dominated Iñaquito and child-filled Calderón.*

Bastan quince minutos de viaje para comprobar la fractura demográfica de la capital. Mientras el centro financiero envejece en departamentos silenciosos, la periferia de Calderón bulle de parques infantiles y escuelas saturadas de estudiantes. La ciudad concentra en su seno las dos fases extremas de la transición demográfica: una brecha generacional de seis a uno que tensiona el transporte, los servicios y la salud pública.

- **Cifra clave:** Índice de envejecimiento de 135,2 en Iñaquito frente a 22,4 en Calderón: seis veces más niños por adulto mayor en la periferia.
- **Fuente oficial:** INEC, Censo 2022 / counts: parroquia/data.parquet (unit_keys: '170150', '170152')

### Consulta SQL Reproducible (DuckDB):
```sql
-- Comparación Iñaquito vs Calderón en Quito
SELECT 
    unit_key,
    CASE WHEN unit_key = '170150' THEN 'Iñaquito (Centro Norte)' ELSE 'Calderón (Periferia Norte)' END AS sector_nombre,
    population,
    (age_00_04_m::BIGINT + age_00_04_f::BIGINT + age_05_09_m::BIGINT + age_05_09_f::BIGINT + age_10_14_m::BIGINT + age_10_14_f::BIGINT) AS pop_0_14,
    (age_65_69_m::BIGINT + age_65_69_f::BIGINT + age_70_74_m::BIGINT + age_70_74_f::BIGINT + age_75_79_m::BIGINT + age_75_79_f::BIGINT + 
     age_80_84_m::BIGINT + age_80_84_f::BIGINT + age_85_89_m::BIGINT + age_85_89_f::BIGINT + age_90_94_m::BIGINT + age_90_94_f::BIGINT + 
     age_95_99_m::BIGINT + age_95_99_f::BIGINT + age_100_120_m::BIGINT + age_100_120_f::BIGINT) AS pop_65_plus,
    pop_65_plus * 100.0 / NULLIF(pop_0_14, 0) AS aging_index
FROM read_parquet('data/counts/v1b1/parroquia/data.parquet')
WHERE unit_key IN ('170150', '170152');
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "parroquia",
  "centro": [
    -78.46,
    -0.14
  ],
  "zoom": 11.2,
  "indicador": "aging_index",
  "filtro": "canton_key = '1701'",
  "capa_extra": "choropleth",
  "resaltados": [
    "170150",
    "170152"
  ]
}
```

---

## Paso 7: ¿Cómo envejece tu propio entorno?

> **English Summary:** *Demographic aging reshapes our future: explore the interactive map to discover how your neighborhood is aging.*

El envejecimiento no es una estadística abstracta: determina qué escuelas cerrarán sus aulas, dónde harán falta geriatras y cómo se sostendrá el sistema de pensiones del porvenir. Las diferencias territoriales demuestran que no hay una única receta para el país. ¿Cómo late el pulso demográfico de tu cantón o barrio? ¿Predomina la juventud o el reloj generacional avanza ya hacia el ocaso?

- **Cifra clave:** 1,5 millones de adultos mayores demandan una nueva arquitectura de cuidados en el Ecuador.
- **Fuente oficial:** CPV 2022 INEC / Explorador interactivo Censo Vivo

### Consulta SQL Reproducible (DuckDB):
```sql
-- Consulta abierta: distribución nacional del índice de envejecimiento por cantón
SELECT 
    percentile_cont(0.25) WITHIN GROUP (ORDER BY aging_index) AS q1,
    percentile_cont(0.50) WITHIN GROUP (ORDER BY aging_index) AS mediana,
    percentile_cont(0.75) WITHIN GROUP (ORDER BY aging_index) AS q3
FROM (
    SELECT pop_65_plus * 100.0 / NULLIF(pop_0_14, 0) AS aging_index
    FROM read_parquet('data/counts/v1b1/canton/data.parquet')
);
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
  "indicador": "aging_index",
  "filtro": "all",
  "capa_extra": "interactive_explorer",
  "resaltados": []
}
```

---

