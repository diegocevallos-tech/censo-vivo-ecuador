# Guion de Scrollytelling: El Ecuador que envejece

**Identificador:** `01_ecuador_envejece`  
**Tema Central:** La transición demográfica nacional y la disparidad generacional entre la Amazonía y los enclaves rurales y urbanos envejecidos.  
**Número de pasos:** 7  
**Giro contraintuitivo comprobado:** *El envejecimiento no es exclusivo de áreas rurales: en sectores urbanos de la parroquia Iñaquito en Quito, el índice de envejecimiento supera los 135 adultos mayores por cada 100 menores de 15 años, superando a parroquias rurales como Calderón (35,88) en el mismo cantón.*

---

## Paso 1: El punto de quiebre demográfico nacional

> **English Summary:** *Ecuador records a major demographic shift with 35.26 seniors per 100 children nationwide.*

Los resultados del Censo 2022 registran una transformación demográfica profunda en el país. Por cada cien menores de quince años habitan treinta y cinco adultos mayores en el territorio nacional. La base de la pirámide poblacional se reduce en comparación con censos anteriores, reflejando una reducción en los nacimientos y un incremento sostenido de la población de sesenta y cinco años y más.

- **Cifra clave:** 35,26 adultos mayores por cada 100 niños (1.520.590 personas de 65+ frente a 4.312.989 de 0 a 14 años sobre 16.938.986 habitantes censados).
- **Fuente oficial:** INEC, Censo de Población y Vivienda 2022 (Boletín Nacional) / counts: nacion/data.parquet

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT population,
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

## Paso 2: La Amazonía: la estructura poblacional más joven

> **English Summary:** *In the Amazonian canton of Taisha, only 5.15 seniors live per 100 children.*

En la región amazónica sur, la estructura por edades muestra un patrón diferente al promedio del país. En el cantón Taisha, perteneciente a Morona Santiago, el 48,6% de los habitantes son menores de quince años y el 2,5% tiene sesenta y cinco años o más. El índice de envejecimiento es de cinco adultos mayores por cada cien niños, el menor registrado a nivel cantonal.

