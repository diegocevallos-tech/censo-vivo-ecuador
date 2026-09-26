# El Ecuador que envejece

**ID de la Historia:** `01_ecuador_envejece`  
**Descripción:** Evolución demográfica, disparidad territorial del envejecimiento e inversión de pirámides poblacionales.

---

## Paso 1: El pulso del país: 35 adultos mayores por cada 100 niños

**English Title:** *The National Pulse: 35 Older Adults Per 100 Children*

El Censo Ecuador 2022 contabilizó 16.938.986 habitantes. A nivel nacional, el índice de envejecimiento se sitúa en 35,26 adultos mayores de 65 años por cada 100 menores de 15 años. El país cuenta con 1.520.590 personas de 65 años y más, frente a 4.312.989 niños y adolescentes de 0 a 14 años, reflejando una transición demográfica en marcha.

**Resumen en inglés:** National aging index is 35.26 older adults per 100 children (1,520,590 older adults vs 4,312,989 children).  

**Cifra clave:** `35.26 mayores 65+ por 100 niños 0-14` (Fuente: *INEC CPV 2022, agregados Fase 1B-1 (nacion/data.parquet)*)

```sql
SELECT sum(pop_65_plus) * 100.0 / sum(pop_0_14) AS national_aging_index, sum(population) AS total_pop, sum(pop_65_plus) AS seniors, sum(pop_0_14) AS kids FROM 'data/derived/counts/v1b1/nacion/data.parquet';
```

```json
{
  "nivel": "nacion",
  "centro": [
    -78.1834,
    -1.8312
  ],
  "zoom": 6.2,
  "indicador": "aging_index",
  "filtro": null,
  "capa_extra": null,
  "resaltados": [
    "EC"
  ]
}
```

---

## Paso 2: La juventud amazónica: Taisha y la base ancha

**English Title:** *Amazonian Youth: Taisha and the Broad Base*

En la Amazonía profunda, la estructura poblacional mantiene una base predominantemente infantil. En el cantón Taisha, en Morona Santiago, el índice de envejecimiento apenas llega a 5,15 adultos mayores por cada 100 niños. Con 26.700 habitantes censados, Taisha registra 12.981 menores de 15 años y solamente 669 adultos mayores, configurándose como el cantón más joven del Ecuador.

**Resumen en inglés:** Taisha in Morona Santiago has the lowest aging index (5.15), with 12,981 children and only 669 older adults.  

**Cifra clave:** `5.15 mayores 65+ por 100 niños 0-14` (Fuente: *INEC CPV 2022, canton/data.parquet (unit_key='1409')*)

```sql
SELECT unit_key, population, pop_65_plus * 100.0 / pop_0_14 AS aging_index FROM 'data/derived/counts/v1b1/canton/data.parquet' WHERE unit_key = '1409';
```

```json
{
  "nivel": "canton",
  "centro": [
    -77.5,
    -2.38
  ],
  "zoom": 9.0,
  "indicador": "aging_index",
  "filtro": "unit_key = '1409'",
  "capa_extra": null,
  "resaltados": [
    "1409"
  ]
}
```

---

## Paso 3: Los cantones donde los mayores superan a los niños

**English Title:** *Cantons Where the Elderly Outnumber Children*

En el extremo opuesto del espectro demográfico, tres cantones de la Sierra sur han invertido su estructura poblacional: Olmedo en Loja con un índice de 103,98, Sevilla de Oro en Azuay con 103,16 y Chaguarpamba en Loja con 102,80. En estas localidades, por cada 100 menores de 15 años habitan más de 102 adultos mayores, perfilando comunidades demográficamente envejecidas.

**Resumen en inglés:** In Olmedo (103.98), Sevilla de Oro (103.16), and Chaguarpamba (102.80), older adults exceed children.  

**Cifra clave:** `103.98 mayores 65+ por 100 niños 0-14` (Fuente: *INEC CPV 2022, canton/data.parquet (unit_keys: '1115', '0112', '1116')*)

```sql
SELECT unit_key, population, pop_65_plus * 100.0 / pop_0_14 AS aging_index FROM 'data/derived/counts/v1b1/canton/data.parquet' WHERE unit_key IN ('1115', '0112', '1116') ORDER BY aging_index DESC;
```

```json
{
  "nivel": "canton",
  "centro": [
    -79.4,
    -3.9
  ],
  "zoom": 8.5,
  "indicador": "aging_index",
  "filtro": "aging_index >= 100",
  "capa_extra": null,
  "resaltados": [
    "1115",
    "0112",
    "1116"
  ]
}
```

---

## Paso 4: Las parroquias rurales extremas: Palmira y San Juan

**English Title:** *Extreme Rural Parishes: Palmira and San Juan*

A escala parroquial, las brechas territoriales se profundizan notablemente. En Chimborazo, la parroquia rural Palmira alcanza un índice de 226,22 personas mayores por cada 100 menores (1.070 mayores frente a 473 niños). En San Juan, la proporción se sitúa en 177,99 (833 mayores y 468 niños). En estos territorios rurales, la presencia de adultos mayores duplica ampliamente al contingente infantil.

