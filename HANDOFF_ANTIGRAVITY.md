# Handoff Antigravity: Auditoría, Guiones de Historias, Fuentes Urbanas y Solicitudes LOTAIP

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

### 1.3 Fuentes Oficiales de Parroquias Urbanas y Compatibilidad Espacial (PR #56, rama `feat/fuentes-parroquias-urbanas`)
- Documento entregable: `docs/fuentes/parroquias_urbanas.md`.
- **Competencias normativas:** Distinción clara entre CONALI (parroquias rurales y cantones) y GAD Municipales (parroquias urbanas internas, COOTAD Arts. 54 y 57).
- **Auditoría técnica en 12 ciudades:**
  - **Habilitadas con descarga abierta directa:** Quito (32 urbanas), Guayaquil (14 urbanas), Cuenca (15 urbanas), Loja (6 urbanas), Ambato (8 urbanas) y Riobamba (5 urbanas).
  - **Fuente académica externa:** Ibarra (UTN GIS; geoportal municipal inactivo con HTTP 410 Gone, excluida del lanzamiento).
  - **Restringidas / privadas:** Santo Domingo (API 401), Portoviejo (Token 499), Manta (Login requerido), Machala y Durán (sin servidor SIG web).
- **Pruebas espaciales a nivel de manzana (`man_a` Marco 2021):**
  - Quito: 99,89% de manzanas y 99,84% de población asignada unívocamente; solo 3,10% de población en manzanas cortadas.
  - Guayaquil: 89,40% de manzanas y 93,11% de población en la mancha urbana consolidada; remanente de 3.241 manzanas hacia el oeste catalogado como *"Cabecera Guayaquil · fuera de las parroquias urbanas municipales"* sin crear unidades artificiales.
  - Cuenca: 99,95% de manzanas y 99,94% de población asignada; solo 2,24% en manzanas cortadas (riberas de ríos).

---

## 2. Fase Actual: Solicitudes de Acceso a la Información Pública (LOTAIP 2023)

**Rama:** `feat/saip-parroquias`  
**Directorio de entrega:** `docs/fuentes/saip/`  
**Estado:** Documentación formal completa, lista para firma y radicación en ventanilla/correo institucional; PR en borrador hacia `main`.

### 2.1 Marco Normativo Verificado
Las 5 solicitudes fueron estructuradas bajo la legislación vigente de la República del Ecuador:
1. **Constitución de la República del Ecuador (CRE):**
   - Art. 18 numeral 2 (derecho al libre acceso a la información pública sin reserva arbitraria).
   - Art. 61 numeral 2 (derecho ciudadano a participar en asuntos de interés público).
   - Art. 227 (principios de eficacia, transparencia y rendición de cuentas en la administración).
2. **Ley Orgánica de Transparencia y Acceso a la Información Pública (LOTAIP):**
   - Publicada en el **Segundo Suplemento del Registro Oficial No. 245, de 7 de febrero de 2023** (vigente; derogatoria de la anterior ley de 2004).
   - **Art. 1:** Objeto de la ley y tutela efectiva del derecho.
   - **Art. 3 lit. b):** Aplicación obligatoria para los GAD cantonales como sujetos obligados.
   - **Art. 4:** Principios de máxima publicidad, gratuidad, formatos abiertos y el principio *in dubio pro petitor*.
   - **Arts. 30, 31 y 33:** Requisitos mínimos, presentación por canales electrónicos y entrega en formatos digitales abiertos sin costo para el solicitante.
   - **Art. 34:** Plazo perentorio de contestación de **diez (10) días hábiles**, con prórroga máxima de **cinco (5) días hábiles adicionales** previa justificación notificada formalmente al solicitante.
   - **Art. 35:** Obligación de entregar la información que obre o deba obrar en custodia de la entidad.
   - **Arts. 36 y 37:** Silencio administrativo como denegación tácita sancionable, habilitando la Acción Constitucional de Acceso a la Información Pública (CRE Art. 91).
3. **Código Orgánico de Organización Territorial, Autonomía y Descentralización (COOTAD):**
   - Arts. 54 y 55 lit. a: Competencia exclusiva municipal de planificación territorial y regulación del uso del suelo.
   - Art. 57 lit. x: Atribución exclusiva del Concejo Cantonal para determinar mediante ordenanza la delimitación y división cantonal en parroquias urbanas.

