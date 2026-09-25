# HANDOFF ANTIGRAVITY - Fase 1B: Guiones de Historias Guiadas (Scrollytelling) - Revisión Editorial

**Fecha:** 25 de septiembre de 2026  
**Rama:** `feat/historias-guion`  
**PR:** Draft PR #47  
**Estado:** Completado tras revisión editorial estricta  

---

## 1. Cumplimiento de Reglas Editoriales

Se aplicaron rigurosamente las 7 reglas editoriales acordadas sobre los guiones de scrollytelling en `docs/historias/`:

1. **Hecho vs Hipótesis:**
   - Todo el cuerpo narrativo afirma exclusivamente lo que surge de los conteos censales del CPV 2022.
   - Las interpretaciones contextuales o causales (precio del suelo, dinámicas de remesas, redes de telecomunicaciones) se aislaron en un recuadro formal `> **Hipótesis:** ... (el censo no lo mide)` con enlace a fuente externa especializada (BID, OIM, FLACSO, ARCOTEL). Máximo una hipótesis por historia.
2. **Misma Escala:**
   - Comparación estricta entre unidades del mismo nivel: nacional con nacional, cantón con cantón, parroquia con parroquia y sector con sector censal.
   - Envejecimiento: se comparan parroquias rurales de Chimborazo (Palmira `060354`, San Juan `060154`) y Loja (Olmedo `111550`) con parroquias rurales de Pichincha (Calderón `170152`), y sectores censales urbanos consolidados de Iñaquito (`170150...`) con sectores rurales.
   - Se eliminaron expresiones no censales ("10 km al norte", "15 minutos").
3. **Mismos Denominadores:**
   - En la brecha digital, se compara hogares con hogares: porcentaje de hogares con servicio de teléfono celular (`H1002=1`, 86,98% nacional) frente a porcentaje de hogares con internet fijo domiciliario (`H1004=1`, 60,89% nacional), ambos sobre el universo homogéneo de **5.188.827 hogares clasificados**.
   - En cantones como Paján (Manabí) y El Empalme (Guayas), la brecha entre ambos servicios supera los 50 puntos porcentuales.
   - Se utilizan únicamente nombres de cantones y parroquias oficiales.
4. **Definiciones del Catálogo:**
   - Cada indicador cita la fórmula e identificador exacto de `indicators.yaml`: `aging_index`, `emigrant_households`, `male_ratio`, `vacant_private_dwellings`, `fixed_internet`, `digital_exclusion`.
   - "Ciudad vacía" utiliza la definición estricta del catálogo (`V0201=4 / V0201 en 1..5`, 11,63% nacional, Cañar 26,41%, Suscal 23,12%).
   - Se documentó en `docs/historias/README.md` la propuesta de variante `unoccupied_dwellings` (que suma las viviendas temporales `V0201=3` para balnearios y cantones migratorios) sin alterar el catálogo actual.
5. **Tabla de Emigración por Sexo y Edad:**
   - En la historia 2 se incluyó el Paso 4 con la tabla de emigrantes por sexo, edad de salida y país de destino para Santa Isabel (`0109`) y Biblián (`0303`), marcado formalmente como `[PENDIENTE: agregado de Emigración por cantón × sexo × edad de salida × país de destino]` para que Codex genere el agregado aditivo a partir de la sección Emigración (variables E01-E04).
6. **Tono Sobrio y Divulgativo:**
   - Textos redactados entre **40 y 70 palabras** en español llano y accesible.
   - Se erradicaron términos sensacionalistas ("amputación", "mansiones con candado", "sobreviven", "esquizofrenia", "desangran").
7. **Verificación Numérica:**
   - Se redactó `docs/historias/verificacion.md` con la tabla exhaustiva de cada cifra citada, su consulta SQL reproducible en DuckDB, el resultado exacto y el contraste con publicaciones oficiales del INEC.

---

## 2. Los 4 Giros Contraintuitivos

| Historia | Creencia Popular Común | Giro Contraintuitivo Comprobado con Datos Censales |
|---|---|---|
| **1. El Ecuador que envejece** | El envejecimiento es exclusivo de aldeas campesinas aisladas. | **La vejez en sectores urbanos consolidados:** En sectores urbanos de Iñaquito (Quito), el índice de envejecimiento supera los 135 adultos mayores por cada 100 niños, contrastando con la parroquia rural Calderón (35,88) en el mismo cantón. |
| **2. Los que se fueron** | La emigración traslada a familias de forma homogénea entre ambos sexos. | **La asimetría de género en edades productivas:** En cantones del Austro como Santa Isabel (Azuay), la razón de masculinidad entre 20 y 39 años desciende a 69,99 varones por cada 100 mujeres residentes. |
| **3. La ciudad vacía** | Las casas vacías son chozas rurales en ruinas o se concentran solo en playas. | **El récord andino de desocupación habitacional:** Bajo la definición oficial del catálogo (`V0201=4`), las mayores tasas cantonales se registran en Cañar (26,41%) y Suscal (23,12%), mientras en el noroeste de Guayaquil el hacinamiento supera el 40%. |
| **4. La brecha digital** | El teléfono celular resolvió la brecha de conectividad de los hogares. | **La brecha entre teléfono celular y red fija en el hogar:** Sobre el mismo universo de hogares, en cantones como Paján (Manabí) y El Empalme (Guayas), más del 80% al 87% de los hogares dispone de celular, pero solo entre el 22% y el 36% tiene internet fijo domiciliario (brecha > 50 puntos). |

---

## 3. Estado de Entrega

- Rama: `feat/historias-guion`
- PR: Draft PR #47 (mantenido en borrador según solicitud)
- Archivos en PR:
  - `docs/historias/01_ecuador_envejece.md`
  - `docs/historias/01_ecuador_envejece.json`
  - `docs/historias/02_los_que_se_fueron.md`
  - `docs/historias/02_los_que_se_fueron.json`
  - `docs/historias/03_ciudad_vacia.md`
  - `docs/historias/03_ciudad_vacia.json`
  - `docs/historias/04_brecha_digital.md`
  - `docs/historias/04_brecha_digital.json`
  - `docs/historias/README.md`
  - `docs/historias/verificacion.md`
  - `HANDOFF_ANTIGRAVITY.md`

---
*Fin del Handoff.*
