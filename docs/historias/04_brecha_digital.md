# La brecha digital

**ID de la Historia:** `04_brecha_digital`  
**Descripción:** Disparidades de acceso a internet fijo domiciliario vs telefonía celular en hogares ecuatorianos.

---

## Paso 1: La brecha de entrada: celular vs internet fijo en los hogares

**English Title:** *The Entry Gap: Mobile Phone vs Fixed Internet in Households*

En el Censo 2022, sobre un total de 5.188.827 hogares clasificados, el 86,98% (4.513.446 hogares) reportó contar con servicio de teléfono celular (H1002=1). En contraste, el servicio de internet fijo domiciliario (H1004=1) solo alcanza al 60,89% (3.159.588 hogares). Esta diferencia de 26,09 puntos porcentuales en el mismo universo de hogares evidencia la brecha estructural de acceso.

**Resumen en inglés:** 86.98% of Ecuadorian households report cell phone service, but only 60.89% have fixed internet (a 26.09 percentage point gap).  

**Cifra clave:** `26.09 puntos porcentuales de brecha en hogares` (Fuente: *INEC CPV 2022, categories/nacion/data.parquet (H1002 vs H1004)*)

```sql
SELECT sum(n) FILTER (WHERE category='1') * 100.0 / sum(n) AS pct FROM 'data/derived/counts/v1b1/categories/nacion/data.parquet' WHERE variable IN ('H1002', 'H1004') GROUP BY variable;
```

```json
{
  "nivel": "nacion",
  "centro": [
    -78.1834,
    -1.8312
  ],
  "zoom": 6.2,
  "indicador": "fixed_internet",
  "filtro": null,
  "capa_extra": null,
  "resaltados": [
    "EC"
  ]
}
```

---

## Paso 2: Los cantones hiperconectados: Rumiñahui y Cuenca

**English Title:** *Hyperconnected Cantons: Rumiñahui and Cuenca*

La cobertura de internet fijo en hogares se concentra marcadamente en cantones con alta infraestructura urbana. Rumiñahui, en Pichincha, lidera el país con un 78,24% de hogares con internet fijo domiciliario. Le sigue Cuenca con 75,30%, Quito con 74,80% y Samborondón con 74,10%, configurando los principales núcleos de conectividad residencial del Ecuador.

**Resumen en inglés:** Rumiñahui (78.24%) and Cuenca (75.30%) exhibit Ecuador's highest household fixed internet penetration rates.  

**Cifra clave:** `78.24 % de hogares con internet fijo` (Fuente: *INEC CPV 2022, categories/canton/17.parquet (unit_key='1705')*)

```sql
SELECT canton_key, sum(n) FILTER (WHERE category='1') * 100.0 / sum(n) AS pct_fixed FROM 'data/derived/counts/v1b1/categories/canton/*.parquet' WHERE variable='H1004' AND canton_key IN ('1705', '0101', '1701', '0916') GROUP BY canton_key ORDER BY pct_fixed DESC;
```

```json
{
  "nivel": "canton",
  "centro": [
    -78.44,
    -0.32
  ],
  "zoom": 10.0,
  "indicador": "fixed_internet",
  "filtro": "unit_key IN ('1705', '0101', '1701', '0916')",
  "capa_extra": null,
  "resaltados": [
    "1705",
    "0101"
  ]
}
```

---

## Paso 3: El desierto digital: Taisha y Paján

**English Title:** *The Digital Desert: Taisha and Paján*

En el extremo opuesto, el acceso a internet fijo domiciliario es prácticamente residual en cantones rurales y amazónicos. En Taisha, únicamente el 14,82% de los hogares reporta contar con servicio de internet fijo. En cantones costeros como Paján (Manabí), la tasa es de 22,64%, evidenciando amplias zonas del país al margen de las redes cableadas residenciales.

**Resumen en inglés:** Fixed internet penetration drops to 14.82% of households in Taisha and 22.64% in Paján (Manabí).  

**Cifra clave:** `14.82 % de hogares con internet fijo` (Fuente: *INEC CPV 2022, categories/canton/14.parquet (unit_key='1409')*)

```sql
SELECT canton_key, sum(n) FILTER (WHERE category='1') * 100.0 / sum(n) AS pct_fixed FROM 'data/derived/counts/v1b1/categories/canton/*.parquet' WHERE variable='H1004' AND canton_key IN ('1409', '1310') GROUP BY canton_key;
```

```json
{
  "nivel": "canton",
  "centro": [
    -77.5,
    -2.38
  ],
  "zoom": 8.5,
  "indicador": "fixed_internet",
  "filtro": "pct_fixed <= 25.0",
  "capa_extra": null,
  "resaltados": [
    "1409",
    "1310"
  ]
}
```

---

## Paso 4: El giro de los dispositivos: celular en casi todos, fijo en pocos

**English Title:** *The Device Twist: Cell Phones Everywhere, Fixed Internet Scarce*

Al contrastar los dos servicios en la misma unidad de análisis, surge una brecha contraintuitiva. En el cantón Paján, el 80,48% de los hogares tiene servicio celular, pero solo el 22,64% accede a internet fijo: una brecha de 57,84 puntos porcentuales. En El Empalme, la brecha alcanza 51,71 puntos (87,74% celular frente a 36,02% fijo).

