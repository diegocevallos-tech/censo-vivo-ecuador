# HANDOFF ANTIGRAVITY - Fase 1B: Guiones de Historias Guiadas (Scrollytelling)

**Fecha:** 25 de septiembre de 2026  
**Rama:** `feat/historias-guion`  
**Estado:** Completado / Listo para revisión en Pull Request  

---

## 1. Entregables Realizados

Se redactaron y especificaron técnica y narrativamente los **4 guiones de historias interactivas guiadas (scrollytelling)** para el portal WebGIS Censo Vivo Ecuador, ubicados en `docs/historias/`:

1. **"El Ecuador que envejece"** (`01_ecuador_envejece.md` / `01_ecuador_envejece.json`): 7 pasos sobre la transición demográfica, desde la Amazonía joven (Taisha, envejecimiento 5,15) hasta la inversión generacional andina (Olmedo, 103,98; Palmira, 226,22) y el enclave metropolitano de alta plusvalía.
2. **"Los que se fueron"** (`02_los_que_se_fueron.md` / `02_los_que_se_fueron.json`): 7 pasos sobre la huella de la emigración internacional (96.825 emigrantes censados en hogares), el récord de Chunchi (7,29%), el éxodo amazónico de Morona Santiago (16,94 por mil) y el desbalance de género en jóvenes.
3. **"La ciudad vacía"** (`03_ciudad_vacia.md` / `03_ciudad_vacia.json`): 7 pasos sobre las 900.000 viviendas deshabitadas o temporales (13,92% nacional), el 41,33% vacacional en Atacames, el 57,58% de desocupación en Déleg (mansiones de remesas con candado) frente al hacinamiento del 40% en Guayaquil.
4. **"La brecha digital"** (`04_brecha_digital.md` / `04_brecha_digital.json`): 7 pasos sobre la disparidad entre uso móvil (69,40%) e internet fijo domiciliario (51,42%), la trampa del prepago en la Costa rural, la brecha interna en Quito (91,99% en Iñaquito vs 50,54% en Pacto) y el analfabetismo digital de adultos mayores.

---

## 2. Los 4 Giros Contraintuitivos

| Historia | Creencia Popular Común | Giro Contraintuitivo Comprobado con Datos Censales |
|---|---|---|
| **1. El Ecuador que envejece** | El envejecimiento es exclusivo de aldeas campesinas aisladas. | **La vejez en las torres de alta plusvalía:** En los barrios residenciales más ricos de Quito (Iñaquito, González Suárez), el envejecimiento ($>135$) y la soledad de adultos mayores igualan al campo andino, a solo 10 km de la marea infantil de Calderón ($22$). |
| **2. Los que se fueron** | La emigración traslada a familias completas de manera homogénea. | **La amputación de varones en edad productiva:** En cantones del Austro como Santa Isabel (Azuay), la razón de masculinidad entre 20 y 39 años se desploma a **69,99 varones por cada 100 mujeres** (faltan 3 de cada 10 hombres jóvenes). |
| **3. La ciudad vacía** | Las casas vacías son chozas ruinosas en aldeas rurales en ruinas. | **Las mansiones de remesas con candado:** En Déleg (Cañar), el **57,58% de las viviendas están desocupadas o son temporales**: grandes residencias de hormigón financiadas con dólares de EE. UU. que pasan deshabitadas, mientras en Guayaquil el hacinamiento supera el 40%. |
| **4. La brecha digital** | Quien tiene un teléfono inteligente ya no sufre brecha de conectividad. | **La trampa del celular prepago:** Mientras el 69,40% navega en su teléfono, la red fija domiciliaria no llega ni al 35% en cantones populares de la Costa (Balzar, El Empalme), obligando a las familias a comprar costosos paquetes diarios de megas sin red para estudiar o teletrabajar. |

---

## 3. Especificación Técnica y Reproducibilidad

- **Textos:** Rigurosamente controlados entre **40 y 70 palabras** por paso en español llano y accesible.
- **Resumen en inglés:** Una línea ejecutiva (`en_summary`) por cada paso para soporte bilingüe en el front-end.
- **Consultas SQL:** Cada paso incorpora su bloque DuckDB reproducible sobre `data/counts/v1b1/` y las salidas de la Fase 1B-2.
- **Especificación WebGIS:** Cada paso define el estado del visor en JSON: `nivel`, `centro [lon, lat]`, `zoom`, `indicador`, `filtro`, `capa_extra` y `resaltados`.
- **Cierre reflexivo:** Cada historia concluye con una pregunta abierta orientada a invitar al ciudadano a explorar su propio cantón o manzana en el visor interactivo.

---
*Fin del Handoff.*
