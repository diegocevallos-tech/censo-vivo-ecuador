# Los que se fueron

**ID de la Historia:** `02_los_que_se_fueron`  
**Descripción:** Geografía de la emigración internacional reciente, asimetría de género en edades activas y concentración en el Austro.

---

## Paso 1: El registro censal de la ausencia: 96.825 emigrantes

**English Title:** *The Census Record of Absence: 96,825 Emigrants*

El Censo 2022 registró 96.825 personas que emigraron del Ecuador en el periodo intercensal reciente, reportadas de forma directa por los hogares que permanecen en el país. Esta cifra censal refleja la magnitud de las familias con ausencias internacionales y constituye el punto de partida para examinar la distribución territorial de los hogares con migrantes.

**Resumen en inglés:** 96,825 emigrants were reported by remaining resident households nationwide in CPV 2022.  

**Cifra clave:** `96825 personas` (Fuente: *INEC CPV 2022, nacion/data.parquet (sum(emigrants))*)

```sql
SELECT sum(emigrants) AS total_emigrants FROM 'data/derived/counts/v1b1/nacion/data.parquet';
```

```json
{
  "nivel": "nacion",
  "centro": [
    -78.1834,
    -1.8312
  ],
  "zoom": 6.2,
  "indicador": "emigrant_households",
  "filtro": null,
  "capa_extra": null,
  "resaltados": [
    "EC"
  ]
}
```

---

## Paso 2: El epicentro del Austro: Cañar y Azuay

**English Title:** *The Epicenter in the Austro: Cañar and Azuay*

La distribución espacial de la emigración muestra una concentración extrema en el Austro ecuatoriano. La provincia de Cañar encabeza la tasa nacional con 38,76 emigrantes por cada mil habitantes (8.820 emigrantes en 227.578 personas). Azuay le sigue de cerca con 28,13 por mil (22.550 emigrantes en 801.609 habitantes). Ambas provincias concentran casi un tercio del total de ausencias registradas.

**Resumen en inglés:** Cañar leads emigration intensity with 38.76 per thousand inhabitants, followed by Azuay with 28.13.  

**Cifra clave:** `38.76 emigrantes por mil habitantes` (Fuente: *INEC CPV 2022, provincia/data.parquet (unit_keys: '03', '01')*)

```sql
SELECT unit_key, population, emigrants, emigrants * 1000.0 / population AS emigrant_rate_per_thousand FROM 'data/derived/counts/v1b1/provincia/data.parquet' WHERE unit_key IN ('03', '01');
```

```json
{
  "nivel": "provincia",
  "centro": [
    -78.95,
    -2.75
  ],
  "zoom": 8.2,
  "indicador": "emigrant_households",
  "filtro": "unit_key IN ('03', '01')",
  "capa_extra": null,
  "resaltados": [
    "03",
    "01"
  ]
}
```

---

## Paso 3: Chunchi: el récord cantonal en la Sierra centro-sur

**English Title:** *Chunchi: Cantonal Record in Central-Southern Sierra*

A nivel cantonal, la intensidad migratoria alcanza su punto cúspide en Chunchi (Chimborazo). Con una población de 10.635 habitantes, 775 personas fueron reportadas como emigrantes en el censo, lo que representa el 7,29% de su población total. En este cantón andino, más de siete de cada cien residentes tienen familiares inmediatos residiendo en el exterior.

**Resumen en inglés:** Chunchi in Chimborazo registers the peak cantonal emigration rate at 7.29% of its total population (775 emigrants).  

**Cifra clave:** `7.29 % de la población cantonal` (Fuente: *INEC CPV 2022, canton/data.parquet (unit_key='0605')*)

```sql
SELECT unit_key, population, emigrants, emigrants * 100.0 / population AS pct_emigrants FROM 'data/derived/counts/v1b1/canton/data.parquet' WHERE unit_key = '0605';
```

```json
{
  "nivel": "canton",
  "centro": [
    -78.91,
    -2.29
  ],
  "zoom": 10.2,
  "indicador": "emigrant_households",
  "filtro": "unit_key = '0605'",
  "capa_extra": null,
  "resaltados": [
    "0605"
  ]
}
```

---

## Paso 4: Perfil de salida: edad, género y destinos principales

**English Title:** *Departure Profile: Age, Gender, and Key Destinations*

La emigración censal captura la salida de población en edades activas hacia destinos tradicionales. En cantones como Santa Isabel y Biblián, la información censal de salida detalla los países de destino y los tramos de edad. La disponibilidad de estos agregados cruzados permite desagregar los flujos por cohortes quinquenales en los tabulados especializados.

**Resumen en inglés:** Detailed cross-tabulation of emigrants by age of departure, sex, and destination country in Santa Isabel and Biblián.  

**Cifra clave:** `[PENDIENTE: agregado de Emigración por cantón × sexo × edad de salida × país de destino] personas emigrantes` (Fuente: *INEC CPV 2022, Cuestionario Censal Sección 4 (E01-E04)*)

```sql
-- [PENDIENTE: agregado de Emigración por cantón × sexo × edad de salida × país de destino]
SELECT canton_key, count(*) FROM emigracion_microdatos GROUP BY canton_key;
```

```json
{
  "nivel": "canton",
  "centro": [
    -79.15,
    -3.05
  ],
  "zoom": 9.2,
  "indicador": "emigrant_households",
  "filtro": "unit_key IN ('0109', '0303')",
  "capa_extra": "arcos_migratorios",
  "resaltados": [
    "0109",
    "0303"
  ]
}
```

---

## Paso 5: El giro demográfico: la asimetría de género en edades productivas

**English Title:** *The Demographic Twist: Gender Asymmetry in Productive Ages*

