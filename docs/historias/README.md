# Especificación Editorial y Arquitectura de Scrollytelling

Este directorio reúne los guiones, consultas SQL reproducibles y estados de cámara y visualización para las cuatro historias guiadas interactivas (*scrollytelling*) del portal WebGIS **Censo Vivo Ecuador 2022**.

---

## 1. Guiones Publicados

| ID | Título | Pasos | Giro Contraintuitivo | Indicador Principal (`indicators.yaml`) |
|---|---|:---:|---|---|
| `01_ecuador_envejece` | [El Ecuador que envejece](01_ecuador_envejece.md) | 7 | Misma escala: la parroquia urbana Iñaquito (141,53) casi quintuplica el índice de la parroquia Calderón (30,11; 250.877 hab) en el mismo cantón Quito. | `aging_index` |
| `02_los_que_se_fueron` | [Los que se fueron](02_los_que_se_fueron.md) | 8 | Asimetría de género en edades productivas: en Santa Isabel la razón de masculinidad (20-39 años) desciende a 69,99 varones por 100 mujeres. | `emigrant_households` / `male_ratio` |
| `03_ciudad_vacia` | [La ciudad vacía](03_ciudad_vacia.md) | 7 | La mayor desocupación cantonal (V0201=4) se registra en Cañar (26,41%) y Suscal (23,12%), mientras Guayaquil noroeste sufre hacinamiento > 40%. | `vacant_private_dwellings` |
| `04_brecha_digital` | [La brecha digital](04_brecha_digital.md) | 7 | Mismo universo de hogares: en Paján el 80,48% de hogares tiene celular pero solo el 22,64% internet fijo (brecha de 57,84 puntos). | `fixed_internet` |

---

## 2. Reglas Editoriales Aplicadas

1. **Hecho vs Hipótesis:** El texto de cada paso contiene estrictamente afirmaciones derivadas de los conteos censales del CPV 2022. Cualquier interpretación contextual (causas de la migración, dinámicas de suelo o redes móviles) se delimita explícitamente en un recuadro de hipótesis, con un máximo de una hipótesis por historia.
2. **Misma Escala Geográfica:** Las comparaciones se ejecutan siempre entre unidades del mismo nivel: nacional con nacional, cantón con cantón, parroquia con parroquia y sector con sector censal.
3. **Mismos Denominadores:** En la brecha digital, se compara hogares con hogares (hogares con celular `H1002=1` vs hogares con internet fijo `H1004=1`), sobre el mismo denominador de 5.188.827 hogares clasificados.
4. **Tono Divulgativo Sobrio:** Lenguaje riguroso, claro y exento de términos sensacionalistas o dramatizaciones no avaladas por la estadística pública.
5. **Calibración de Extensión:** Cada paso cuenta con un texto narrativo de **40 a 70 palabras**, acompañado de un resumen en inglés (`en_summary`) para interfaces bilingües.

---

## 3. Propuesta de Variante: `unoccupied_dwellings` (Viviendas No Ocupadas Habitualmente)

### Justificación Metodológica
En `indicators.yaml`, el indicador oficial `vacant_private_dwellings` está definido como:
$$\text{vacant\_private\_dwellings} = 100 \times \frac{\text{V0201}=4}{\sum_{i=1}^5 \text{V0201}=i}$$
Esta métrica mide estrictamente la vivienda **desocupada**.

No obstante, en cantones de balneario turístico (Atacames, Salinas, Playas) y en cantones de alta emigración (Déleg, Sevilla de Oro), existe un parque habitacional muy significativo clasificado como **vivienda temporal o vacacional** (`V0201=3`). Al evaluar la presión sobre los servicios y la presencia efectiva de residentes permanentes, resulta de alto valor analítico considerar conjuntamente las viviendas desocupadas y las de uso temporal.

### Propuesta Formal de Adición a indicators.yaml (Variante)
Se propone formalmente incorporar en futuras versiones del catálogo la siguiente variante sin alterar `vacant_private_dwellings`:

```yaml
- id: unoccupied_dwellings
  name:
    es: Viviendas desocupadas y de uso temporal
    en: Unoccupied and seasonal dwellings
  theme: vivienda
  kind: ratio
  formula: 100 × V0201∈{3,4} / V0201 válido
  population_reference: Viviendas particulares con condición válida
  source_variables:
  - V0201
  min_level: manzana
  min_n: 30
  direction: neutral
  palette: PuRd
  methodological_note: Suma las viviendas de uso temporal/vacacional (categoría 3) y desocupadas (categoría 4). Permite analizar el parque sin ocupación permanente.
  bibliography: INEC (2022), Diccionario de Variables CPV 2022.
  numerator:
  - cat:vivienda:V0201:3
  - cat:vivienda:V0201:4
  denominator:
  - cat:vivienda:V0201:1
  - cat:vivienda:V0201:2
  - cat:vivienda:V0201:3
  - cat:vivienda:V0201:4
  - cat:vivienda:V0201:5
  factor: 100
  bayesian: true
```

---
*Documentación oficial de guiones y especificaciones.*