> **Hipótesis:** La marcada concentración de adultos mayores en áreas rurales obedece principalmente a la selectividad de la migración de personas en edad productiva hacia centros urbanos, que reduce la fecundidad rural y retiene a la población mayor. (el censo no lo mide). [Comisión Económica para América Latina y el Caribe (CEPAL), 2022, pág. 33](https://repositorio.cepal.org/server/api/core/bitstreams/e345daf3-2e35-4569-a2f8-4e22db139a02/content).
>
> *Cita textual:* «Si bien las zonas urbanas, en particular las grandes ciudades, son las áreas donde este proceso está más avanzado, esta tendencia no se observa en todos los países debido, principalmente, al proceso de migración rural selectiva hacia las zonas urbanas, pues la población en edad de trabajar se desplaza con mayor frecuencia, dejando a las personas mayores en las zonas rurales.»

**Resumen en inglés:** Rural parishes in Chimborazo exhibit acute aging: Palmira reaches 226.22 and San Juan 177.99.  

**Cifra clave:** `226.22 mayores 65+ por 100 niños 0-14` (Fuente: *INEC CPV 2022, parroquia/data.parquet (unit_keys: '060354', '060154')*)

```sql
SELECT unit_key, pop_65_plus * 100.0 / pop_0_14 AS aging_index FROM 'data/derived/counts/v1b1/parroquia/data.parquet' WHERE unit_key IN ('060354', '060154');
```

```json
{
  "nivel": "parroquia",
  "centro": [
    -78.75,
    -1.85
  ],
  "zoom": 10.5,
  "indicador": "aging_index",
  "filtro": "unit_key IN ('060354', '060154')",
  "capa_extra": null,
  "resaltados": [
    "060354",
    "060154"
  ]
}
```

---

## Paso 5: El giro urbano: el hipercentro norte frente a Calderón

**English Title:** *The Urban Twist: North Center vs Calderón*

Dentro de Quito conviven realidades demográficas opuestas. Mientras la parroquia rural Calderón registra un índice de 30,11 (17.578 mayores frente a 58.379 niños), el hipercentro norte (La Carolina y El Batán) muestra un marcado envejecimiento. La cifra oficial de la parroquia urbana Iñaquito permanece [PENDIENTE: índice de Iñaquito con la capa de parroquias urbanas del visor], al registrar el censo la urbe como cabecera única.

**Resumen en inglés:** Within Quito, rural parish Calderón registers a young aging index of 30.11 (17,578 seniors vs 58,379 children), contrasting with the aged north-central core. Urban parish Iñaquito is pending the viewer's non-census municipal layer.  

**Cifra clave:** `[PENDIENTE: índice de Iñaquito con la capa de parroquias urbanas del visor] mayores 65+ por 100 niños 0-14` (Fuente: *INEC CPV 2022, parroquia/data.parquet (unit_key='170155') / [PENDIENTE: capa de parroquias urbanas del visor]*)

```sql
-- Calderón (parroquia censal oficial 170155)
SELECT '170155' as unit_key, 'Calderon' as name, population, pop_65_plus, pop_0_14, pop_65_plus * 100.0 / pop_0_14 AS aging_index FROM 'data/derived/counts/v1b1/parroquia/data.parquet' WHERE unit_key = '170155';
-- [PENDIENTE: índice de Iñaquito con la capa de parroquias urbanas del visor]
```

```json
{
  "nivel": "parroquia",
  "centro": [
    -78.46,
    -0.14
  ],
  "zoom": 11.5,
  "indicador": "aging_index",
  "filtro": "canton_key = '1701'",
  "capa_extra": null,
  "resaltados": [
    "170150",
    "170155"
  ]
}
```

---

## Paso 6: De sector a sector: la polarización entre el centro y la periferia

**English Title:** *Sector by Sector: Polarization Between Center and Periphery*

Al comparar sectores con muestra suficiente según el umbral censal, la polarización es contundente. El percentil 90 del hipercentro norte alcanza 217,00 adultos mayores por cada 100 niños, mientras el percentil 10 de Calderón desciende a 14,83, una brecha casi quince veces superior. En el extremo, el sector 170150257003 en La Carolina registra 127 mayores y 34 niños (373,53), frente a periferias con 9 mayores y 179 niños (5,03).

**Resumen en inglés:** Evaluating robust sectors (pop_0_14 >= 30), the 90th percentile of north-central sectors reaches 217.00 seniors per 100 kids, whereas Calderón's 10th percentile drops to 14.83.  

**Cifra clave:** `217.0 mayores 65+ por 100 niños 0-14` (Fuente: *INEC CPV 2022, sector/17.parquet (sectores con pop_0_14 >= 30)*)

```sql
SELECT unit_key, population, pop_65_plus, pop_0_14, pop_65_plus * 100.0 / pop_0_14 AS aging_index FROM 'data/derived/counts/v1b1/sector/17.parquet' WHERE unit_key IN ('170150257003', '170155025002');
-- Umbral pop_0_14 >= 30: p90 hipercentro norte (La Carolina/Batán) = 217.00 | p10 Calderón = 14.83
```

```json
{
  "nivel": "sector",
  "centro": [
    -78.47,
    -0.15
  ],
  "zoom": 12.5,
  "indicador": "aging_index",
  "filtro": "canton_key = '1701'",
  "capa_extra": null,
  "resaltados": [
    "170150257003",
    "170155025002"
  ]
}
```

---

## Paso 7: ¿Hacia dónde va la pirámide poblacional ecuatoriana?

**English Title:** *Where Is Ecuador's Population Pyramid Heading?*

La coexistencia de sectores urbanos envejecidos junto a periferias jóvenes y parroquias rurales sin reemplazo generacional plantea retos de infraestructura y cuidados. Cuando un país envejece de manera desigual en su territorio, ¿cómo deben reasignarse los servicios de salud, guarderías y espacios públicos para responder a poblaciones con necesidades diametralmente opuestas?

**Resumen en inglés:** Territorial divergence in aging demands tailored public policies for health, education, and urban infrastructure.  

**Cifra clave:** `N/A reflexión analítica` (Fuente: *Censo Ecuador 2022*)

```json
{
  "nivel": "canton",
  "centro": [
    -78.1834,
    -1.8312
  ],
  "zoom": 6.8,
  "indicador": "aging_index",
  "filtro": null,
  "capa_extra": null,
  "resaltados": []
}
```

---