La huella más nítida de la emigración se observa en la estructura etaria local. En el cantón Santa Isabel (Azuay), la razón de masculinidad para el grupo de 20 a 39 años desciende a 69,99 varones por cada 100 mujeres (2.628 hombres frente a 3.755 mujeres). En Biblián se ubica en 76,07, confirmando un déficit pronunciado de población masculina en edad laboral.

> **Hipótesis:** La concentración territorial de la emigración coincide con la mayor presencia de hogares beneficiarios y cobertura de entidades financieras pagadoras de remesas en las provincias del Austro (el censo no lo mide). [Banco Central del Ecuador (BCE), 2024, pág. 8](https://contenido.bce.fin.ec/documentos/Estadisticas/SectorExterno/BalanzaPagos/Remesas/ere2023IV.pdf).
>
> *Cita textual:* «Esta participación se atribuye a la presencia de un considerable número de hogares beneficiarios en estas áreas geográficas, así como a la disponibilidad de entidades financieras y empresas remesadoras que ofrecen servicios de pago de remesas en dichas localidades contribuyó a la consolidación de estas provincias como centros clave en la recepción de remesas, con base a la investigación de campo efectuada por el Banco Central del Ecuador.»

**Resumen en inglés:** In Santa Isabel (Azuay), sex ratio for ages 20-39 drops to 69.99 males per 100 females (2,628 vs 3,755).  

**Cifra clave:** `69.99 hombres por cada 100 mujeres` (Fuente: *INEC CPV 2022, canton/data.parquet (unit_keys: '0109', '0303')*)

```sql
SELECT unit_key, (age_20_24_m + age_25_29_m + age_30_34_m + age_35_39_m) * 100.0 / (age_20_24_f + age_25_29_f + age_30_34_f + age_35_39_f) AS male_ratio_20_39 FROM 'data/derived/counts/v1b1/canton/data.parquet' WHERE unit_key IN ('0109', '0303');
```

```json
{
  "nivel": "canton",
  "centro": [
    -79.31,
    -3.27
  ],
  "zoom": 10.0,
  "indicador": "male_ratio",
  "filtro": "unit_key IN ('0109', '0303')",
  "capa_extra": null,
  "resaltados": [
    "0109",
    "0303"
  ]
}
```

---

## Paso 6: La frontera migratoria amazónica: Morona Santiago

**English Title:** *The Amazonian Migration Frontier: Morona Santiago*

Aunque la migración internacional se asocia comúnmente a la Sierra centro-sur, los datos del Censo 2022 revelan que la Amazonía sur se ha integrado activamente a este proceso. Morona Santiago registra 16,94 emigrantes por cada mil habitantes (3.261 personas emigrantes en 192.508 habitantes), superando la tasa provincial de varias provincias andinas y costeñas.

**Resumen en inglés:** Morona Santiago shows an emerging migration rate of 16.94 emigrants per thousand inhabitants.  

**Cifra clave:** `16.94 emigrantes por mil habitantes` (Fuente: *INEC CPV 2022, provincia/data.parquet (unit_key='14')*)

```sql
SELECT unit_key, population, emigrants, emigrants * 1000.0 / population AS emigrant_rate_per_thousand FROM 'data/derived/counts/v1b1/provincia/data.parquet' WHERE unit_key = '14';
```

```json
{
  "nivel": "provincia",
  "centro": [
    -77.8,
    -2.8
  ],
  "zoom": 7.8,
  "indicador": "emigrant_households",
  "filtro": "unit_key = '14'",
  "capa_extra": null,
  "resaltados": [
    "14"
  ]
}
```

---

## Paso 7: Migración interna: los polos de atracción

**English Title:** *Internal Migration: Growth Poles and Counter-flows*

Frente a los cantones expulsores de población internacional, cantones receptores en zonas metropolitanas y periurbanas han experimentado un crecimiento notable. Cantones como Daule y Samborondón en Guayas, o Rumiñahui en Pichincha, absorben flujos residenciales significativos. En Daule, 34.664 personas reportaron en el censo haber residido en otro cantón cinco años antes, transformando la dinámica urbana regional.

**Resumen en inglés:** Peri-urban cantons like Daule absorbed large internal migration flows (34,664 people from other cantons).  

**Cifra clave:** `34664 personas` (Fuente: *INEC CPV 2022, cross_counts Fase 1B-2 (canton_key='0906')*)

```sql
SELECT canton_key, sum(n) as internal_migrants FROM cross_counts_v1b2 WHERE variable = 'residence_5yr_prior' AND canton_key = '0906' GROUP BY canton_key;
```

```json
{
  "nivel": "canton",
  "centro": [
    -79.98,
    -1.98
  ],
  "zoom": 10.0,
  "indicador": "internal_migrants",
  "filtro": "unit_key = '0906'",
  "capa_extra": null,
  "resaltados": [
    "0906"
  ]
}
```

---

## Paso 8: ¿Qué queda en las comunidades de origen?

**English Title:** *What Remains in Communities of Origin?*

La salida de decenas de miles de personas en edad productiva deja una impronta indeleble en el tejido productivo y social de los cantones de origen. Con pirámides sesgadas hacia mujeres, niños y ancianos, ¿cómo se reconfiguran las economías locales del Austro y qué desafíos enfrentan los territorios que pierden a su fuerza laboral?

**Resumen en inglés:** Reflections on demographic hollows, eldercare burdens, and sustainable development in high-emigration cantons.  

**Cifra clave:** `N/A reflexión analítica` (Fuente: *Censo Ecuador 2022*)

```json
{
  "nivel": "canton",
  "centro": [
    -78.1834,
    -1.8312
  ],
  "zoom": 6.8,
  "indicador": "emigrant_households",
  "filtro": null,
  "capa_extra": null,
  "resaltados": []
}
```

---