> **Hipótesis:** La disparidad entre la posesión de celular y el acceso a internet fijo domiciliario refleja barreras de costo de instalación de redes cableadas frente a la mayor asequibilidad de los paquetes móviles bajo modalidad prepago. (el censo no lo mide). [Agencia de Regulación y Control de las Telecomunicaciones (ARCOTEL), 2023, pág. 8](https://www.arcotel.gob.ec/wp-content/uploads/2023/12/Boletin-cierre-de-a%C3%B1o.pdf).
>
> *Cita textual:* «En diciembre del año 2022 en la modalidad pospago se registraron 3.743.849 y en la modalidad prepago 13.740.159 líneas activas.»

**Resumen en inglés:** In Paján, 80.48% of households have cell phones, but only 22.64% have fixed internet (a 57.84 percentage point gap).  

**Cifra clave:** `57.84 puntos porcentuales (% celular - % internet fijo)` (Fuente: *INEC CPV 2022, categories/canton/13.parquet (canton='1310')*)

```sql
SELECT canton_key, sum(n) FILTER (WHERE variable='H1002' AND category='1') * 100.0 / sum(n) FILTER (WHERE variable='H1002') AS pct_celular, sum(n) FILTER (WHERE variable='H1004' AND category='1') * 100.0 / sum(n) FILTER (WHERE variable='H1004') AS pct_fijo, (sum(n) FILTER (WHERE variable='H1002' AND category='1') * 100.0 / sum(n) FILTER (WHERE variable='H1002')) - (sum(n) FILTER (WHERE variable='H1004' AND category='1') * 100.0 / sum(n) FILTER (WHERE variable='H1004')) AS brecha_puntos FROM 'data/derived/counts/v1b1/categories/canton/13.parquet' WHERE canton_key = '1310' GROUP BY canton_key;
```

```json
{
  "nivel": "canton",
  "centro": [
    -80.43,
    -1.55
  ],
  "zoom": 9.5,
  "indicador": "fixed_internet",
  "filtro": "unit_key IN ('1310', '0908')",
  "capa_extra": "bivariate_gap",
  "resaltados": [
    "1310",
    "0908"
  ]
}
```

---

## Paso 5: La brecha intraurbana: Iñaquito frente a Pacto

**English Title:** *Intra-urban Divide: Iñaquito vs Pacto in Quito*

La desigualdad digital persiste incluso dentro del cantón Quito al comparar personas con personas. En la parroquia urbana Iñaquito, el 91,99% de la población de 5 años y más reporta usar internet. En la parroquia rural Pacto, perteneciente al mismo cantón, la proporción desciende al 50,54%. En una sola circunscripción cantonal conviven brechas territoriales de más de 40 puntos.

**Resumen en inglés:** Within Quito, internet usage reaches 91.99% of people in urban Iñaquito, but only 50.54% in rural Pacto.  

**Cifra clave:** `41.45 puntos porcentuales de diferencia en personas 5+ años` (Fuente: *INEC CPV 2022, cross_counts analítica 1B-2 (unit_keys: '170157', '170161')*)

```sql
SELECT parish_key, internet_person_5 * 100.0 / internet_response_5 AS pct_users FROM cross_counts_v1b2 WHERE parish_key IN ('170157', '170161');
```

```json
{
  "nivel": "parroquia",
  "centro": [
    -78.55,
    -0.05
  ],
  "zoom": 10.2,
  "indicador": "digital_exclusion",
  "filtro": "canton_key = '1701'",
  "capa_extra": null,
  "resaltados": [
    "170157",
    "170161"
  ]
}
```

---

## Paso 6: La brecha generacional: jóvenes urbanos vs adultos mayores rurales

**English Title:** *The Generational Gap: Urban Youth vs Rural Seniors*

Al cruzar grupos de edad censales, la desigualdad digital alcanza su mayor distancia. Mientras el 88,85% de jóvenes de 15 a 29 años en Quito utiliza internet de manera habitual, en cantones rurales como Eloy Alfaro (Esmeraldas), apenas el 8,72% de adultos mayores de 65 años declara utilizar la red, configurando una distancia de 80,13 puntos porcentuales.

**Resumen en inglés:** 88.85% of urban youth in Quito use the internet, compared to only 8.72% of rural seniors in Eloy Alfaro.  

**Cifra clave:** `80.13 puntos porcentuales (Quito jóvenes vs Eloy Alfaro mayores)` (Fuente: *INEC CPV 2022, cross_counts analítica 1B-2*)

```sql
SELECT (SELECT digital_youth_yes * 100.0 / digital_youth_n FROM cross_counts WHERE canton_key='1701') - (SELECT digital_senior_yes * 100.0 / digital_senior_n FROM cross_counts WHERE canton_key='0802') AS gap;
```

```json
{
  "nivel": "canton",
  "centro": [
    -78.5,
    0.4
  ],
  "zoom": 8.0,
  "indicador": "digital_exclusion",
  "filtro": "unit_key IN ('1701', '0802')",
  "capa_extra": null,
  "resaltados": [
    "1701",
    "0802"
  ]
}
```

---

## Paso 7: ¿Es el internet un derecho universal o un privilegio geográfico?

**English Title:** *Is the Internet a Universal Right or a Geographic Privilege?*

Cuando el acceso a trámites del Estado, educación virtual y empleo depende de una conexión fija que no llega a 4 de cada 10 hogares ecuatorianos, la conectividad condiciona el ejercicio de derechos. ¿Qué políticas públicas deben implementarse para que la inclusión digital no dependa del cantón en el que se nace?

**Resumen en inglés:** Final policy reflection on universal digital connectivity and geographic equity.  

**Cifra clave:** `N/A reflexión analítica` (Fuente: *Censo Ecuador 2022*)

```json
{
  "nivel": "canton",
  "centro": [
    -78.1834,
    -1.8312
  ],
  "zoom": 6.8,
  "indicador": "fixed_internet",
  "filtro": null,
  "capa_extra": null,
  "resaltados": []
}
```

---
