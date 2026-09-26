# Handoff Antigravity: Auditoría, Guiones de Historias y Fuentes de Parroquias Urbanas

Este documento resume las tareas desarrolladas de forma autónoma e independiente por Antigravity en el repositorio `diegocevallos-tech/censo-vivo-ecuador`.

---

## 1. Historial de Fases Previas

### 1.1 Auditoría Independiente Fase 1B-2 (PR #45)
- Auditoría cuantitativa completa de las salidas analíticas de Codex: Moran's I, LISA, clústeres geodemográficos K-Means y validación censal INEC.
- Registro detallado en `docs/analitica.md` y `docs/qa/validacion_inec.md`.

### 1.2 Guiones de Scrollytelling (PR #47, rama `feat/historias-guion`)
- Guiones de las 4 historias guiadas: "El Ecuador que envejece", "Los que se fueron", "La ciudad vacía" y "La brecha digital".
- Especificaciones de estados de mapa en JSON, consultas reproducibles DuckDB y textos estrictamente redactados entre 40 y 70 palabras.
- Verificación exhaustiva de fuentes externas (CEPAL, BCE, ARCOTEL) y auditoría numérica documentada en `docs/historias/verificacion.md`.
- El indicador de Iñaquito se mantuvo como `[PENDIENTE: índice de Iñaquito con la capa de parroquias urbanas del visor]` a la espera de la delimitación municipal oficial.

---

## 2. Fase Actual: Fuentes Oficiales de Parroquias Urbanas y Compatibilidad Espacial

**Rama:** `feat/fuentes-parroquias-urbanas`  
**Documento entregable:** `docs/fuentes/parroquias_urbanas.md`  
**Estado:** PR en borrador hacia `main`.

### 2.1 Marco Normativo y Competencias
1. **Límites Nacionales / Cantonales / Parroquias Rurales:**  
   Competencia del Comité Nacional de Límites Internos (**CONALI**) (COOTAD, Arts. 55 y 57). Su catálogo oficial registra 1.053 circunscripciones (222 cabeceras cantonales y 831 parroquias rurales). El censo nacional (CPV 2022) y el Marco Geoestadístico 2021 agregan toda la urbe bajo la cabecera cantonal (`XXYY50`).
2. **Límites de Parroquias Urbanas Internas:**  
   Competencia exclusiva de los **GAD Municipales** vía ordenanza cantonal (COOTAD, Arts. 54 y 57). No existe una capa nacional unificada ni del CONALI ni del INEC. Por tanto, toda capa integrada al visor proviene de fuentes municipales y debe rotularse como *"Fuente oficial municipal; límite no censal"*.

### 2.2 Auditoría de Fuentes en las 12 Principales Ciudades
Se auditaron las 10 cabeceras cantonales más pobladas del país más Riobamba e Ibarra:
1. **Quito (32 urbanas):** MDMQ - STHV / DMIT. Servicio ArcGIS REST FeatureServer (`geoquito.quito.gob.ec/server/rest/services/Hosted/parroquias_ref_a/FeatureServer/0`). **Operacional (200 OK)**.
2. **Guayaquil (14-16 urbanas):** M.I. Municipalidad de Guayaquil - DUMDYT. Servicio ArcGIS REST MapServer (`geoportalcat.guayaquil.gob.ec/.../MapServer/9`). **Operacional (200 OK)**.
3. **Cuenca (15 urbanas):** GAD Municipal de Cuenca - DGPT / IDE Cuenca. Servicio OGC WFS GeoServer (`ide.cuenca.gob.ec/geoserver/wfs`, capa `dgpt_limites:limite_parroquias_urbanas`). **Operacional (200 OK)**.
4. **Loja (6 urbanas):** GAD Municipal de Loja - Planificación / SIL. Servicio OGC WFS GeoServer (`sil.loja.gob.ec/geoserver/wfs`, capa `pugs_2023_2033:limites_parroquias_urbanas_2023_2033`). **Operacional (200 OK)**.
5. **Ambato (8 urbanas):** GAD Municipalidad de Ambato - Catastros / SIG. Servicio ArcGIS REST MapServer (`arcgis.ambato.gob.ec/mapas/.../MapServer/1`). **Operacional (200 OK)**.
6. **Riobamba (5 urbanas):** GAD Municipal de Riobamba - Planificación. ArcGIS Online institucional (`services9.arcgis.com/.../parroquias_urbanas/FeatureServer/0`). **Operacional (200 OK)**.
7. **Ibarra (5 urbanas):** Repositorio UTN GIS (Universidad Técnica del Norte / Centro SIG). Catalogada como **fuente académica, no municipal**. Geoportal directo del GAD Ibarra responde HTTP 410 Gone. **Excluida de la recomendación de lanzamiento**.
8. **Santo Domingo (7 urbanas):** Geoportal activo (`geoportal.santodomingo.gob.ec`), pero su API REST `/api/v1/layers` exige autenticación (HTTP 401 Unauthorized). **Restringido**.
9. **Portoviejo (9 urbanas):** Geoportal Fénix / Portoviejo 2035 activo en visor web, pero su FeatureServer (`Parro_Barro_PIT`) exige token privado (Error 499). **Restringido**.
10. **Manta (5 urbanas):** Plataforma GeoManta (`geoportal.manta.gob.ec`) bajo autenticación obligatoria (Login AdminLTE). **Restringido**.
11. **Durán (3 urbanas) y Machala (5 urbanas):** Sin plataformas de datos espaciales públicas ni servicios WFS/REST. **Sin cobertura SIG web**.

