# La brecha digital

**ID de la Historia:** `04_brecha_digital`  
**Descripción:** Disparidades de acceso a internet fijo domiciliario vs telefonía celular en hogares ecuatorianos.

---

## Paso 1: La escala nacional de la conectividad en el hogar

**English Title:** *National Scale of Home Connectivity*

El Censo 2022 evaluó el equipamiento tecnológico en 5.188.827 hogares clasificados en el Ecuador. A nivel nacional, el 86,98% de los hogares reportó contar con al menos un teléfono celular (4.513.446 hogares). En contraste, el servicio de internet fijo domiciliario alcanzó una cobertura del 60,89% (3.159.588 hogares), marcando una brecha nacional de más de 26 puntos porcentuales entre conectividad móvil y fija.

**Resumen en inglés:** Nationwide, 86.98% of households have mobile phones, while only 60.89% have fixed broadband at home.  

**Cifra clave:** `60.89 % de hogares con internet fijo` (Fuente: *INEC CPV 2022, categories/nacion/data.parquet (H1004=1 / sum(H1004))*)

```sql
SELECT category, n, n * 100.0 / sum(n) OVER () AS pct FROM 'data/derived/counts/v1b1/categories/nacion/data.parquet' WHERE variable = 'H1004';
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

## Paso 2: Las islas conectadas: Rumiñahui y Cuenca

**English Title:** *Connected Islands: Rumiñahui and Cuenca*

El acceso a internet fijo se concentra en cantones metropolitanos y urbanos consolidados. El cantón Rumiñahui en Pichincha encabeza la conectividad domiciliaria con el 78,24% de sus hogares dotados de internet fijo. Cuenca, en Azuay, registra el 75,30%. En estos cantones, tres de cada cuatro hogares disponen de conectividad fija de banda ancha.

**Resumen en inglés:** Rumiñahui (78.24%) and Cuenca (75.30%) register the highest household fixed internet penetration rates.  

**Cifra clave:** `78.24 % de hogares` (Fuente: *INEC CPV 2022, categories/canton/17.parquet y 01.parquet*)

```sql
SELECT unit_key, sum(CASE WHEN category = '1' THEN n ELSE 0 END) * 100.0 / sum(n) AS pct_fixed_internet FROM 'data/derived/counts/v1b1/categories/canton/17.parquet' WHERE variable = 'H1004' AND unit_key = '1705' GROUP BY unit_key;
```

```json
{
  "nivel": "canton",
  "centro": [
    -78.44,
    -0.32
  ],
  "zoom": 10.5,
  "indicador": "fixed_internet",
  "filtro": "unit_key IN ('1705', '0101')",
  "capa_extra": null,
  "resaltados": [
    "1705",
    "0101"
  ]
}
```

---

## Paso 3: El desierto digital: Taisha y la ruralidad costera

**English Title:** *The Digital Desert: Taisha and Coastal Rurality*

En el extremo opuesto, la carencia de infraestructura fija aísla a extensos territorios. En el cantón amazónico Taisha (Morona Santiago), apenas el 14,82% de los hogares dispone de internet fijo. La brecha no es exclusiva del oriente: en la Costa rural, el cantón Paján (Manabí) registra un 22,64% de acceso fijo, dejando a más de tres cuartas partes de sus hogares desprovistos de conectividad domiciliaria.

**Resumen en inglés:** In Taisha (14.82%) and Paján (22.64%), less than a quarter of households have home broadband access.  

**Cifra clave:** `14.82 % de hogares` (Fuente: *INEC CPV 2022, categories/canton/14.parquet y 13.parquet*)

```sql
SELECT unit_key, sum(CASE WHEN category = '1' THEN n ELSE 0 END) * 100.0 / sum(n) AS pct_fixed_internet FROM 'data/derived/counts/v1b1/categories/canton/14.parquet' WHERE variable = 'H1004' AND unit_key IN ('1409', '1310') GROUP BY unit_key;
```

```json
{
  "nivel": "canton",
  "centro": [
    -78.5,
    -1.8
  ],
  "zoom": 8.0,
  "indicador": "fixed_internet",
  "filtro": "unit_key IN ('1409', '1310')",
  "capa_extra": null,
  "resaltados": [
    "1409",
    "1310"
  ]
}
```

---

## Paso 4: El giro de la brecha: celular universal frente a internet fijo

**English Title:** *The Gap Twist: Universal Mobile vs Fixed Broadband*

Al contrastar equipamientos dentro del mismo universo de hogares, emerge un desbalance estructural: en cantones rurales la telefonía móvil es masiva, pero la red fija es marginal. En Paján, el 80,48% de hogares posee celular, frente a solo el 22,64% con internet fijo: una brecha de 57,84 puntos. En El Empalme la discrepancia alcanza 51,71 puntos (87,74% vs 36,02%).

> **Hipótesis:** La disparidad entre la adopción de celulares y el acceso a internet fijo responde al menor costo inicial del servicio móvil bajo la modalidad prepago frente a los costos de instalación de las redes fijas. (el censo no lo mide). [Agencia de Regulación y Control de las Telecomunicaciones (ARCOTEL), 2023, pág. 8](https://www.arcotel.gob.ec/wp-content/uploads/2023/12/Boletin-cierre-de-a%C3%B1o.pdf).
>
> *Cita textual:* «En diciembre del año 2022 en la modalidad pospago se registraron 3.743.849 y en la modalidad prepago 13.740.159 líneas activas.»

**Resumen en inglés:** In Paján, 80.48% of households own cellphones but only 22.64% have fixed internet (57.84 percentage point gap).  

**Cifra clave:** `57.84 puntos porcentuales de diferencia` (Fuente: *INEC CPV 2022, categories/canton/13.parquet (H1002 vs H1004)*)

```sql
SELECT unit_key, sum(CASE WHEN variable='H1002' AND category='1' THEN n ELSE 0 END) * 100.0 / sum(CASE WHEN variable='H1002' THEN n ELSE 0 END) AS pct_celular, sum(CASE WHEN variable='H1004' AND category='1' THEN n ELSE 0 END) * 100.0 / sum(CASE WHEN variable='H1004' THEN n ELSE 0 END) AS pct_fijo, (sum(CASE WHEN variable='H1002' AND category='1' THEN n ELSE 0 END) * 100.0 / sum(CASE WHEN variable='H1002' THEN n ELSE 0 END)) - (sum(CASE WHEN variable='H1004' AND category='1' THEN n ELSE 0 END) * 100.0 / sum(CASE WHEN variable='H1004' THEN n ELSE 0 END)) AS brecha_puntos FROM 'data/derived/counts/v1b1/categories/canton/13.parquet' WHERE unit_key = '1310' GROUP BY unit_key;
```

```json
{
  "nivel": "canton",
  "centro": [
    -80.42,
    -1.55
  ],
  "zoom": 10.0,
  "indicador": "fixed_internet",
  "filtro": "unit_key IN ('1310', '0908')",
  "capa_extra": null,
  "resaltados": [
    "1310",
    "0908"
  ]
}
```

---

## Paso 5: La fractura parroquial dentro del mismo cantón

**English Title:** *Parish-Level Fracture Within the Same Canton*

La desigualdad digital se reproduce con fuerza al interior de los municipios. En el cantón Quito, la parroquia urbana Iñaquito alcanza un 91,99% de población de 5 años y más que usa internet. A corta distancia, en la parroquia noroccidental Pacto, el indicador se desploma al 50,54%. En una misma jurisdicción cantonal conviven estándares de conectividad diametralmente dispares.

**Resumen en inglés:** Within Quito, Iñaquito parish reaches 91.99% individual internet use, while rural Pacto drops to 50.54%.  

**Cifra clave:** `41.45 puntos porcentuales de diferencia` (Fuente: *INEC CPV 2022, cross_counts Fase 1B-2 (parroquias: 170157, 170161)*)

```sql
SELECT parish_key, internet_users * 100.0 / pop_5_plus AS pct_internet FROM cross_counts_v1b2 WHERE parish_key IN ('170157', '170161');
```

```json
{
  "nivel": "parroquia",
  "centro": [
    -78.6,
    0.05
  ],
  "zoom": 10.2,
  "indicador": "fixed_internet",
  "filtro": "canton_key = '1701'",
  "capa_extra": null,
  "resaltados": [
    "170157",
    "170161"
  ]
}
```

---

## Paso 6: La doble exclusión: edad y territorio

**English Title:** *Double Exclusion: Age and Geography*

La brecha digital combina factores generacionales y geográficos. En áreas metropolitanas como Quito, el 88,85% de jóvenes de 15 a 29 años utiliza internet. En contraste, en cantones rurales dispersos como Eloy Alfaro (Esmeraldas), el uso de internet entre personas de 65 años y más apenas alcanza el 8,72%, configurando una exclusión casi absoluta de las tecnologías digitales.

**Resumen en inglés:** Extreme generational divide: 88.85% of Quito youth are online vs only 8.72% of seniors in rural Eloy Alfaro.  

**Cifra clave:** `8.72 % de adultos mayores conectados` (Fuente: *INEC CPV 2022, cross_counts Fase 1B-2 (canton_keys: '1701', '0802')*)

```sql
SELECT canton_key, senior_internet_users * 100.0 / senior_pop AS pct_senior_internet FROM cross_counts_v1b2 WHERE canton_key IN ('1701', '0802');
```

```json
{
  "nivel": "canton",
  "centro": [
    -78.9,
    0.5
  ],
  "zoom": 8.5,
  "indicador": "fixed_internet",
  "filtro": "unit_key IN ('1701', '0802')",
  "capa_extra": null,
  "resaltados": [
    "1701",
    "0802"
  ]
}
```

---

## Paso 7: ¿Hacia una ciudadanía digital o una nueva desigualdad?

**English Title:** *Towards Digital Citizenship or Deepening Inequality?*

Con el 87% de los hogares conectados mediante telefonía móvil pero una persistente exclusión de redes fijas en la ruralidad, la brecha de calidad compromete la educación remota, el teletrabajo y los trámites públicos. ¿Cómo garantizar un acceso equitativo a servicios digitales avanzados para las comunidades que dependen exclusivamente de recargas telefónicas?

**Resumen en inglés:** Policy inquiry on closing structural digital quality gaps beyond mobile phone penetration.  

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