---

### 2.2 Matriz de Solicitudes Formales Preparadas

Se generaron 5 solicitudes formales completas, personalizadas con la autoridad competente de cada GAD, el estado técnico detectado en la auditoría y los canales oficiales de radicación:

| Municipio / Cantón | Autoridad Máxima y Dirección Técnica | Estado Cartográfico Previo | Archivo Generado | Canal Oficial de Envío / Ventanilla |
|---|---|---|---|---|
| **Santo Domingo** | - **Ing. Wilson Erazo Argoti** (Alcalde)<br>- **Arq. Darwin Edmundo Aldaz** (Dir. Planificación y Proyectos)<br>- Dirección de Avalúos y Catastros | Geoportal activo; API REST `/api/v1/layers` restringida con **HTTP 401 Unauthorized**. | [`docs/fuentes/saip/santo_domingo.md`](file:///docs/fuentes/saip/santo_domingo.md) | - Ventanilla Única Virtual: `https://www.santodomingo.gob.ec/`<br>- Correos: `contacto@santodomingo.gob.ec`, `alcaldia@santodomingo.gob.ec` |
| **Portoviejo** | - **Ab. Javier Pincay Salvatierra** (Alcalde)<br>- **Simón García** (Dir. Cantonal Desarrollo Territorial)<br>- **Arq. Johan Pérez Bernal** (Dir. Gestión Urbanística y Catastro) | Geoportal Fénix activo; FeatureServer `Parro_Barro_PIT` bloqueado con **Error 499 (Token Required)**. | [`docs/fuentes/saip/portoviejo.md`](file:///docs/fuentes/saip/portoviejo.md) | - Ventanilla Digital: `https://www.portoviejo.gob.ec` / `https://tramites.portoviejo.gob.ec`<br>- Correos: `secretariageneral@portoviejo.gob.ec`, `alcaldia@portoviejo.gob.ec` |
| **Manta** | - **Lcda. Marciana Valdivieso Zamora** (Alcaldesa)<br>- **Lex Vera** (Dir. Planificación y Ordenamiento Territorial)<br>- Dirección de Avalúos y Catastros | Plataforma GeoManta activa pero con **Login Administrativo Obligatorio** (acceso cerrado). | [`docs/fuentes/saip/manta.md`](file:///docs/fuentes/saip/manta.md) | - Portal Ciudadano / Ventanilla: `https://manta.gob.ec`<br>- Correos: `atencionciudadana@manta.gob.ec`, `alcaldia@manta.gob.ec` |
| **Machala** | - **Ing. Darío Macas Salvatierra** (Alcalde)<br>- **Arq. Xavier Reyes Pacheco** (Dir. Urbanismo)<br>- **Ab. Vanessa Torres** (Dir. Planificación)<br>- Subdirección de Catastro | **Sin geoservidor web público** (`geoportal.machala.gob.ec` sin DNS). Datos custodiados internamente. | [`docs/fuentes/saip/machala.md`](file:///docs/fuentes/saip/machala.md) | - Portal de Trámites: `https://www.machala.gob.ec`<br>- Correos: `info@machala.gob.ec`, `secretariageneral@machala.gob.ec` |
| **Durán** | - **Ing. Luis Chonillo Breilh** (Alcalde)<br>- **[NOMBRE DE LA AUTORIDAD]** (Dir. Gral. Planeamiento, Ordenamiento y Terrenos)<br>- Dirección General de Avalúos y Catastros | **Sin geoservidor web público** (`geoportal.duran.gob.ec` sin DNS). Datos custodiados internamente. | [`docs/fuentes/saip/duran.md`](file:///docs/fuentes/saip/duran.md) | - Ventanilla Digital: `https://www.duran.gob.ec`<br>- Correos: `secretariageneral@duran.gob.ec`, `alcaldia@duran.gob.ec` |

---

### 2.3 Contenido Estandarizado de Cada Solicitud
Cada uno de los 5 documentos incorpora:
1. **Encabezado institucional formal:** Número de oficio referencial, fecha, autoridades destinatarias debidamente jerarquizadas.
2. **Identificación legal del solicitante:** Comparecencia formal de la **Fundación REDSA**, representada legalmente por `[NOMBRE DEL REPRESENTANTE]`, señalando RUC, domicilio legal y casillero electrónico para notificaciones.
3. **Fundamentación jurídica rigurosa:** Citas directas y concordadas de la CRE (Arts. 18.2, 61.2, 227), LOTAIP 2023 (Segundo Suplemento RO No. 245, Arts. 1, 3.b, 4, 30, 31, 33, 34, 35, 36, 37) y COOTAD (Arts. 54, 55.a, 57.x).
4. **Petición concreta de información técnica:**
   - Capa poligonal vectorial en formatos interoperables abiertos (**GeoPackage, Shapefile o GeoJSON**).
   - Sistema de Referencia de Coordenadas (**WGS 84 / UTM Zona 17 Sur, EPSG:32717** o WGS 84 geográfico).
   - Diccionario de datos y metadatos técnicos mínimos (nombres oficiales, códigos parroquiales, superficies).
   - Copia de la **Ordenanza Cantonal de delimitación parroquial vigente**, con fecha de sanción y vigencia.
5. **Finalidad pública y compromiso de atribución institucional:** Explicación del proyecto cívico y de ciencia abierta sin fines de lucro **"Censo Vivo Ecuador"**, comprometiendo la mención destacada y atribución técnica oficial en favor de cada GAD Municipal.
6. **Vía digital de entrega:** Solicitud expresa de remisión telemática directa sin costo alguno.
7. **Tabla resumen de plazos legales de respuesta.**
8. **Pie de firma formal.**

---

### 2.4 Tabla Consolidada de Plazos Legales y Consecuencias Jurídicas

Todas las solicitudes notifican a los GAD el régimen legal de plazos previsto en el Art. 34 de la LOTAIP 2023:

```
=============================================================================================================
HITO / ACTUACIÓN                         BASE LEGAL         TÉRMINO LEGAL       CONSECUENCIA JURÍDICA
=============================================================================================================
Recepción e ingreso de solicitud         LOTAIP Art. 30     Inmediato (Día 0)   Asignación de número de trámite
                                                                                y fe de recepción digital.
-------------------------------------------------------------------------------------------------------------
Respuesta ordinaria y entrega de datos   LOTAIP Art. 34     10 días hábiles     Obligación de entregar la capa
                                                                                vectorial y ordenanza.
-------------------------------------------------------------------------------------------------------------
Prórroga excepcional justificada         LOTAIP Art. 34     +5 días hábiles     Solo procede si la entidad
                                                            (máx. 15 hábiles)   notifica formalmente la causa
                                                                                antes del vencimiento del día 10.
-------------------------------------------------------------------------------------------------------------
Vencimiento / Silencio administrativo    LOTAIP Arts. 36-37 Término perentorio  Configuración de denegación tácita.
                                         CRE Art. 91                            Habilita recurso de corrección y
                                                                                Acción Constitucional de Acceso a
                                                                                la Información Pública ante jueces.
=============================================================================================================
```

---

### 2.5 Protocolo Operativo para la Radicación y Seguimiento
1. **Firma y Completitud de Campos:**
   - Reemplazar los marcadores entre corchetes (`[NOMBRE DEL REPRESENTANTE]`, `[NÚMERO DE IDENTIFICACIÓN]`, `[NÚMERO DE RUC DE FUNDACIÓN REDSA]`, `[DIRECCIÓN DOMICILIARIA REDSA]`, `[CORREO INSTITUCIONAL REDSA]`, `[TELÉFONO DE CONTACTO]`).
   - Aplicar firma electrónica digital válida en Ecuador (ej. BCE, Security Data, Consejo de la Judicatura) sobre el archivo PDF generado.
2. **Ingreso Telemático:**
   - Radicar prioritariamente por la Ventanilla Única Virtual de cada GAD.
   - Enviar copia simultánea con fe de presentación a los correos de Secretaría General y Alcaldía de cada municipio.
3. **Custodia de Fe de Recepción y Control de Calendario:**
   - Registrar la fecha exacta de confirmación de recepción (Día 0).
   - Iniciar el cómputo de los 10 días hábiles (excluyendo fines de semana y feriados nacionales o locales).
   - Si transcurridos 8 días no se recibe respuesta, enviar oficio de insistencia preventiva.
   - En caso de silencio administrativo al término del día 10 (o 15 en caso de prórroga), iniciar la Acción Constitucional de Acceso a la Información Pública conforme al Art. 91 de la CRE.

---
*Fin del Handoff.*
