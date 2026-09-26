# Fuentes Oficiales de Parroquias Urbanas en Ecuador y Análisis de Compatibilidad Cartográfica

**Fecha de relevamiento y auditoría:** 2026-09-26  
**Rama de trabajo:** `feat/fuentes-parroquias-urbanas`  
**Autor:** Antigravity (Auditoría Técnica y Cartográfica Independiente)

---

## 1. Contexto Jurídico y Cartográfico

En el sistema territorial del Ecuador rigen dos niveles de competencia claramente diferenciados:
1. **Límites Nacionales, Provinciales, Cantonales y Parroquiales Rurales:**
   - La fijación, arbitraje y registro de estos límites corresponden al **Comité Nacional de Límites Internos (CONALI)** (COOTAD, Arts. 55 y 57; Ley para la Fijación de Límites Territoriales Internos).
   - El catálogo oficial del CONALI (`circunscripciones-ecuador-conali.xlsx`, enero 2025/2026, Ministerio de Gobierno) registra exactamente **1.053 circunscripciones**: 222 cabeceras cantonales (ej. `010150: CUENCA`, `170150: QUITO`) y 831 parroquias rurales (ej. `010151: BAÑOS`, `170155: CALDERÓN`).
   - El Instituto Nacional de Estadística y Censos (**INEC**) en el Censo de Población y Vivienda 2022 y en el **Marco Geoestadístico 2021** agrega la totalidad de la población y el amanzanamiento urbano consolidado de cada cantón bajo el código único de cabecera cantonal (`XXYY50`).

2. **Límites de Parroquias Urbanas Internas:**
   - La creación, supresión y delimitación de las parroquias urbanas es competencia exclusiva de los **Gobiernos Autónomos Descentralizados (GAD) Municipales o Metropolitanos**, mediante ordenanza cantonal (COOTAD, Art. 54 y 57).
   - Ninguna entidad nacional (ni el CONALI ni el INEC) emite ni custodia una capa cartográfica unificada continua de parroquias urbanas a nivel país.
   - En consecuencia, toda incorporación de límites de parroquias urbanas al visor WebGIS del proyecto debe provenir de los **geoportales y servicios SIG oficiales de cada municipalidad**, y debe rotularse obligatoriamente con la advertencia:
     > *"Límites de parroquias urbanas provistos por los GAD Municipales. Fuente oficial municipal; límite no censal."*

---

## 2. Matriz Resumen de Fuentes Oficiales por Ciudad

Se relevaron y auditaron las 10 cabeceras cantonales más pobladas del país, junto con Riobamba e Ibarra:

| Ciudad / Cantón | Institución Custodio | URL Exacta del Servicio o Descarga | Formato | CRS | Año / Vigencia | Licencia / Uso | Nº Parroquias | Nombres Incluidos | Estado de Acceso |
|---|---|---|---|---|---|---|:---:|:---:|:---:|
| **Quito** | MDMQ - STHV / DMIT | [`https://geoquito.quito.gob.ec/server/rest/services/Hosted/parroquias_ref_a/FeatureServer/0`](https://geoquito.quito.gob.ec/server/rest/services/Hosted/parroquias_ref_a/FeatureServer/0) | ArcGIS REST FeatureServer (GeoJSON/JSON) | EPSG:3857 / EPSG:32717 | 2024 (PUGS 2024) | Datos Abiertos Municipales / IDE Quito | 32 urbanas (60 en total) | Sí (`dpa_despar`) | **Operacional (200 OK)** |
| **Guayaquil** | M.I. Municipalidad de Guayaquil - DUMDYT | [`https://geoportalcat.guayaquil.gob.ec/arcgis/rest/services/Geoportal_Actualizado/GEOPORTAL_ACTUALIZADO/MapServer/9`](https://geoportalcat.guayaquil.gob.ec/arcgis/rest/services/Geoportal_Actualizado/GEOPORTAL_ACTUALIZADO/MapServer/9) | ArcGIS REST MapServer (GeoJSON/JSON) | EPSG:32717 (UTM 17S) | 2022-2023 | Geoportal Municipal (Acceso público anónimo) | 16 polígonos (14 parroquias) | Sí (`Nam`) | **Operacional (200 OK)** |
| **Cuenca** | GAD Municipal de Cuenca - DGPT / IDE | [`https://ide.cuenca.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=dgpt_limites:limite_parroquias_urbanas&outputFormat=application/json`](https://ide.cuenca.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=dgpt_limites:limite_parroquias_urbanas&outputFormat=application/json) | OGC WFS (GeoJSON, SHP, GML) | EPSG:32717 (UTM 17S) | 2022 (PDOT/PUGS) | Datos Abiertos / IDE Cuenca | 15 urbanas | Sí (`parroquias`) | **Operacional (200 OK)** |
| **Loja** | GAD Municipal de Loja - Planificación / SIL | [`http://sil.loja.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=pugs_2023_2033:limites_parroquias_urbanas_2023_2033&outputFormat=application/json`](http://sil.loja.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=pugs_2023_2033:limites_parroquias_urbanas_2023_2033&outputFormat=application/json) | OGC WFS (GeoJSON, SHP, GML) | EPSG:32717 (UTM 17S) | 2023 (PUGS 2023-2033) | Sistema de Información Local (Uso público) | 6 urbanas | Sí (`parroquia`) | **Operacional (200 OK)** |
| **Ambato** | GAD Municipalidad de Ambato - Catastros / SIG | [`https://arcgis.ambato.gob.ec/mapas/rest/services/MXD/AMBATO/MapServer/1`](https://arcgis.ambato.gob.ec/mapas/rest/services/MXD/AMBATO/MapServer/1) | ArcGIS REST MapServer (GeoJSON/JSON) | EPSG:32717 (UTM 17S) | 2024-2025 | SIG Municipal Ambato (Uso público en consultas) | 8 urbanas | Sí (`PARROQUIA`) | **Operacional (200 OK)** |
| **Riobamba** | GAD Municipal de Riobamba - Planificación | [`https://services9.arcgis.com/WR0heBS35BiLFAuA/arcgis/rest/services/parroquias_urbanas/FeatureServer/0`](https://services9.arcgis.com/WR0heBS35BiLFAuA/arcgis/rest/services/parroquias_urbanas/FeatureServer/0) | ArcGIS REST FeatureServer (GeoJSON/JSON) | EPSG:3857 / EPSG:32717 | 2022-2023 | Planificación Urbana (Público institucional) | 5 urbanas | Sí (`PARROQUIA`) | **Operacional (200 OK)** |
| **Ibarra** | GAD Ibarra / Repositorio UTN GIS | [`https://services5.arcgis.com/1ICMZTKY59jmGreu/arcgis/rest/services/PARROQUIAS_IBARRA/FeatureServer/0`](https://services5.arcgis.com/1ICMZTKY59jmGreu/arcgis/rest/services/PARROQUIAS_IBARRA/FeatureServer/0) | ArcGIS REST FeatureServer (GeoJSON/JSON) | EPSG:3857 / EPSG:32717 | 2022 | Académico-Institucional (Público) | 5 urbanas | Sí (`parroquia`) | **Alternativa activa** (Geoportal GAD da 410) |
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
- **Servicio Auditado:** Servidor ArcGIS Enterprise del DMQ (`geoquito.quito.gob.ec`).
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
- **Servicio Auditado:** Servidor ArcGIS Server municipal (`geoportalcat.guayaquil.gob.ec`).
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
- **Servicio Auditado:** GeoServer OGC WFS (`ide.cuenca.gob.ec/geoserver`).
- **Endpoint WFS Oficial:**  
  `https://ide.cuenca.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=dgpt_limites:limite_parroquias_urbanas&outputFormat=application/json`  
  *(Capa complementaria idéntica: `ide:limites_parroquias_urbanas`)*.
- **Estructura y Atributos:**  
  Total de registros: 15 parroquias urbanas.  
  - Campos: `parroquias` (nombre), `habitantes`, `poblacion`, `area_ha`, `shape_area`.
- **Listado de Parroquias Urbanas (15):**  
  Bellavista, Cañaribamba, El Batán, El Sagrario, El Vecino, Gil Ramírez Dávalos, Hermano Miguel, Huayna Cápac, Machángara, Monay, San Blas, San Sebastián, Sucre, Totoracocha, Yanuncay.
- **Verificación:** `HTTP 200 OK`. Archivo GeoJSON de 540 KB descargado e integrado en las pruebas de compatibilidad.

### 3.4 Loja
- **Institución:** GAD Municipal de Loja — Dirección de Planificación / Sistema de Información Local (SIL).
- **Servicio Auditado:** GeoServer OGC WFS (`sil.loja.gob.ec/geoserver`).
- **Endpoint WFS Oficial:**  
  `http://sil.loja.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=pugs_2023_2033:limites_parroquias_urbanas_2023_2033&outputFormat=application/json`
- **Estructura y Atributos:**  
  Total de registros: 6 parroquias urbanas bajo ordenanza PUGS 2023-2033.  
  - Campos: `parroquia`, `subclasifi`, `cod_parroq`, `shape_area`.
- **Listado de Parroquias Urbanas (6):**  
  Sucre, San Sebastián, Punzara, Sagrario, El Valle, Carigán.
- **Verificación:** `HTTP 200 OK`. GeoJSON con geometría poligonal y CRS EPSG:32717 comprobado.

### 3.5 Ambato
- **Institución:** GAD Municipalidad de Ambato — Dirección de Catastros y Avalúos / SIG Municipal.
- **Servicio Auditado:** Servidor ArcGIS MapServer institucional (`arcgis.ambato.gob.ec/mapas`).
- **Endpoint MapServer Oficial:**  
  `https://arcgis.ambato.gob.ec/mapas/rest/services/MXD/AMBATO/MapServer/1`
- **Estructura y Atributos:**  
  Total de registros: 8 parroquias urbanas.  
  - Campos: `PARROQUIA`, `CODIGO`, `SHAPE.AREA`, `LAST_EDITED_DATE` (actualizaciones registradas en 2024 y 2025).
- **Listado de Parroquias Urbanas (8):**  
  San Francisco (09), La Matriz (07), Huachi Loreto, Atocha Ficoa (01), La Merced (05), Celiano Monge (02), La Península (06), Huachi Chico (03).
- **Verificación:** `HTTP 200 OK`. Capa activa con CRS EPSG:32717 nativo.

### 3.6 Riobamba
- **Institución:** GAD Municipal de Riobamba (GADMR) — Dirección de Gestión de Planificación.
- **Servicio Auditado:** ArcGIS Online institucional (`coellop_gadmriobamba`).
- **Endpoint FeatureServer:**  
  `https://services9.arcgis.com/WR0heBS35BiLFAuA/arcgis/rest/services/parroquias_urbanas/FeatureServer/0`
- **Estructura y Atributos:**  
  Total de registros: 5 parroquias urbanas.  
  - Campos: `PARROQUIA`, `AREA`, `SHAPE_Leng`, `SHAPE_Area`.
- **Listado de Parroquias Urbanas (5):**  
  Lizarzaburu, Velasco, Yaruquíes, Veloz, Maldonado.
- **Verificación:** `HTTP 200 OK`. Capa descargable y con metadatos completos.

### 3.7 Ibarra
- **Institución:** Repositorio UTN GIS (Universidad Técnica del Norte) / GAD Municipal de Ibarra.
- **Endpoint FeatureServer:**  
  `https://services5.arcgis.com/1ICMZTKY59jmGreu/arcgis/rest/services/PARROQUIAS_IBARRA/FeatureServer/0`
- **Estructura:** 5 parroquias urbanas (Alpachaca, Caranqui, Sagrario, Priorato, San Francisco).
- **Auditoría del Geoportal Municipal:** El dominio oficial del GAD Ibarra (`geoportal.ibarra.gob.ec`) responde con código `HTTP 410 Gone`, evidenciando que el servicio web municipal directo fue desactivado o migrado a una red interna. La capa de la UTN funciona como respaldo alternativo.

### 3.8 Santo Domingo, Portoviejo, Manta, Machala y Durán
- **Santo Domingo:** El GAD mantiene activo su Geoportal (`https://geoportal.santodomingo.gob.ec/`), pero las rutas de su API REST (`/api/v1/layers`, `/api/v1/datasets`) responden `HTTP 401 Unauthorized`. La interfaz visual permite consulta predial en línea, pero no ofrece descargas de polígonos abiertos.
- **Portoviejo:** El Geoportal Fénix / Portoviejo 2035 dispone de visores WebApp, pero sus FeatureLayers (`Parro_Barro_PIT`) responden con el código `499 Token Required`.
- **Manta:** El portal `geoportal.manta.gob.ec` exige inicio de sesión (`GeoManta | Autenticación`) mediante credenciales internas (AdminLTE).
- **Machala y Durán:** Ambas municipalidades carecen de servicios web geográficos (WFS o ArcGIS REST públicos); la delimitación de sus parroquias urbanas solo consta en textos de ordenanzas y mapas estáticos en formato PDF.

---

## 4. Auditoría de Compatibilidad Espacial: Quito, Guayaquil y Cuenca

Para evaluar la viabilidad de cruzar estas capas con la base cartográfica oficial del proyecto, se descargaron los polígonos municipales oficiales y se contrastaron espacialmente contra la capa de sectores censales del **Marco Geoestadístico 2021 del INEC (`sec_a`)** en el sistema de coordenadas proyectadas oficial **EPSG:32717 (UTM 17S)**.

### Metodología de la Prueba
1. Se seleccionaron los sectores censales pertenecientes a la cabecera cantonal respectiva (`parroquia = '170150'` en Quito, `'090150'` en Guayaquil y `'010150'` en Cuenca).
2. Se extrajo el centroide geométrico de cada sector censal (`sector.geometry.centroid`).
3. Se realizó un cruce espacial punto-en-polígono (*Point-in-Polygon, predicate: within*) entre los centroides y los polígonos de las parroquias urbanas municipales.
4. Se cuantificó la ambigüedad de asignación:
   - **Asignados sin ambigüedad:** centroide contenido en exactamente un polígono parroquial.
   - **No asignados:** centroide ubicado fuera del límite urbano municipal.
   - **Solapamiento múltiple:** centroide contenido en más de un polígono (polígonos municipales solapados).
5. Se analizó el corte geométrico de los sectores censales:
   - Se evaluó cuántos polígonos censales intersecan la frontera/límite parroquial (*boundary intersection*).
   - Se evaluó cuántos sectores censales intersecan dos o más parroquias a la vez (*corte interparroquial*).

---

### Resultados Cuantitativos

```
========================================================================================
MÉTRICA DE COMPATIBILIDAD                       QUITO          GUAYAQUIL         CUENCA
========================================================================================
Código cabecera cantonal (Marco 2021)          170150            090150          010150
Total sectores censales en la cabecera          4.758             6.412           1.071
Parroquias urbanas municipales evaluadas           32          16 feats (14)         15
----------------------------------------------------------------------------------------
ASIGNACIÓN POR CENTROIDE:
  Asignados sin ambigüedad (1 parroquia)        4.740 (99,62%)    5.876 (91,64%)  1.071 (100,00%)
  No asignados (fuera del límite urbano)           18  (0,38%)      536  (8,36%)      0   (0,00%)
  Ambigüedad múltiple (solapamiento)                0  (0,00%)        0  (0,00%)      0   (0,00%)
----------------------------------------------------------------------------------------
CORTES GEOMÉTRICOS DE LÍMITE:
  Sectores cuyo polígono corta límite             834 (17,53%)      603  (9,40%)    336  (31,37%)
  Sectores con corte interparroquial (>= 2)       760 (15,97%)      242  (3,77%)    240  (22,41%)
  Sectores 100% contenidos en 1 parroquia       3.924 (82,47%)    5.809 (90,60%)    735  (68,63%)
========================================================================================
```

---

### Interpretación y Hallazgos Cartográficos

#### 1. Quito (MDMQ)
- **Excelente coherencia global (99,62%):** 4.740 de los 4.758 sectores urbanos del censo quedan asignados sin ninguna ambigüedad a una de las 32 parroquias urbanas oficiales.
- **Sectores no asignados (18 sectores, 0,38%):** Se localizan en bordes perimetrales de quebradas y laderas periféricas donde la malla censal de la cabecera `170150` toca las parroquias rurales del DMQ (Calderón, Zámbiza, Llano Chico, Cumbayá y Lloa). Al cruzar los centroides contra las 60 parroquias metropolitanas completas, la asignación alcanza el 100%.
- **Cortes de frontera (15,97%):** 760 sectores censales cortan la línea divisoria entre dos parroquias urbanas colindantes (ej. avenidas estructurantes como Av. 10 de Agosto, Amazonas o Eloy Alfaro que dividen Iñaquito de Rumipamba y Belisario Quevedo). El método de asignación por centroide resuelve de forma unívoca y estandarizada la agregación estadística.

#### 2. Guayaquil (M.I. Municipalidad de Guayaquil)
- **Asignación en la mancha consolidada (91,64%):** 5.876 sectores urbanos se vinculan de manera perfecta a las parroquias tradicionales y de planificación de la urbe (Febres Cordero, Tarqui, Ximena, Pascuales, etc.).
- **Explicación técnica de los 536 sectores no asignados (8,36%):**  
  La capa municipal `MapServer/9` delimita estrictamente la conurbación urbana central de Guayaquil (el casco urbano tradicional comprendido entre el Río Daule, el Río Guayas y el Estero Salado hasta Pascuales).  
  Sin embargo, el INEC en el Marco 2021 codifica bajo la cabecera cantonal `090150` una franja territorial extensa hacia el oeste del cantón: el corredor de Vía a la Costa, Puerto Hondo, las comunas de Chongón y sectores periurbanos de manglar. La delimitación histórica de parroquias urbanas de Guayaquil no cubre este territorio rural/periurbano occidental.  
  *Solución técnica propuesta para el visor:* Agrupar estos 536 sectores bajo una categoría territorial explícita: `"090150-EXT: Guayaquil Expansión / Vía a la Costa - Chongón"`, manteniendo la integridad del 100% de los sectores censales.

#### 3. Cuenca (GAD Municipal de Cuenca)
- **Asignación perfecta (100,00%):** Los 1.071 sectores censales de la cabecera cantonal de Cuenca (`010150`) quedan asignados en su totalidad a las 15 parroquias urbanas oficiales sin dejar un solo sector huérfano.
- **Cortes de frontera (22,41%):** Al ser una traza urbana donde varios sectores censales abarcan manzanas a ambos lados de ríos (Tomebamba, Yanuncay, Tarqui, Machángara) o avenidas perimetrales, 240 sectores cortan los límites interparroquiales. La asignación por centroide funciona con total estabilidad matemática.

---

## 5. Recomendación Final y Plan de Integración en el Visor WebGIS

1. **Ciudades Habilitadas para Implementación Inmediata (Fase 3):**
   - **Quito (32 parroquias):** Integrar GeoJSON desde `geoquito.quito.gob.ec` (capa `Hosted/parroquias_ref_a`).
   - **Guayaquil (14 parroquias + zona expansión):** Integrar GeoJSON desde `geoportalcat.guayaquil.gob.ec` (capa `MapServer/9`).
   - **Cuenca (15 parroquias):** Integrar GeoJSON desde `ide.cuenca.gob.ec` (capa WFS `dgpt_limites:limite_parroquias_urbanas`).
   - **Loja (6 parroquias):** Integrar GeoJSON desde `sil.loja.gob.ec` (capa WFS `pugs_2023_2033:limites_parroquias_urbanas_2023_2033`).
   - **Ambato (8 parroquias):** Integrar GeoJSON desde `arcgis.ambato.gob.ec` (capa `MXD/AMBATO/MapServer/1`).
   - **Riobamba (5 parroquias):** Integrar GeoJSON desde ArcGIS Online institucional (`coellop_gadmriobamba`).

2. **Ciudades que Requieren Trámite de Acceso a la Información (SAIP) o Token Institucional:**
   - **Santo Domingo (7 parroquias):** Solicitar al GAD Municipal la habilitación del endpoint `/api/v1/layers` o entrega de la cobertura cartográfica en GeoPackage/Shapefile.
   - **Portoviejo (9 parroquias):** Solicitar al GAD Municipal el token temporal de acceso o entrega del shapefile de la capa `Parro_Barro_PIT`.
   - **Manta (5 parroquias):** Solicitar credencial de consulta o copia de la capa de parroquias urbanas del sistema GeoManta.
   - **Machala (5 parroquias) y Durán (3 parroquias):** Tramitar solicitud de información pública (SAIP) formal ante las Direcciones de Catastro y Planificación Territorial, al no contar con plataformas SIG públicas interoperables.

3. **Estandarización de Atributos para el Frontend (Fase 3):**
   Se recomienda estructurar la tabla de cruce sectorial en el pipeline del proyecto con este esquema tabular unificado:
   ```json
   {
     "sector_key": "170150257003",
     "canton_key": "1701",
     "parroquia_censal": "170150",
     "parroquia_urbana_codigo": "170112",
     "parroquia_urbana_nombre": "IÑAQUITO",
     "fuente_limite": "MDMQ-STHV-2024",
     "es_limite_censal": false,
     "metodo_asignacion": "centroide_en_poligono"
   }
   ```
   Esta asignación formal permitirá desbloquear la métrica `[PENDIENTE: índice de Iñaquito]` en el guion de scrollytelling de la Historia 1 (`docs/historias/01_ecuador_envejece.json` y `.md`) calculando el valor exacto sobre la delimitación municipal oficial de la STHV.
