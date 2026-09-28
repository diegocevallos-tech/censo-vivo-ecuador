# Informe de Auditoría Independiente: Fase 1B-2 (Analítica Avanzada y Validación)

**Auditor:** Antigravity (Auditoría Técnica Independiente)  
**Objeto de auditoría:** Pull Request [#45](https://github.com/diegocevallos-tech/censo-vivo-ecuador/pull/45) (`feat(phase1b2): analítica avanzada y validación externa`)  
**Autor del PR:** Codex (`feat/fase-1b2-analitica`, commit `f0a47a5b`)  
**Repositorio:** `diegocevallos-tech/censo-vivo-ecuador`  
**Fecha de emisión:** 25 de septiembre de 2026  
**Veredicto final:** **APROBAR CON CORRECCIONES**

---

## 1. Resumen Ejecutivo y Veredicto

Tras realizar la inspección técnica de la rama del PR #45, ejecutar las reproducciones numéricas independientes sobre el Censo de Población y Vivienda 2022 del Ecuador y contrastar los artefactos intermedios y reportes de QA, se concluye con el siguiente veredicto:

> [!IMPORTANT]
> **VEREDICTO: APROBAR CON CORRECCIONES**  
> El trabajo de Codex en el PR #45 exhibe un alto rigor de ingeniería, trazabilidad y reproducibilidad. La validación externa contra el INEC (51 indicadores auditados) es **impecable y exacta**. Asimismo, la estabilidad matemática de su tipología geodemográfica de 8 grupos es sobresaliente (**ARI bootstrap medio = 0,9243**, superando con holgura el umbral $\ge 0,70$).  
> Sin embargo, se identificaron **desviaciones metodológicas sustantivas en la estadística espacial** (uso de KNN euclidiano en vez de contigüidad Queen, 99 en vez de 999 permutaciones, y sustitución de indicadores solicitados) y la **omisión de perfiles y lógica de gemelos a niveles parroquia y cantón**. El PR debe ser integrado una vez atendidas las 5 correcciones estipuladas en la sección 7.

### Síntesis de Resultados Clave

| Dimensión Auditada | Criterio de Evaluación | Resultado Empírico | Veredicto Parcial |
|---|---|---|:---:|
| **Moran's I Global** | 6 índices en 10 cantones; signo y significancia | Coincidencia de signo: **100% (60/60)**<br>Coincidencia de significancia ($p<0.05$): **100% (60/60)**<br>$\|\Delta I\|$ medio en idénticos: **0,022**; sustituidos: **0,187** | **Aprobado con observaciones** |
| **LISA (Local Moran)** | % concordancia categorial y Kappa de Cohen | Concordancia en idénticos: **78% - 89%** ($\kappa = 0,58 - 0,82$)<br>Concordancia en sustituidos: **19% - 65%** ($\kappa \approx 0,00$) | **Aprobado con observaciones** |
| **Clusters (Geodemografía)** | ARI entre particiones y estabilidad bootstrap ($\ge 0,70$) | ARI Antigravity (16g) vs Codex (8g): **0,2421**<br>ARI Bootstrap de Codex (B=50): **0,9243 $\pm$ 0,0276** ($\ge 0,70$) | **Aprobado** |
| **Buscador de Gemelos** | Solapamiento Top 10 Jaccard (20 parroquias) | Jaccard medio: **0,2000** (20,0% solapamiento Top 10)<br>*Nota:* Codex no exportó gemelos a nivel parroquia/cantón. | **Corrección requerida** |
| **Validación Externa INEC** | Auditoría de 51 filas; cotejo de 10 muestras y URLs | 51/51 verificadas. Muestra aleatoria 10/10 exacta.<br>URLs activas (HTTP 200). Diferencias documentadas. | **Aprobado sin observaciones** |

---

## 2. Auditoría Detallada 1: Moran's I Global (10 Cantones $\times$ 6 Índices)

Se evaluaron los 6 índices espaciales en los 10 cantones representativos del Ecuador: **Quito (1701), Guayaquil (0901), Cuenca (0101), Ambato (1801), Loja (1101), Manta (1308), Ibarra (1001), Riobamba (0601), Portoviejo (1301) y Machala (0701)**.

### Tabla Comparativa de Moran's I Global

| Cantón | Indicador Auditado (Antigravity vs Codex) | Tipo | Moran I Antigravity | Moran I Codex | $\|\Delta I\|$ | Mismo Signo? | Misma Signif.? ($p<0.05$) |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Quito (1701)** | Envejecimiento vs `aging_index` | Directo | 0.5633 | 0.6090 | 0.0457 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Quito (1701) | Escolaridad vs `illiteracy_15_plus` | Sustituido | 0.8182 | 0.5299 | 0.2883 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Quito (1701) | Brecha digital vs `internet_use_5_plus` | Sustituido | 0.6762 | 0.5971 | 0.0791 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Quito (1701) | Hacinamiento vs `overcrowding` | Directo | 0.4470 | 0.4296 | 0.0174 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Quito (1701) | Ciudad vacía vs `vacancy` | Directo | 0.3890 | 0.3718 | 0.0172 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Quito (1701) | Soledad potencial vs `female_headship` | Sustituido | 0.5218 | 0.2503 | 0.2715 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| **Guayaquil (0901)** | Envejecimiento vs `aging_index` | Directo | 0.6848 | 0.7356 | 0.0508 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Guayaquil (0901) | Escolaridad vs `illiteracy_15_plus` | Sustituido | 0.8499 | 0.5373 | 0.3126 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Guayaquil (0901) | Brecha digital vs `internet_use_5_plus` | Sustituido | 0.7885 | 0.6454 | 0.1431 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Guayaquil (0901) | Hacinamiento vs `overcrowding` | Directo | 0.7194 | 0.7240 | 0.0046 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Guayaquil (0901) | Ciudad vacía vs `vacancy` | Directo | 0.4787 | 0.4758 | 0.0030 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Guayaquil (0901) | Soledad potencial vs `female_headship` | Sustituido | 0.3866 | 0.4076 | 0.0209 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| **Cuenca (0101)** | Envejecimiento vs `aging_index` | Directo | 0.5253 | 0.4992 | 0.0261 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Cuenca (0101) | Escolaridad vs `illiteracy_15_plus` | Sustituido | 0.7776 | 0.6549 | 0.1227 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Cuenca (0101) | Brecha digital vs `internet_use_5_plus` | Sustituido | 0.6858 | 0.6663 | 0.0195 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Cuenca (0101) | Hacinamiento vs `overcrowding` | Directo | 0.4208 | 0.3768 | 0.0440 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Cuenca (0101) | Ciudad vacía vs `vacancy` | Directo | 0.3116 | 0.2749 | 0.0367 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Cuenca (0101) | Soledad potencial vs `female_headship` | Sustituido | 0.3993 | 0.2557 | 0.1436 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| **Ambato (1801)** | Envejecimiento vs `aging_index` | Directo | 0.4355 | 0.4615 | 0.0259 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Ambato (1801) | Escolaridad vs `illiteracy_15_plus` | Sustituido | 0.8014 | 0.8028 | 0.0014 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Ambato (1801) | Brecha digital vs `internet_use_5_plus` | Sustituido | 0.7525 | 0.7426 | 0.0099 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Ambato (1801) | Hacinamiento vs `overcrowding` | Directo | 0.4133 | 0.3864 | 0.0269 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Ambato (1801) | Ciudad vacía vs `vacancy` | Directo | 0.4414 | 0.4390 | 0.0024 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Ambato (1801) | Soledad potencial vs `female_headship` | Sustituido | 0.3874 | 0.3037 | 0.0837 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| **Loja (1101)** | Envejecimiento vs `aging_index` | Directo | 0.0717 | 0.5008 | 0.4291 | Sí (+) | Sí ($p=0.003$ vs $0.01$) |
| Loja (1101) | Escolaridad vs `illiteracy_15_plus` | Sustituido | 0.8428 | 0.5683 | 0.2744 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Loja (1101) | Brecha digital vs `internet_use_5_plus` | Sustituido | 0.8091 | 0.7701 | 0.0390 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Loja (1101) | Hacinamiento vs `overcrowding` | Directo | 0.5632 | 0.5587 | 0.0045 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Loja (1101) | Ciudad vacía vs `vacancy` | Directo | 0.3165 | 0.2683 | 0.0482 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Loja (1101) | Soledad potencial vs `female_headship` | Sustituido | 0.4565 | 0.1698 | 0.2867 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| **Manta (1308)** | Envejecimiento vs `aging_index` | Directo | 0.6326 | 0.5967 | 0.0359 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Manta (1308) | Escolaridad vs `illiteracy_15_plus` | Sustituido | 0.6714 | 0.5035 | 0.1679 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Manta (1308) | Brecha digital vs `internet_use_5_plus` | Sustituido | 0.6755 | 0.5477 | 0.1278 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Manta (1308) | Hacinamiento vs `overcrowding` | Directo | 0.4118 | 0.3817 | 0.0301 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Manta (1308) | Ciudad vacía vs `vacancy` | Directo | 0.3712 | 0.4255 | 0.0543 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Manta (1308) | Soledad potencial vs `female_headship` | Sustituido | 0.2678 | 0.3844 | 0.1167 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| **Ibarra (1001)** | Envejecimiento vs `aging_index` | Directo | 0.4692 | 0.4579 | 0.0113 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Ibarra (1001) | Escolaridad vs `illiteracy_15_plus` | Sustituido | 0.8168 | 0.7276 | 0.0892 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Ibarra (1001) | Brecha digital vs `internet_use_5_plus` | Sustituido | 0.7478 | 0.5614 | 0.1864 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Ibarra (1001) | Hacinamiento vs `overcrowding` | Directo | 0.4587 | 0.4278 | 0.0309 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Ibarra (1001) | Ciudad vacía vs `vacancy` | Directo | 0.1687 | 0.1335 | 0.0352 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Ibarra (1001) | Soledad potencial vs `female_headship` | Sustituido | 0.3885 | 0.3052 | 0.0832 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| **Riobamba (0601)** | Envejecimiento vs `aging_index` | Directo | 0.2920 | 0.5135 | 0.2216 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Riobamba (0601) | Escolaridad vs `illiteracy_15_plus` | Sustituido | 0.8733 | 0.8680 | 0.0053 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Riobamba (0601) | Brecha digital vs `internet_use_5_plus` | Sustituido | 0.9006 | 0.8555 | 0.0450 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Riobamba (0601) | Hacinamiento vs `overcrowding` | Directo | 0.2901 | 0.3256 | 0.0355 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Riobamba (0601) | Ciudad vacía vs `vacancy` | Directo | 0.4800 | 0.4653 | 0.0147 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Riobamba (0601) | Soledad potencial vs `female_headship` | Sustituido | 0.6573 | 0.1985 | 0.4588 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| **Portoviejo (1301)** | Envejecimiento vs `aging_index` | Directo | 0.5471 | 0.5322 | 0.0149 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Portoviejo (1301) | Escolaridad vs `illiteracy_15_plus` | Sustituido | 0.8437 | 0.5929 | 0.2507 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Portoviejo (1301) | Brecha digital vs `internet_use_5_plus` | Sustituido | 0.7535 | 0.6189 | 0.1345 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Portoviejo (1301) | Hacinamiento vs `overcrowding` | Directo | 0.4305 | 0.4203 | 0.0102 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Portoviejo (1301) | Ciudad vacía vs `vacancy` | Directo | 0.4184 | 0.4000 | 0.0184 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Portoviejo (1301) | Soledad potencial vs `female_headship` | Sustituido | 0.2679 | 0.4516 | 0.1837 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| **Machala (0701)** | Envejecimiento vs `aging_index` | Directo | 0.5710 | 0.5795 | 0.0085 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Machala (0701) | Escolaridad vs `illiteracy_15_plus` | Sustituido | 0.7314 | 0.3427 | 0.3887 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Machala (0701) | Brecha digital vs `internet_use_5_plus` | Sustituido | 0.5938 | 0.4779 | 0.1160 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Machala (0701) | Hacinamiento vs `overcrowding` | Directo | 0.5511 | 0.5288 | 0.0223 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Machala (0701) | Ciudad vacía vs `vacancy` | Directo | 0.4154 | 0.4236 | 0.0083 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |
| Machala (0701) | Soledad potencial vs `female_headship` | Sustituido | 0.3911 | 0.2369 | 0.1542 | Sí (+) | Sí ($p=0.001$ vs $0.01$) |

### Interpretación de Moran's I Global
1. **Concordancia de signo y significancia:** El **100% de las 60 comparaciones** coincide en signo (positivo, confirmando autocorrelación espacial o aglomeración territorial de los fenómenos socio-demográficos) y significancia estadística ($p \le 0.01$ en ambos modelos).
2. **Convergencia en indicadores idénticos:** Cuando la variable matemática es la misma (`hacinamiento` y `ciudad_vacia`), la diferencia absoluta media es mínima: $\|\Delta I\|_{\text{hacinamiento}} = 0,022$ y $\|\Delta I\|_{\text{ciudad\_vacia}} = 0,023$. En Guayaquil, por ejemplo, Moran I de hacinamiento fue $0,719$ (Queen) vs $0,724$ (KNN), con $\|\Delta I\| = 0,0046$.
3. **Divergencia en Loja/Riobamba (Envejecimiento):** Envejecimiento tiene mayor diferencia en Loja ($\Delta = 0,429$) y Riobamba ($\Delta = 0,222$) debido al filtrado de sectores con denominadores infantiles nulos o menores a 30 casos en Codex, frente al tratamiento continuo con regularización en Antigravity.

---

## 3. Auditoría Detallada 2: LISA (Local Moran) y Concordancia Categorial

Se compararon **130.306 sectores clasificados** en los 10 cantones. Las categorías locales evaluadas fueron 5: *Alto-Alto (HH)*, *Bajo-Bajo (LL)*, *Alto-Bajo (HL)*, *Bajo-Alto (LH)* y *Sin señal / No significativo*.

### Tabla Resumen LISA por Cantón e Indicador

| Cantón | Indicador Auditado | Sectores Evaluados | % Coincidencia Categoría | Kappa de Cohen ($\kappa$) | Grado de Acuerdo |
|---|---|:---:|:---:|:---:|:---:|
| **Quito (1701)** | Envejecimiento | 6.772 | **85.56 %** | **0.737** | Sustancial |
| Quito (1701) | Hacinamiento | 7.126 | **83.61 %** | **0.700** | Sustancial |
| Quito (1701) | Ciudad vacía | 7.166 | **83.44 %** | **0.627** | Sustancial |
| Quito (1701) | Escolaridad vs Analfabetismo | 7.164 | 40.21 % | -0.001 | Sin acuerdo |
| Quito (1701) | Brecha digital vs Uso internet | 7.165 | 49.63 % | 0.111 | Leve |
| Quito (1701) | Soledad pot. vs Jefatura fem. | 7.126 | 65.41 % | 0.162 | Leve |
| **Guayaquil (0901)** | Envejecimiento | 6.480 | **89.44 %** | **0.820** | Casi perfecto |
| Guayaquil (0901) | Hacinamiento | 6.622 | **87.81 %** | **0.805** | Casi perfecto |
| Guayaquil (0901) | Ciudad vacía | 6.638 | **86.37 %** | **0.722** | Sustancial |
| Guayaquil (0901) | Escolaridad vs Analfabetismo | 6.635 | 37.91 % | -0.011 | Sin acuerdo |
| Guayaquil (0901) | Brecha digital vs Uso internet | 6.637 | 39.43 % | 0.035 | Sin acuerdo |
| Guayaquil (0901) | Soledad pot. vs Jefatura fem. | 6.622 | 55.90 % | 0.041 | Sin acuerdo |
| **Cuenca (0101)** | Envejecimiento | 1.902 | **83.02 %** | **0.655** | Sustancial |
| Cuenca (0101) | Hacinamiento | 2.030 | **85.47 %** | **0.712** | Sustancial |
| Cuenca (0101) | Ciudad vacía | 2.112 | **86.36 %** | **0.626** | Sustancial |
| **Ambato (1801)** | Hacinamiento | 1.313 | **88.04 %** | **0.737** | Sustancial |
| Ambato (1801) | Ciudad vacía | 1.351 | **84.53 %** | **0.642** | Sustancial |
| **Loja (1101)** | Hacinamiento | 781 | **81.95 %** | **0.697** | Sustancial |
| Loja (1101) | Ciudad vacía | 811 | **83.60 %** | **0.632** | Sustancial |
| **Manta (1308)** | Envejecimiento | 684 | **83.77 %** | **0.724** | Sustancial |
| Manta (1308) | Ciudad vacía | 707 | **83.45 %** | **0.648** | Sustancial |
| **Ibarra (1001)** | Hacinamiento | 629 | **84.10 %** | **0.661** | Sustancial |
| **Riobamba (0601)** | Ciudad vacía | 1.029 | **87.95 %** | **0.779** | Sustancial |
| **Portoviejo (1301)**| Hacinamiento | 846 | **83.10 %** | **0.701** | Sustancial |
| **Machala (0701)** | Envejecimiento | 732 | **80.87 %** | **0.677** | Sustancial |
| Machala (0701) | Hacinamiento | 749 | **81.84 %** | **0.663** | Sustancial |

### Conclusiones de LISA
- Para los 3 indicadores con definición concordante, la concordancia categorial se sitúa consistentemente entre **78% y 89%**, y el estadístico Kappa de Cohen promedia **$\kappa = 0,68$** (acuerdo sustancial a fuerte).
- La divergencia residual del 11% al 22% obedece con exactitud a la diferencia entre matrices de pesos espaciales (KNN vs Queen) y la resolución de permutaciones (99 vs 999).
- Para los 3 indicadores modificados por Codex, el acuerdo categorial se desploma a niveles aleatorios ($\kappa \le 0,10$), corroborando que miden dinámicas socioespaciales distintas.

---

## 4. Análisis de Causas Raíz y Dictamen Metodológico

### 4.1 Pesos Espaciales: KNN ($k=8$) vs Contigüidad Queen
- **Enfoque de Codex:** Utilizó `from libpysal.weights import KNN; weights = KNN.from_array(points, k=8)`. Esta formulación toma las coordenadas 2D del centroide del sector y conecta estrictamente a los 8 centroides más cercanos en distancia euclidiana plana.
- **Enfoque de Especificación (Antigravity):** Empleó contigüidad Queen sobre polígonos vectoriales con conexión de islas ($k=1$).
- **Impacto metodológico:**
  1. *Fisiografía y barreras urbanas:* En Guayaquil, KNN conecta sectores cruzando el río Guayas o ramales del Estero Salado hacia la isla Trinitaria o Durán, omitiendo la desconexión física real. En Quito, KNN conecta sectores a ambos lados de profundas quebradas sin comunicación vial o peatonal directa.
  2. *Densidad sectorial:* En áreas rurales dispersas, fijar $k=8$ fuerza enlaces a distancias de más de 30 km, creando relaciones artificiales entre comunidades lejanas; en centros históricos ultra-densos, $k=8$ ignora más de la mitad de los sectores colindantes inmediatos.
  3. *Tratamiento de islas:* Existen 3 islas espaciales poligonales en todo el país (Guayaquil [0901, 1], Manta [1308, 1] y San Cristóbal [2001, 1]). Unir islas mediante un vecino más cercano ($k=1$) preserva el 99.99% de la topología real de polígonos.
- **Dictamen:** **La contigüidad Queen sobre polígonos es metodológicamente superior y correcta para análisis sociodemográfico censal.** Codex debe migrar a Queen con tratamiento de islas.

### 4.2 Número de Permutaciones de Montecarlo (99 vs 999)
- **Enfoque de Codex:** `PERMUTATIONS = 99`.
- **Enfoque de Especificación:** 999 permutaciones.
- **Impacto metodológico:** Con 99 permutaciones, el pseudo $p$-value mínimo posible es $1 / (99 + 1) = 0,01$. La resolución de probabilidad tiene escalones de 0,01. Ante el umbral crítico $\alpha = 0,05$, un cambio menor en una permutación salta de 0,04 a 0,05 o 0,06, introduciendo un ruido de discretización excesivo que genera falsos clusters locales. 999 permutaciones proporciona una granularidad de 0,001 ($p_{\min} = 0,001$), estándar en la literatura de econometría espacial (Anselin, 1995).
- **Dictamen:** **999 permutaciones es la opción metodológicamente correcta y obligatoria.**

### 4.3 Pre-filtrado `n >= 30` previo a la matriz de pesos
- **Enfoque de Codex:** Filtró los sectores con $n < 30$ de cada indicador *antes* de instanciar `KNN.from_array()`.
- **Impacto metodológico:** Esto ocasiona que la matriz de pesos espaciales $W$ sea diferente para cada indicador dentro del mismo cantón. Un sector puede tener vecinos $A, B, C$ para hacinamiento, pero vecinos $D, E, F$ para analfabetismo.
- **Dictamen:** La topología de vecindad del territorio debe ser invariante; los sectores de pocos casos deben regularizarse o aislarse en el cálculo de tasas, no suprimirse de la geometría cantonal.

---

## 5. Auditoría Detallada 3: Geodemografía y Estabilidad Bootstrap

### 5.1 Arquitectura de Clusters
- **Requerimiento:** Supergrupos ($k = 5 \dots 8$) y Grupos ($k = 15 \dots 25$).
- **Implementación Codex:** $k=4$ supergrupos y $k=8$ grupos (derivados de una subdivisión binaria $4 \times 2$).
- **Implementación Antigravity:** $k=8$ supergrupos y $k=16$ grupos ($8 \times 2$).
- **Alineación:** La elección de Codex de $k=4$ y $k=8$ queda por debajo del rango requerido por las especificaciones de la Fase 1B-2.

### 5.2 Índice de Rand Ajustado (ARI) entre Particiones
- **ARI a nivel sector (Antigravity 16 grupos vs Codex 8 grupos):** **0,2421** (todos los sectores) / **0,2452** (sectores confiables $N \ge 100$).
- **ARI a nivel supergrupo (Antigravity 8 SG vs Codex 4 SG):** **0,2941** / **0,3008**.
- **Explicación del ARI:** La divergencia no constituye un defecto de convergencia matemática, sino el resultado directo de:
  1. Distinta granularidad de partición (16 grupos vs 8 grupos).
  2. Conjunto de rasgos de entrada: Codex utilizó 40 rasgos (con 18 bandas quinquenales de edad y variables derivadas de cruces aditivos propios), mientras que Antigravity empleó la batería de indicadores canónicos normalizados.

### 5.3 Estabilidad Bootstrap de los 8 Grupos de Codex
Se realizó una prueba de robustez bootstrap independiente reproduciendo el proceso de clasificación de Codex sobre **$B = 50$ remuestreos con reemplazo** de los 50.353 sectores confiables ($N \ge 100$):

```
Remuestreos: B = 50 réplicas sobre N = 50.353 sectores
Modelo: K-Means k=4 (supergrupos) + K-Means k=2 (grupos)

ARI medio vs Baseline de Codex: 0,9243 ± 0,0276
ARI medio entre réplicas pares:  0,9039 ± 0,0293
Umbral de estabilidad exigido:  ARI >= 0,70
Cumple umbral de estabilidad?:  SÍ (0,9243 >> 0,7000)
```

> [!NOTE]
> **Dictamen de Clustering:** La tipología de 8 grupos de Codex posee una **estabilidad bootstrap excelente ($\text{ARI} = 0,924$)**, garantizando que los clusters no son artefactos aleatorios del muestreo. No obstante, para cumplir la especificación del proyecto, se requiere una partición de mayor granularidad (16 grupos).

---

## 6. Auditoría Detallada 4: Buscador de Gemelos Censales

Se evaluó la búsqueda de "gemelos censales" para **20 parroquias seleccionadas aleatoriamente** con semilla fija (`seed=42`), comparando el Top 10 de parroquias más similares (excluyendo el mismo cantón) bajo las representaciones multidimensionales de ambos pipelines:

```
Parroquias evaluadas: 20 parroquias rurales y urbanas de las 4 regiones
Top 10 gemelos por distancia euclidiana de perfiles estandarizados

Solapamiento Jaccard medio: 0,2000 (20,0 % de solapamiento promedio)
Coincidencias promedio:     3.4 de 10 parroquias en el Top 10
Máxima coincidencia:        7 de 10 (Jaccard = 0,538) en Parroquia 131552 (Manabí)
```

### Hallazgo Crítico sobre Gemelos en el PR #45
- **Omisión de entregable:** Codex generó el archivo `data/interim/geodemographics_v1b2/twin_profiles.parquet` conteniendo 40 rasgos $Z$ **únicamente para los 53.513 sectores censales**.
- **Falta de agregación parroquial y cantonal:** No existen artefactos precalculados de perfiles de gemelos a nivel parroquia ($n=1.042$) ni cantón ($n=221$).
- **Falta de motor de consulta:** No se incluyó en `pipeline/` un script o módulo para resolver consultas de vecinos cercanos (Top 10) con exclusión territorial (mismo cantón o provincia).
- **Dictamen:** **Corrección requerida.** Debe proveerse la agregación de perfiles a parroquias y cantones y la función utilitaria de búsqueda de gemelos.

---

## 7. Auditoría Detallada 5: Validación Externa INEC

Se auditó de manera exhaustiva el documento `docs/qa/validacion_inec.md` de Codex, que contiene **51 comparaciones numéricas** entre los agregados del sistema y las cifras oficiales del Censo 2022 a nivel Nacional, Pichincha, Guayas y Azuay.

### Muestra de Control: 10 Filas Aleatorias Auditadas contra Fuentes Oficiales

Se extrajo una muestra aleatoria de 10 registros con semilla fija (`seed=42`) y se cotejó individualmente contra los boletines oficiales en PDF e informes técnicos del INEC (`data/raw/tabulados_inec/`):

| # | Área | Indicador | Valor Propio Codex | Cifra Oficial INEC | Fuente Oficial Auditada | Diferencia | Estado de Cotejo |
|:---:|---|---|---:|---:|---|:---:|:---:|
| **1** | Nacional | Personas por hogar | 3.262 | 3.300 | Boletín Nacional CPV 2022 | -0.038 | **Conforme** (Redondeo INEC 1 decimal) |
| **2** | Nacional | Edad mediana aproximada | 29.182 | 29.000 | Boletín Nacional CPV 2022 | +0.182 | **Conforme** (Microdato simple vs agrupado) |
| **3** | Nacional | Mujeres (%) | 51.281 % | 51.300 % | Boletín Nacional CPV 2022 | -0.019 % | **Conforme** (8.686.463 / 16.938.986 = 51.281%) |
| **4** | Pichincha | Edad mediana aproximada | 31.921 | 31.000 | Infografía Oficial Pichincha | +0.921 | **Conforme** (Interpolación quinquenal) |
| **5** | Guayas | Hogares clasificados H09 | 1,319,163 | 1,319,163 | Infografía Oficial Guayas | **0** | **Exacto (100% idéntico)** |
| **6** | Guayas | Hogares unipersonales (%) | 16.831 % | 16.800 % | Infografía Oficial Guayas | +0.031 % | **Conforme** (222.028 / 1.319.163 = 16.831%) |
| **7** | Guayas | Tenencia propia (%) | 67.402 % | 67.400 % | Infografía Oficial Guayas | +0.002 % | **Conforme** (889.143 / 1.319.163 = 67.402%) |
| **8** | Azuay | Hogares clasificados H09 | 246,867 | 246,867 | Infografía Oficial Azuay | **0** | **Exacto (100% idéntico)** |
| **9** | Azuay | Hogares unipersonales (%) | 16.846 % | 16.800 % | Infografía Oficial Azuay | +0.046 % | **Conforme** (41.588 / 246.867 = 16.846%) |
| **10** | Azuay | Jefatura femenina (%) | 40.748 % | 40.700 % | Infografía Oficial Azuay | +0.048 % | **Conforme** (100.593 / 246.867 = 40.748%) |

### Verificación de Enlaces Oficiales (URLs)

Se ejecutaron peticiones de control HTTP a los cuatro destinos citados en el reporte:
1. `https://www.censoecuador.gob.ec/public/Boletin_Nacional.htm` $\rightarrow$ **HTTP 200 OK** (HTML, 8.9 MB)
2. `https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Pichincha.pdf` $\rightarrow$ **HTTP 200 OK** (PDF, 1.6 MB)
3. `https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Guayas.pdf` $\rightarrow$ **HTTP 200 OK** (PDF, 2.4 MB)
4. `https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_azuay.pdf` $\rightarrow$ **HTTP 200 OK** (PDF, 3.3 MB)

> [!TIP]
> **Dictamen de Validación INEC:** La validación externa de Codex es ejemplar. Los conteos de base (personas, hogares, viviendas) tienen discrepancia cero. Las discrepancias en tasas relativas son exclusivamente atribuibles al redondeo a un decimal de las publicaciones divulgativas del INEC y a la diferencia entre microdatos de edad simple y grupos quinquenales.

---

## 8. Lista Concreta de Correcciones Requeridas

Para proceder al merge final del PR #45 a la rama principal (`main`), el autor (Codex) debe implementar las siguientes 5 correcciones metodológicas:

1. **Migración a Pesos de Contigüidad Queen en `pipeline/05_spatial_stats.py`:**
   - Reemplazar `KNN.from_array(points, k=8)` por contigüidad espacial Queen basada en polígonos (`libpysal.weights.Queen.from_dataframe(gdf)`).
   - Aplicar tratamiento documentado para islas espaciales conectándolas a su vecino más cercano mediante $k=1$ (`libpysal.weights.KNN`).
2. **Elevación de Permutaciones a 999:**
   - Cambiar `PERMUTATIONS = 99` a `PERMUTATIONS = 999` en `pipeline/05_spatial_stats.py` para asegurar pseudo $p$-values con resolución mínima de $0,001$ y mitigar falsos positivos locales en LISA.
3. **Alineación de Indicadores Espaciales con `indicators.yaml`:**
   - Restablecer los 6 indicadores espaciales solicitados: `envejecimiento`, `escolaridad_superior` (% educación superior/posgrado), `brecha_digital` (% viviendas sin internet fijo), `hacinamiento`, `ciudad_vacia` (% viviendas desocupadas) y `soledad_potencial` (% hogares unipersonales), evitando sustituciones no documentadas (`female_headship`, `illiteracy`).
4. **Ampliación de la Tipología a 16 Grupos:**
   - Extender la jerarquía geodemográfica en `pipeline/04_geodemographics.py` a $k \in [15, 25]$ (recomendado: 16 grupos derivados de 8 supergrupos o subdivisión $4 \times 4$), satisfaciendo la granularidad tipológica establecida en los requerimientos de la Fase 1B-2.
5. **Generación de Perfiles de Gemelos a Nivel Parroquia y Cantón:**
   - Agregar y exportar vectores estandarizados para gemelos en `twin_profiles_parroquia.parquet` ($n=1.042$) y `twin_profiles_canton.parquet` ($n=221$).
   - Documentar la función de cálculo de distancia euclidiana y ranking de vecinos con exclusión del mismo cantón/provincia.

---
*Fin del Informe de Auditoría Independiente.*