- **Cifra clave:** Índice de envejecimiento de 5,15 en el cantón Taisha (12.981 niños frente a 669 adultos mayores en 26.700 habitantes).
- **Fuente oficial:** INEC, Censo 2022 / counts: canton/data.parquet (unit_key='1409')

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT unit_key, population,
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
    "1409"
  ]
}
```

---

## Paso 3: La Sierra austral: cantones con más adultos mayores que niños

> **English Summary:** *In southern Andean cantons such as Olmedo and Sevilla de Oro, seniors outnumber children.*

En contraste con la Amazonía, varios cantones de la Sierra sur registran más adultos mayores que menores de quince años. En Olmedo y Chaguarpamba, en Loja, y en Sevilla de Oro, en Azuay, el índice de envejecimiento supera cien. En estas jurisdicciones, el grupo de sesenta y cinco años y más representa más del veinte por ciento de la población cantonal total censada.

- **Cifra clave:** Índice de envejecimiento de 103,98 en Olmedo (Loja), 103,16 en Sevilla de Oro (Azuay) y 102,80 en Chaguarpamba (Loja).
- **Fuente oficial:** INEC, Censo 2022 / counts: canton/data.parquet (unit_keys: '1115', '0112', '1116')

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT unit_key, population,
       (age_00_04_m::BIGINT + age_00_04_f::BIGINT + age_05_09_m::BIGINT + age_05_09_f::BIGINT + age_10_14_m::BIGINT + age_10_14_f::BIGINT) AS pop_0_14,
       (age_65_69_m::BIGINT + age_65_69_f::BIGINT + age_70_74_m::BIGINT + age_70_74_f::BIGINT + age_75_79_m::BIGINT + age_75_79_f::BIGINT + 
        age_80_84_m::BIGINT + age_80_84_f::BIGINT + age_85_89_m::BIGINT + age_85_89_f::BIGINT + age_90_94_m::BIGINT + age_90_94_f::BIGINT + 
        age_95_99_m::BIGINT + age_95_99_f::BIGINT + age_100_120_m::BIGINT + age_100_120_f::BIGINT) AS pop_65_plus,
       pop_65_plus * 100.0 / NULLIF(pop_0_14, 0) AS aging_index
FROM read_parquet('data/counts/v1b1/canton/data.parquet')
WHERE unit_key IN ('1115', '0112', '1116')
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

## Paso 4: Palmira y San Juan: la escala parroquial rural

> **English Summary:** *Rural parishes like Palmira (226.22) and San Juan (177.99) show the highest aging ratios.*

Al analizar la división parroquial, las diferencias se amplían notablemente. En la parroquia rural Palmira, perteneciente al cantón Guamote en Chimborazo, el índice de envejecimiento alcanza 226,22, con 1.070 adultos mayores y 473 niños. En la parroquia rural San Juan, del cantón Riobamba, el indicador se sitúa en 177,99, duplicando el promedio provincial de personas mayores por cada cien infantes.

- **Cifra clave:** 226,22 adultos mayores por cada 100 niños en Palmira (Chimborazo) y 177,99 en San Juan (Chimborazo).
- **Fuente oficial:** INEC, Censo 2022 / counts: parroquia/data.parquet (unit_keys: '060354', '060154')

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT unit_key, canton_key, population,
       (age_00_04_m::BIGINT + age_00_04_f::BIGINT + age_05_09_m::BIGINT + age_05_09_f::BIGINT + age_10_14_m::BIGINT + age_10_14_f::BIGINT) AS pop_0_14,
       (age_65_69_m::BIGINT + age_65_69_f::BIGINT + age_70_74_m::BIGINT + age_70_74_f::BIGINT + age_75_79_m::BIGINT + age_75_79_f::BIGINT + 
        age_80_84_m::BIGINT + age_80_84_f::BIGINT + age_85_89_m::BIGINT + age_85_89_f::BIGINT + age_90_94_m::BIGINT + age_90_94_f::BIGINT + 
        age_95_99_m::BIGINT + age_95_99_f::BIGINT + age_100_120_m::BIGINT + age_100_120_f::BIGINT) AS pop_65_plus,
       pop_65_plus * 100.0 / NULLIF(pop_0_14, 0) AS aging_index
FROM read_parquet('data/counts/v1b1/parroquia/data.parquet')
WHERE unit_key IN ('060354', '060154');
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
  "filtro": "canton_key IN ('0601', '0603')",
  "capa_extra": "choropleth",
  "resaltados": [
    "060354",
    "060154"
  ]
}
```

---

## Paso 5: El giro urbano: sectores consolidados de Iñaquito

> **English Summary:** *Urban sectors in Quito's Iñaquito exceed 135 seniors per 100 children, rivaling rural aging.*

A nivel de sector censal, el envejecimiento elevado no se restringe a zonas rurales andinas. En sectores censales urbanos de Iñaquito, en el cantón Quito, el índice de envejecimiento supera 135 adultos mayores por cada cien niños, con más del veinte por ciento de personas mayores residiendo solas. Estos valores superan con amplitud a los de cantones rurales enteros del país.