### 2.3 Pruebas Espaciales de Compatibilidad a Nivel Manzana (`man_a`)
Se descargaron las capas poligonales oficiales de Quito, Guayaquil y Cuenca y se cruzaron contra las manzanas cartográficas del Marco 2021 del INEC (`man_a`, EPSG:32717 UTM 17S), vinculando la población censal oficial (`finest/*.parquet`):

| Ciudad | Cabecera Censal | Manzanas Cartográficas (`man_a`) | Población Vinculada | Manzanas Asignadas por Centroide | Población Asignada | Manzanas Fuera de Parroquias Urbanas | Población Fuera de Parroquias Urbanas | Manzanas Cortadas por Límite | Población en Manzanas Cortadas | Manzanas 100% Contenidas |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Quito** | `170150` | 16.907 | 1.766.196 hab | **16.888 (99,89%)** | **1.763.309 (99,84%)** | 19 (0,11%) | 2.887 (0,16%) | 310 (1,83%) | **54.835 (3,10%)** | 16.597 (98,17%) |
| **Guayaquil** | `090150` | 30.580 | 2.653.650 hab | **27.339 (89,40%)** | **2.470.928 (93,11%)** | 3.241 (10,60%) | 182.722 (6,89%) | 467 (1,53%) | **65.404 (2,46%)** | 30.113 (98,47%) |
| **Cuenca** | `010150` | 4.049 | 360.359 hab | **4.047 (99,95%)** | **360.150 (99,94%)** | 2 (0,05%) | 209 (0,06%) | 147 (3,63%) | **8.068 (2,24%)** | 3.902 (96,37%) |

**Observaciones cartográficas clave:**
- **Quito (99,89% manzanas, 99,84% población):** Asignación prácticamente perfecta. Solo el 3,10% de la población (54.835 hab en 310 manzanas) habita en manzanas que tocan algún límite interparroquial. El 98,17% de las manzanas está 100% contenido en su parroquia.
- **Guayaquil (89,40% manzanas, 93,11% población):** El casco urbano consolidado muestra una coincidencia limpia. Solo el 2,46% de la población (65.404 hab en 467 manzanas) vive en manzanas cortadas por límites. Las 3.241 manzanas no cubiertas (182.722 habitantes hacia el oeste en Vía a la Costa, Chongón y manglares) quedan clasificadas como *"Cabecera Guayaquil · fuera de las parroquias urbanas municipales"*, sin crear ninguna unidad nueva.
- **Cuenca (99,95% manzanas, 99,94% población):** Asignación unívoca total. Solo el 2,24% de la población (8.068 hab en 147 manzanas ribereñas) reside en manzanas cortadas por límites.

### 2.4 Hoja de Ruta de Implementación
1. **Lanzamiento Inmediato (Fase 3):**  
   Implementar las 6 ciudades con servicios oficiales municipales abiertos y verificados: **Quito, Guayaquil, Cuenca, Loja, Ambato y Riobamba**.
2. **Excluidas del Lanzamiento:**  
   - **Ibarra:** Fuente académica (UTN GIS), no municipal; excluida hasta validación oficial del GAD.
   - **Santo Domingo, Portoviejo y Manta:** Servicios protegidos por autenticación/token; requieren trámite formal ante el GAD.
   - **Machala y Durán:** Sin servicios SIG en línea; requieren solicitud SAIP a Catastro.
3. **Desbloqueo de Scrollytelling:**  
   Con la capa de la STHV de Quito (`Hosted/parroquias_ref_a`), se desbloquea el cálculo exacto del índice de **Iñaquito (170112)** para cerrar el Paso 5 de la Historia 1.

---
*Fin del Handoff.*
