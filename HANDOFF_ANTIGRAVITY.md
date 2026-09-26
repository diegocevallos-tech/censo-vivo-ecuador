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
7. **Ibarra (5 urbanas):** Repositorio UTN GIS / Convenio GAD Ibarra (`services5.arcgis.com/.../PARROQUIAS_IBARRA/FeatureServer/0`). El geoportal directo del GAD Ibarra responde HTTP 410 Gone. **Capa alternativa activa**.
8. **Santo Domingo (7 urbanas):** Geoportal activo (`geoportal.santodomingo.gob.ec`), pero su API REST `/api/v1/layers` exige autenticación (HTTP 401 Unauthorized). **Restringido**.
9. **Portoviejo (9 urbanas):** Geoportal Fénix / Portoviejo 2035 activo en visor web, pero su FeatureServer (`Parro_Barro_PIT`) exige token privado (Error 499). **Restringido**.
10. **Manta (5 urbanas):** Plataforma GeoManta (`geoportal.manta.gob.ec`) bajo autenticación obligatoria (Login AdminLTE). **Restringido**.
11. **Durán (3 urbanas) y Machala (5 urbanas):** Sin plataformas de datos espaciales públicas ni servicios WFS/REST. **Sin cobertura SIG web**.

### 2.3 Pruebas Espaciales de Compatibilidad con el Marco Geoestadístico 2021 (`sec_a`)
Se descargaron las capas poligonales oficiales de Quito, Guayaquil y Cuenca y se cruzaron contra los sectores censales del Marco 2021 del INEC (`sec_a`, EPSG:32717 UTM 17S):

| Ciudad | Cabecera Censal | Sectores Censales Totales | Parroquias Evaluadas | Asignación por Centroide Sin Ambigüedad | Fuera de Límite Urbano | Cortes de Límite (Polígono) | Cortes Interparroquiales (>=2) | 100% Contenidos en 1 Parroquia |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Quito** | `170150` | 4.758 | 32 urbanas | **4.740 (99,62%)** | 18 (0,38%) | 834 (17,53%) | 760 (15,97%) | 3.924 (82,47%) |
| **Guayaquil** | `090150` | 6.412 | 16 polígonos | **5.876 (91,64%)** | 536 (8,36%) | 603 (9,40%) | 242 (3,77%) | 5.809 (90,60%) |
| **Cuenca** | `010150` | 1.071 | 15 urbanas | **1.071 (100,00%)** | 0 (0,00%) | 336 (31,37%) | 240 (22,41%) | 735 (68,63%) |

**Observaciones cartográficas clave:**
- **Quito (99,62%):** Los 18 sectores censales no asignados corresponden a zonas de contacto periférico con parroquias rurales del DMQ (Calderón, Zámbiza, Llano Chico, Cumbayá y Lloa). Al evaluar contra las 60 parroquias del DMQ, la cobertura es del 100%.
- **Guayaquil (91,64%):** Los 536 sectores no cubiertos obedecen a que la delimitación municipal cubre la mancha consolidada tradicional, mientras que el código censal `090150` del INEC abarca hacia el oeste todo el corredor de Vía a la Costa, Puerto Hondo y Chongón. Se recomienda categorizar este remanente como *"090150-EXT: Guayaquil Expansión / Vía a la Costa - Chongón"*.
- **Cuenca (100,00%):** Coincidencia perfecta de los 1.071 sectores censales urbanos.

### 2.4 Hoja de Ruta de Implementación
1. **Inmediatas (Fase 3):** Quito, Guayaquil, Cuenca, Loja, Ambato y Riobamba.
2. **Con Fuente Alternativa:** Ibarra (vía UTN GIS).
3. **Pendientes de Trámite SAIP / Token:** Santo Domingo, Portoviejo, Manta, Machala y Durán.
4. **Desbloqueo de Scrollytelling:** Con la capa oficial de la STHV de Quito integrada, se podrá calcular el índice exacto de Iñaquito (`170112`) y sustituir la marca `[PENDIENTE]` en la Historia 1.

---
*Fin del Handoff.*