> **Hipótesis:** La concentración de adultos mayores en sectores urbanos consolidados suele asociarse a la permanencia residencial de propietarios originales y a costos de suelo que orientan a familias jóvenes hacia periferias (el censo no mide precios inmobiliarios ni historial de transacciones). Fuente: [BID, Vivienda en ALC](https://publications.iadb.org/es/publicacion/17449/vivienda-para-el-desarrollo-en-america-latina-y-el-caribe) (el censo no lo mide).

- **Cifra clave:** Índice de envejecimiento superior a 135 en sectores censales de Iñaquito (Quito) y 21,3% de soledad en 65+.
- **Fuente oficial:** INEC / counts: sector/17.parquet y cross_counts_v1b2 (solitary_65)

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT c.unit_key, c.population,
       c.pop_65_plus * 100.0 / NULLIF(c.pop_0_14, 0) AS aging_index,
       x.solitary_65 * 100.0 / NULLIF(x.all_65, 0) AS pct_solitary_65
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
  "capa_extra": "choropleth",
  "resaltados": [
    "170150004001",
    "170150005002"
  ]
}
```

---

## Paso 6: La disparidad intra-cantonal: Iñaquito frente a Calderón

> **English Summary:** *Within Quito, urban sectors contrast sharply with the younger demographic structure of parish Calderón.*

Dentro del cantón Quito, la comparación entre parroquias evidencia contrastes notorios en una misma demarcación. Mientras los sectores consolidados de Iñaquito exhiben una estructura marcadamente envejecida, la parroquia rural Calderón registra un índice de envejecimiento de 35,88, con 9.884 menores de quince años y 3.546 personas mayores. El cantón abarca simultáneamente etapas divergentes de la transición por edad.

- **Cifra clave:** Índice de envejecimiento de 35,88 en la parroquia Calderón (unit_key='170152') frente a más de 135 en sectores de Iñaquito.
- **Fuente oficial:** INEC, Censo 2022 / counts: parroquia/data.parquet (unit_key='170152')

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT unit_key, population,
       (age_00_04_m::BIGINT + age_00_04_f::BIGINT + age_05_09_m::BIGINT + age_05_09_f::BIGINT + age_10_14_m::BIGINT + age_10_14_f::BIGINT) AS pop_0_14,
       (age_65_69_m::BIGINT + age_65_69_f::BIGINT + age_70_74_m::BIGINT + age_70_74_f::BIGINT + age_75_79_m::BIGINT + age_75_79_f::BIGINT + 
        age_80_84_m::BIGINT + age_80_84_f::BIGINT + age_85_89_m::BIGINT + age_85_89_f::BIGINT + age_90_94_m::BIGINT + age_90_94_f::BIGINT + 
        age_95_99_m::BIGINT + age_95_99_f::BIGINT + age_100_120_m::BIGINT + age_100_120_f::BIGINT) AS pop_65_plus,
       pop_65_plus * 100.0 / NULLIF(pop_0_14, 0) AS aging_index
FROM read_parquet('data/counts/v1b1/parroquia/data.parquet')
WHERE unit_key = '170152';
```

### Estado del Mapa (WebGIS Spec):
```json
{
  "nivel": "parroquia",
  "centro": [
    -78.44,
    -0.1
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

## Paso 7: ¿Qué estructura de edad presenta su cantón?

> **English Summary:** *Demographic aging varies greatly: explore your canton on the interactive map to compare local patterns.*

La distribución por edades condiciona la demanda de infraestructura escolar, servicios de salud y sistemas de cuidados en cada circunscripción del país. Los datos censales demuestran que las políticas públicas no pueden asumir homogeneidad territorial. ¿Cuál es el índice de envejecimiento en su cantón y cómo se compara con los extremos amazónicos y andinos?

- **Cifra clave:** Rango cantonal nacional entre 5,15 (Taisha) y 103,98 (Olmedo) adultos mayores por cada 100 menores de 15 años.
- **Fuente oficial:** CPV 2022 INEC / indicators.yaml (id: aging_index)

### Consulta SQL Reproducible (DuckDB):
```sql
SELECT min(aging_index) AS min_cantonal,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY aging_index) AS mediana_cantonal,
       max(aging_index) AS max_cantonal
FROM (
    SELECT (age_65_69_m::BIGINT + age_65_69_f::BIGINT + age_70_74_m::BIGINT + age_70_74_f::BIGINT + age_75_79_m::BIGINT + age_75_79_f::BIGINT + 
            age_80_84_m::BIGINT + age_80_84_f::BIGINT + age_85_89_m::BIGINT + age_85_89_f::BIGINT + age_90_94_m::BIGINT + age_90_94_f::BIGINT + 
            age_95_99_m::BIGINT + age_95_99_f::BIGINT + age_100_120_m::BIGINT + age_100_120_f::BIGINT) * 100.0 / 
           NULLIF(age_00_04_m::BIGINT + age_00_04_f::BIGINT + age_05_09_m::BIGINT + age_05_09_f::BIGINT + age_10_14_m::BIGINT + age_10_14_f::BIGINT, 0) AS aging_index
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

