# Fuentes Oficiales de Parroquias Urbanas en Ecuador y Auditoría de Compatibilidad Cartográfica

**Fecha de relevamiento y auditoría:** 2026-09-26  
**Rama de trabajo:** `feat/fuentes-parroquias-urbanas`  
**Autor:** Antigravity (Auditoría Técnica y Cartográfica Independiente)

---

## 1. Contexto Jurídico y Cartográfico

En el ordenamiento territorial del Ecuador coexisten dos regímenes de delimitación espacial con marcos normativos independientes:

1. **Límites Nacionales, Provinciales, Cantonales y Parroquiales Rurales:**
   - La fijación, arbitraje y registro de estas circunscripciones es competencia privativa del **Comité Nacional de Límites Internos (CONALI)** (COOTAD, Arts. 55 y 57; Ley para la Fijación de Límites Territoriales Internos).
   - El catálogo oficial del CONALI (`circunscripciones-ecuador-conali.xlsx`, enero 2025/2026, Ministerio de Gobierno) registra exactamente **1.053 circunscripciones**: 222 cabeceras cantonales (`XXYY50`) y 831 parroquias rurales (`XXYY51` a `XXYY99`).
   - El Instituto Nacional de Estadística y Censos (**INEC**) en el Censo de Población y Vivienda 2022 y en el **Marco Geoestadístico 2021** agrega la totalidad de la población y el amanzanamiento urbano consolidado de cada cantón bajo el código único de cabecera cantonal (`XXYY50`).

2. **Límites de Parroquias Urbanas Internas:**
   - La creación, supresión y delimitación de las parroquias urbanas es competencia exclusiva de los **Gobiernos Autónomos Descentralizados (GAD) Municipales o Metropolitanos**, mediante ordenanza cantonal (COOTAD, Arts. 54 y 57).
   - Ningún organismo nacional (ni el CONALI ni el INEC) emite ni custodia una capa cartográfica continua y homologada de parroquias urbanas para todo el país.
   - En consecuencia, toda incorporación de límites de parroquias urbanas al visor WebGIS del proyecto debe provenir de los **geoportales y servicios SIG oficiales de cada municipalidad**, y debe rotularse obligatoriamente con la advertencia:
     > *"Límites de parroquias urbanas provistos por los GAD Municipales. Fuente oficial municipal; límite no censal."*

---

## 2. Matriz Resumen de Fuentes Oficiales por Ciudad

Se auditaron las 10 cabeceras cantonales más pobladas del país, junto con Riobamba e Ibarra:

| Ciudad / Cantón | Institución Custodio | URL Exacta del Servicio o Descarga | Formato | CRS | Año / Vigencia | Licencia / Uso | Nº Parroquias | Nombres Incluidos | Estado de Acceso |
|---|---|---|---|---|---|---|:---:|:---:|:---:|
| **Quito** | MDMQ - STHV / DMIT | [`https://geoquito.quito.gob.ec/server/rest/services/Hosted/parroquias_ref_a/FeatureServer/0`](https://geoquito.quito.gob.ec/server/rest/services/Hosted/parroquias_ref_a/FeatureServer/0) | ArcGIS REST FeatureServer (GeoJSON/JSON) | EPSG:3857 / EPSG:32717 | 2024 (PUGS 2024) | Datos Abiertos Municipales / IDE Quito | 32 urbanas (60 en total) | Sí (`dpa_despar`) | **Operacional (200 OK)** |
| **Guayaquil** | M.I. Municipalidad de Guayaquil - DUMDYT | [`https://geoportalcat.guayaquil.gob.ec/arcgis/rest/services/Geoportal_Actualizado/GEOPORTAL_ACTUALIZADO/MapServer/9`](https://geoportalcat.guayaquil.gob.ec/arcgis/rest/services/Geoportal_Actualizado/GEOPORTAL_ACTUALIZADO/MapServer/9) | ArcGIS REST MapServer (GeoJSON/JSON) | EPSG:32717 (UTM 17S) | 2022-2023 | Geoportal Municipal (Acceso público anónimo) | 16 polígonos (14 parroquias) | Sí (`Nam`) | **Operacional (200 OK)** |
| **Cuenca** | GAD Municipal de Cuenca - DGPT / IDE | [`https://ide.cuenca.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=dgpt_limites:limite_parroquias_urbanas&outputFormat=application/json`](https://ide.cuenca.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=dgpt_limites:limite_parroquias_urbanas&outputFormat=application/json) | OGC WFS (GeoJSON, SHP, GML) | EPSG:32717 (UTM 17S) | 2022 (PDOT/PUGS) | Datos Abiertos / IDE Cuenca | 15 urbanas | Sí (`parroquias`) | **Operacional (200 OK)** |
| **Loja** | GAD Municipal de Loja - Planificación / SIL | [`http://sil.loja.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=pugs_2023_2033:limites_parroquias_urbanas_2023_2033&outputFormat=application/json`](http://sil.loja.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=pugs_2023_2033:limites_parroquias_urbanas_2023_2033&outputFormat=application/json) | OGC WFS (GeoJSON, SHP, GML) | EPSG:32717 (UTM 17S) | 2023 (PUGS 2023-2033) | Sistema de Información Local (Uso público) | 6 urbanas | Sí (`parroquia`) | **Operacional (200 OK)** |
| **Ambato** | GAD Municipalidad de Ambato - Catastros / SIG | [`https://arcgis.ambato.gob.ec/mapas/rest/services/MXD/AMBATO/MapServer/1`](https://arcgis.ambato.gob.ec/mapas/rest/services/MXD/AMBATO/MapServer/1) | ArcGIS REST MapServer (GeoJSON/JSON) | EPSG:32717 (UTM 17S) | 2024-2025 | SIG Municipal Ambato (Uso público en consultas) | 8 urbanas | Sí (`PARROQUIA`) | **Operacional (200 OK)** |
| **Riobamba** | GAD Municipal de Riobamba - Planificación | [`https://services9.arcgis.com/WR0heBS35BiLFAuA/arcgis/rest/services/parroquias_urbanas/FeatureServer/0`](https://services9.arcgis.com/WR0heBS35BiLFAuA/arcgis/rest/services/parroquias_urbanas/FeatureServer/0) | ArcGIS REST FeatureServer (GeoJSON/JSON) | EPSG:3857 / EPSG:32717 | 2022-2023 | Planificación Urbana (Público institucional) | 5 urbanas | Sí (`PARROQUIA`) | **Operacional (200 OK)** |
| **Ibarra** | Repositorio UTN GIS (Univ. Técnica del Norte) | [`https://services5.arcgis.com/1ICMZTKY59jmGreu/arcgis/rest/services/PARROQUIAS_IBARRA/FeatureServer/0`](https://services5.arcgis.com/1ICMZTKY59jmGreu/arcgis/rest/services/PARROQUIAS_IBARRA/FeatureServer/0) | ArcGIS REST FeatureServer (GeoJSON/JSON) | EPSG:3857 / EPSG:32717 | 2022 | Académico (No municipal) | 5 urbanas | Sí (`parroquia`) | **Fuente académica, no municipal** |
| **Santo Domingo** | GAD Municipal de Santo Domingo - Planificación | [`https://geoportal.santodomingo.gob.ec/`](https://geoportal.santodomingo.gob.ec/) (API: `/api/v1/layers`) | Visor SPA / API REST | UTM 17S | 2023 | Restringido (API con autenticación) | 7 urbanas | Sí (en visor) | **Visor activo / API 401 Unauthorized** |
| **Portoviejo** | GAD Municipal de Portoviejo - Portoviejo 2035 | [`https://services8.arcgis.com/X3k9gMjGtUbPqiTf/arcgis/rest/services/Parro_Barro_PIT/FeatureServer`](https://services8.arcgis.com/X3k9gMjGtUbPqiTf/arcgis/rest/services/Parro_Barro_PIT/FeatureServer) | ArcGIS REST FeatureServer | EPSG:3857 | 2022 | Restringido (Token ArcGIS obligatorio) | 9 urbanas | Sí (en visor) | **Visor activo / REST Error 499 (Token)** |
| **Manta** | GAD Municipal de Manta - Planificación | [`https://geoportal.manta.gob.ec/`](https://geoportal.manta.gob.ec/) | Plataforma Web GeoManta | UTM 17S | 2022-2023 | Restringido (Login obligatorio) | 5 urbanas | Sí (en visor) | **Geoportal privado (Login required)** |
| **Durán** | GAD Municipal de Durán | No disponible (`geoportal.duran.gob.ec` sin DNS) | Sin SIG web | N/A | 2020 (Ordenanza) | N/A | 3 urbanas | N/A | **Sin servidor SIG público** |
| **Machala** | GAD Municipal de Machala | No disponible (`geoportal.machala.gob.ec` sin DNS) | Sin SIG web | N/A | 2021 (PUGS/PDF) | N/A | 5 urbanas | N/A | **Sin servidor SIG público** |

---

## 3. Detalle Técnico de Auditoría por Ciudad

Cada uno de los servicios y URLs listados en este informe fue probado mediante peticiones HTTP automatizadas, inspección de encabezados y descarga directa de geometrías.

### 3.1 Quito (Distrito Metropolitano de Quito)
- **Institución:** Secretaría de Territorio, Hábitat y Vivienda (STHV) / Dirección Metropolitana de Información Territorial (DMIT).
- **Endpoint del FeatureServer:**  
  `https://geoquito.quito.gob.ec/server/rest/services/Hosted/parroquias_ref_a/FeatureServer/0`
- **Consulta de Descarga GeoJSON Directa:**  
  `https://geoquito.quito.gob.ec/server/rest/services/Hosted/parroquias_ref_a/FeatureServer/0/query?where=1=1&outFields=*&f=geojson&outSR=32717`
- **Estructura y Atributos:**  
  Total de registros: 60 parroquias metropolitanas.  
  - Parroquias urbanas (32 registros): códigos `170101` a `170132`.
  - Parroquias rurales (28 registros): códigos `170151` a `170186`.
  - Campos: `dpa_parroq` (código DPA), `dpa_despar` (nombre oficial), `SHAPE__Area`, `SHAPE__Length`.
- **Listado de Parroquias Urbanas (32):**  
  Belisario Quevedo (170101), Carcelén (170102), Centro Histórico (170103), Cochapamba (170104), Comité del Pueblo (170105), Cotocollao (170106), Chilibulo (170107), Chillogallo (170108), Chimbacalle (170109), El Condado (170110), Guamaní (170111), **Iñaquito (170112)**, Itchimbía (170113), Jipijapa (170114), Kennedy (170115), La Argelia (170116), La Concepción (170117), La Ecuatoriana (170118), La Ferroviaria (170119), La Libertad (170120), La Magdalena (170121), La Mena (170122), Mariscal Sucre (170123), Ponceano (170124), Puengasí (170125), Quitumbe (170126), Rumipamba (170127), San Bartolo (170128), San Isidro del Inca (170129), San Juan (170130), Solanda (170131), Turubamba (170132).
- **Verificación:** `HTTP 200 OK`. Archivo GeoJSON de 2.385 KB descargado e integrado en las pruebas de compatibilidad.

### 3.2 Guayaquil
- **Institución:** Muy Ilustre Municipalidad de Guayaquil — Dirección de Urbanismo, Movilidad y Desarrollo Territorial (DUMDYT).
- **Endpoint del MapServer:**  
  `https://geoportalcat.guayaquil.gob.ec/arcgis/rest/services/Geoportal_Actualizado/GEOPORTAL_ACTUALIZADO/MapServer/9`
- **Consulta de Descarga GeoJSON Directa:**  
  `https://geoportalcat.guayaquil.gob.ec/arcgis/rest/services/Geoportal_Actualizado/GEOPORTAL_ACTUALIZADO/MapServer/9/query?where=1=1&outFields=*&f=geojson&outSR=32717`
- **Estructura y Atributos:**  
  Total de registros: 16 polígonos.  
  - Parroquias representadas (14 nombres únicos): Roca, Rocafuerte, Olmedo, Bolívar, Ayacucho, García Moreno, Sucre, Nueve de Octubre, Urdaneta, Letamendi, Febres Cordero, Pascuales, Tarqui (2 polígonos), Ximena, Carbo.
  - Campos: `Nam` (nombre de la parroquia), `OBJECTID`, `Shape_Leng`, `Shape.STArea()`.
- **Verificación:** `HTTP 200 OK`. Archivo GeoJSON de 316 KB descargado e integrado en las pruebas de compatibilidad.

### 3.3 Cuenca
- **Institución:** GAD Municipal del Cantón Cuenca — Dirección General de Planificación Territorial (DGPT) / Infraestructura de Datos Espaciales (IDE Cuenca).
- **Endpoint WFS Oficial:**  
  `https://ide.cuenca.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=dgpt_limites:limite_parroquias_urbanas&outputFormat=application/json`
- **Estructura y Atributos:**  
  Total de registros: 15 parroquias urbanas.  
  - Campos: `parroquias` (nombre), `habitantes`, `poblacion`, `area_ha`, `shape_area`.
- **Listado de Parroquias Urbanas (15):**  
  Bellavista, Cañaribamba, El Batán, El Sagrario, El Vecino, Gil Ramírez Dávalos, Hermano Miguel, Huayna Cápac, Machángara, Monay, San Blas, San Sebastián, Sucre, Totoracocha, Yanuncay.
- **Verificación:** `HTTP 200 OK`. Archivo GeoJSON de 540 KB descargado e integrado en las pruebas de compatibilidad.

### 3.4 Loja
- **Institución:** GAD Municipal de Loja — Dirección de Planificación / Sistema de Información Local (SIL).
- **Endpoint WFS Oficial:**  
  `http://sil.loja.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=pugs_2023_2033:limites_parroquias_urbanas_2023_2033&outputFormat=application/json`
- **Estructura:** 6 parroquias urbanas bajo ordenanza PUGS 2023-2033 (Sucre, San Sebastián, Punzara, Sagrario, El Valle, Carigán).
- **Verificación:** `HTTP 200 OK`. CRS EPSG:32717.

### 3.5 Ambato
- **Institución:** GAD Municipalidad de Ambato — Dirección de Catastros y Avalúos / SIG Municipal.
- **Endpoint MapServer Oficial:**  
  `https://arcgis.ambato.gob.ec/mapas/rest/services/MXD/AMBATO/MapServer/1`
- **Estructura:** 8 parroquias urbanas (San Francisco, La Matriz, Huachi Loreto, Atocha Ficoa, La Merced, Celiano Monge, La Península, Huachi Chico).
- **Verificación:** `HTTP 200 OK`. CRS EPSG:32717 nativo con actualizaciones 2024-2025.

### 3.6 Riobamba
- **Institución:** GAD Municipal de Riobamba (GADMR) — Dirección de Gestión de Planificación.
- **Endpoint FeatureServer:**  
  `https://services9.arcgis.com/WR0heBS35BiLFAuA/arcgis/rest/services/parroquias_urbanas/FeatureServer/0`
- **Estructura:** 5 parroquias urbanas (Lizarzaburu, Velasco, Yaruquíes, Veloz, Maldonado).
- **Verificación:** `HTTP 200 OK`.

### 3.7 Ibarra (Fuente Académica, No Municipal)
- **Institución:** Repositorio UTN GIS (Universidad Técnica del Norte / Centro SIG).
- **Endpoint FeatureServer:**  
  `https://services5.arcgis.com/1ICMZTKY59jmGreu/arcgis/rest/services/PARROQUIAS_IBARRA/FeatureServer/0`
- **Diagnóstico institucional:** Catalogada explícitamente como **fuente académica, no municipal**. El geoportal municipal directo (`geoportal.ibarra.gob.ec`) responde con código `HTTP 410 Gone` (servicio municipal dado de baja o no disponible públicamente). Se excluye de la recomendación de lanzamiento de Fase 3 hasta contar con validación oficial municipal directa.

### 3.8 Santo Domingo, Portoviejo, Manta, Machala y Durán
- **Santo Domingo:** Geoportal activo (`geoportal.santodomingo.gob.ec`), pero su API REST (`/api/v1/layers`) responde `HTTP 401 Unauthorized` (requiere credenciales).
- **Portoviejo:** Geoportal Fénix activo en visor web, pero su FeatureServer (`Parro_Barro_PIT`) responde `499 Token Required`.
- **Manta:** Geoportal `geoportal.manta.gob.ec` bajo autenticación obligatoria (Login AdminLTE).
- **Machala y Durán:** Sin servicios web geográficos (WFS/REST públicos); delimitaciones restringidas a ordenanzas impresas y planos PDF.

---

## 4. Auditoría de Compatibilidad Espacial a Nivel de Manzana (`man_a`)

Para evaluar la compatibilidad cartográfica con el mayor nivel de granularidad geográfica del Censo 2022, se descargaron las capas de polígonos municipales y se cruzaron espacialmente contra la totalidad de las manzanas cartográficas del **Marco Geoestadístico 2021 del INEC (`man_a`)** en el sistema de coordenadas proyectadas **EPSG:32717 (UTM 17S)**, vinculando la población censal de cada manzana desde las salidas exactas de Fase 1B-1 (`finest/*.parquet`).

### Metodología de la Prueba a Nivel Manzana
1. Se filtraron las manzanas cartográficas de `man_a` de la cabecera cantonal (`man LIKE '170150%'` en Quito, `'090150%'` en Guayaquil y `'010150%'` en Cuenca).
2. Se vinculó a cada manzana su población censal oficial (`population`).
3. Se calculó el centroide geométrico de cada manzana (`manzana.geometry.centroid`) y se ejecutó un cruce punto-en-polígono (*Point-in-Polygon, within*) con los polígonos de las parroquias urbanas municipales.
4. Se cuantificó la asignación unívoca (% de manzanas y % de población asignada) y el remanente ubicado fuera de los límites municipales.
5. Se analizaron las manzanas cortadas por límites:
   - Se evaluó cuántas manzanas intersecan alguna línea de frontera parroquial (interior o perimetral).
   - Se cuantificó la **población censal exacta que reside en manzanas cortadas por el límite**.

---

### Resultados Cuantitativos a Nivel Manzana

```
========================================================================================
MÉTRICA DE COMPATIBILIDAD                       QUITO          GUAYAQUIL         CUENCA
========================================================================================
Código cabecera cantonal (Marco 2021)          170150            090150          010150
Total manzanas cartográficas (man_a)           16.907            30.580           4.049
Población censal vinculada a man_a          1.766.196 hab     2.653.650 hab     360.359 hab
Población total censal cabecera             1.776.364 hab     2.665.392 hab     361.524 hab
----------------------------------------------------------------------------------------
ASIGNACIÓN POR CENTROIDE DE MANZANA:
  Manzanas asignadas sin ambigüedad            16.888 (99,89%)   27.339 (89,40%)  4.047 (99,95%)
  Población en manzanas asignadas           1.763.309 (99,84%)2.470.928 (93,11%)360.150 (99,94%)
  
  Manzanas fuera de parroquias urbanas             19  (0,11%)    3.241 (10,60%)      2  (0,05%)
  Población fuera de parroquias urbanas         2.887  (0,16%)  182.722  (6,89%)    209  (0,06%)
  
  Ambigüedad múltiple (solapamiento)                0  (0,00%)        0  (0,00%)      0  (0,00%)
----------------------------------------------------------------------------------------
MANZANAS CORTADAS POR LÍMITES PARROQUIALES:
  Manzanas que cortan línea de límite             310  (1,83%)      467  (1,53%)    147  (3,63%)
  Población en manzanas cortadas por límite    54.835  (3,10%)   65.404  (2,46%)  8.068  (2,24%)
  
  Manzanas con corte interparroquial (>= 2)       265  (1,57%)       58  (0,19%)     92  (2,27%)
  Población en corte interparroquial           46.818  (2,65%)    8.862  (0,33%)  4.269  (1,18%)
  
  Manzanas 100% contenidas en 1 parroquia      16.597 (98,17%)   30.113 (98,47%)  3.902 (96,37%)
  Población 100% contenida en 1 parroquia   1.711.361 (96,90%)2.588.246 (97,54%)352.291 (97,76%)
========================================================================================
```

---

### Diagnóstico Territorial y Hallazgos a Escala Manzana

1. **Quito (MDMQ):**
   - **Precisión casi perfecta (99,89% de manzanas y 99,84% de población):** 16.888 manzanas con 1.763.309 habitantes quedan asignadas de forma unívoca a una de las 32 parroquias urbanas oficiales.
   - **Población en manzanas cortadas (3,10%):** Solo 310 manzanas (54.835 habitantes) cortan alguna línea de división parroquial (ej. manzanas sobre ejes viales anchos como Av. 10 de Agosto, Av. Amazonas o Av. Mariscal Sucre). Más del **98,17% de las manzanas (16.597)** están 100% contenidas dentro de su respectiva parroquia urbana.
   - **Manzanas no asignadas (19 manzanas, 2.887 habitantes):** Corresponden a bordes periurbanos en quebradas adyacentes a parroquias rurales (Llano Chico, Zámbiza, Cumbayá). Al evaluar las 60 parroquias metropolitanas completas, la asignación es del 100%.

2. **Guayaquil (M.I. Municipalidad de Guayaquil):**
   - **Mancha urbana consolidada (89,40% de manzanas y 93,11% de población):** 27.339 manzanas albergando a 2.470.928 habitantes se asignan con total congruencia a las parroquias tradicionales y de planificación de la urbe (Tarqui, Febres Cordero, Ximena, Pascuales, etc.).
   - **Mínimo impacto de corte (1,53% de manzanas y 2,46% de población):** Solo 467 manzanas (65.404 habitantes) cortan los límites parroquiales, y solo 58 manzanas (8.862 habitantes) quedan divididas entre dos parroquias urbanas colindantes. El **98,47% de las manzanas** está 100% contenido en su polígono parroquial.
   - **Tratamiento del territorio exterior (3.241 manzanas, 182.722 habitantes):**  
     La capa municipal `MapServer/9` delimita la conurbación urbana continua de Guayaquil. Sin embargo, el INEC bajo el código cantonal `090150` incluye una franja territorial extensa hacia el oeste del cantón: el corredor de Vía a la Costa, Puerto Hondo, las comunas de Chongón y sectores periurbanos de manglar.  
     **Regla adoptada:** En estricto apego al censo, estas 3.241 manzanas y sus 182.722 habitantes quedan catalogadas como:  
     `"Cabecera Guayaquil · fuera de las parroquias urbanas municipales"`  
     *No se crea ninguna unidad cartográfica nueva ni código artificial*, manteniéndose bajo la cabecera cantonal `090150`.

3. **Cuenca (GAD Municipal de Cuenca):**
   - **Asignación prácticamente total (99,95% de manzanas y 99,94% de población):** 4.047 manzanas con 360.150 habitantes se asignan sin ambigüedad a las 15 parroquias urbanas oficiales.
   - **Población en manzanas cortadas (2,24%):** Solo 147 manzanas (8.068 habitantes) cortan fronteras parroquiales (generalmente a lo largo de las riberas de los ríos Tomebamba, Yanuncay y Machángara). El **96,37% de las manzanas** está 100% contenida dentro de su polígono parroquial.

---

## 5. Recomendación Final y Plan de Integración en el Visor WebGIS

1. **Ciudades Habilitadas para Lanzamiento Inmediato (Fase 3):**
   Se recomienda implementar las siguientes **6 ciudades** que disponen de servicios oficiales 100% municipales, abiertos, verificados y con descarga directa:
   - **Quito (32 parroquias):** Capa STHV / DMIT (`Hosted/parroquias_ref_a`). Permite desbloquear el cálculo definitivo del índice de **Iñaquito (170112)** en la Historia 1 de scrollytelling.
   - **Guayaquil (14 parroquias):** Capa DUMDYT (`MapServer/9`), catalogando el remanente occidental como *"Cabecera Guayaquil · fuera de las parroquias urbanas municipales"*.
   - **Cuenca (15 parroquias):** Capa DGPT / IDE Cuenca (`dgpt_limites:limite_parroquias_urbanas`).
   - **Loja (6 parroquias):** Capa SIL / Planificación (`pugs_2023_2033:limites_parroquias_urbanas_2023_2033`).
   - **Ambato (8 parroquias):** Capa Catastros / SIG (`MXD/AMBATO/MapServer/1`).
   - **Riobamba (5 parroquias):** Capa GADMR (`parroquias_urbanas/FeatureServer/0`).

2. **Ciudades Excluidas del Lanzamiento:**
   - **Ibarra (5 parroquias):** Marcada como **"fuente académica, no municipal"** (repositorio UTN GIS). Al encontrarse inactivo el servicio municipal directo (`geoportal.ibarra.gob.ec` responde HTTP 410), queda **fuera de la recomendación de lanzamiento** hasta contar con una capa validada formalmente por el GAD Municipal de Ibarra.
   - **Santo Domingo, Portoviejo y Manta:** Excluidas por requerir autenticación o token privado (HTTP 401 / 499 / Login). Requieren gestión formal ante los GAD Municipales.
   - **Machala y Durán:** Excluidas por no disponer de infraestructura de datos espaciales en línea.

3. **Estandarización de Atributos para el Frontend:**
   Se recomienda estructurar la tabla de cruce en el pipeline del proyecto con este esquema tabular unificado:
   ```json
   {
     "manzana_key": "170150001001001",
     "sector_key": "170150001001",
     "canton_key": "1701",
     "parroquia_censal": "170150",
     "parroquia_urbana_codigo": "170112",
     "parroquia_urbana_nombre": "IÑAQUITO",
     "fuente_limite": "MDMQ-STHV-2024",
     "es_limite_censal": false,
     "metodo_asignacion": "centroide_manzana_en_poligono"
   }
   ```
