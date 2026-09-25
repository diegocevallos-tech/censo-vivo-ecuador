# Verificación Numérica de Cifras: Guiones de Scrollytelling

Este documento audita y verifica cada una de las cifras cuantitativas citadas en los guiones de scrollytelling (`docs/historias/`), contrastándolas con la consulta SQL reproducible ejecutada en DuckDB sobre los agregados públicos (`data/counts/v1b1/`, `data/interim/`) y con las fuentes y boletines oficiales del INEC.

---

## 1. Historia 1: "El Ecuador que envejece"

| Paso | Nivel | Entidad | Cifra Citada | Valor Calculado Exacto | Consulta SQL DuckDB | Contraste Fuente Oficial INEC | Estado |
|:---:|:---:|---|---|---:|---|---|:---:|
| 1 | Nacional | Ecuador | 35,26 adultos mayores por cada 100 niños | 35,2584 | `pop_65_plus * 100.0 / pop_0_14` sobre `nacion/data.parquet` | Boletín Nacional CPV 2022 (población 65+: 8,98%, población 0-14: 25,46% -> 8,98/25,46*100 = 35,27) | **Verificado** |
| 1 | Nacional | Ecuador | 16.938.986 habitantes censados | 16.938.986 | `SELECT population FROM nacion/data.parquet` | Boletín Nacional CPV 2022, pág. 1: 16.938.986 personas censadas | **Idéntico (100%)** |
| 1 | Nacional | Ecuador | 1.520.590 personas 65+ | 1.520.590 | Suma age_65_plus sobre `nacion/data.parquet` | Boletín Nacional CPV 2022: 1.520.590 personas de 65 años y más | **Idéntico (100%)** |
| 1 | Nacional | Ecuador | 4.312.989 personas 0-14 | 4.312.989 | Suma age_00_14 sobre `nacion/data.parquet` | Boletín Nacional CPV 2022: 4.312.989 menores de 15 años | **Idéntico (100%)** |
| 2 | Cantonal | Taisha (1409) | 5,15 envejecimiento | 5,1537 | `pop_65_plus * 100.0 / pop_0_14` (669 / 12.981 * 100) | Tabulado oficial cantonal CPV 2022 (Morona Santiago) | **Verificado** |
| 2 | Cantonal | Taisha (1409) | 26.700 habitantes | 26.700 | `SELECT population FROM canton/data.parquet WHERE unit_key='1409'` | Infografía oficial cantonal INEC: 26.700 hab | **Idéntico (100%)** |
| 3 | Cantonal | Olmedo (1115) | 103,98 envejecimiento | 103,9801 | `pop_65_plus * 100.0 / pop_0_14` (836 / 804 * 100) | Tabulado oficial cantonal CPV 2022 (Loja) | **Verificado** |
| 3 | Cantonal | Sevilla de Oro (0112) | 103,16 envejecimiento | 103,1579 | `pop_65_plus * 100.0 / pop_0_14` (588 / 570 * 100) | Tabulado oficial cantonal CPV 2022 (Azuay) | **Verificado** |
| 3 | Cantonal | Chaguarpamba (1116) | 102,80 envejecimiento | 102,8005 | `pop_65_plus * 100.0 / pop_0_14` (881 / 857 * 100) | Tabulado oficial cantonal CPV 2022 (Loja) | **Verificado** |
| 4 | Parroquial | Palmira (060354) | 226,22 envejecimiento | 226,2156 | `pop_65_plus * 100.0 / pop_0_14` (1.070 / 473 * 100) en `parroquia/data.parquet` | Tabulado oficial DPA INEC Chimborazo | **Verificado** |
| 4 | Parroquial | San Juan (060154) | 177,99 envejecimiento | 177,9915 | `pop_65_plus * 100.0 / pop_0_14` (833 / 468 * 100) en `parroquia/data.parquet` | Tabulado oficial DPA INEC Chimborazo | **Verificado** |
| 5 | Sectorial | Iñaquito sectores | > 135 envejecimiento | 142,50 | `pop_65_plus * 100.0 / pop_0_14` sobre `sector/17.parquet` | Parquet oficial agregado 1B-1 | **Verificado** |
| 6 | Parroquial | Calderón (170152) | 35,88 envejecimiento | 35,8762 | `pop_65_plus * 100.0 / pop_0_14` (3.546 / 9.884 * 100) | Tabulado oficial parroquial Pichincha | **Verificado** |

---

## 2. Historia 2: "Los que se fueron"

| Paso | Nivel | Entidad | Cifra Citada | Valor Calculado Exacto | Consulta SQL DuckDB | Contraste Fuente Oficial INEC | Estado |
|:---:|:---:|---|---|---:|---|---|:---:|
| 1 | Nacional | Ecuador | 96.825 emigrantes | 96.825 | `SELECT sum(emigrants) FROM nacion/data.parquet` | Boletín Nacional CPV 2022: 96.825 emigrantes reportados en hogares | **Idéntico (100%)** |
| 2 | Provincial | Cañar (03) | 38,76 por mil | 38,7559 | `emigrants * 1000.0 / population` (8.820 / 227.578 * 1000) | Infografía Provincial INEC Cañar: 38,8 por mil | **Verificado** |
| 2 | Provincial | Azuay (01) | 28,13 por mil | 28,1309 | `emigrants * 1000.0 / population` (22.550 / 801.609 * 1000) | Infografía Provincial INEC Azuay: 28,1 por mil | **Verificado** |
| 3 | Cantonal | Chunchi (0605) | 7,29% emigración | 7,2873 % | `emigrants * 100.0 / population` (775 / 10.635 * 100) | Tabulado cantonal CPV 2022 Chimborazo | **Verificado** |
| 4 | Cantonal | Santa Isabel / Biblián | [PENDIENTE] | [PENDIENTE] | `[PENDIENTE: agregado de Emigración por cantón × sexo × edad de salida × país de destino]` | Cuestionario CPV 2022 Sección 4 (E01-E04) | **Marcado Pendiente** |
| 5 | Cantonal | Santa Isabel (0109) | 69,99 masculinidad 20-39 | 69,9867 | `men_20_39 * 100.0 / women_20_39` (2.628 / 3.755 * 100) | Conteos exactos por edad quinquenal y sexo `canton/data.parquet` | **Verificado** |
| 5 | Cantonal | Biblián (0303) | 76,07 masculinidad 20-39 | 76,0684 | `men_20_39 * 100.0 / women_20_39` (5.963 / 7.839 * 100) | Conteos exactos por edad quinquenal y sexo `canton/data.parquet` | **Verificado** |
| 6 | Provincial | Morona Santiago (14) | 16,94 por mil | 16,9396 | `emigrants * 1000.0 / population` (3.261 / 192.508 * 1000) | Infografía Provincial INEC Morona Santiago: 16,9 por mil | **Verificado** |
| 7 | Cantonal | Daule (0906) | 34.664 personas de otro cantón | 34.664 | `sum(residence_other_canton_5) FROM cross_counts_v1b2` | Agregado aditivo verificado Fase 1B-2 | **Verificado** |

---

## 3. Historia 3: "La ciudad vacía"

| Paso | Nivel | Entidad | Cifra Citada | Valor Calculado Exacto | Consulta SQL DuckDB | Contraste Fuente Oficial INEC | Estado |
|:---:|:---:|---|---|---:|---|---|:---:|
| 1 | Nacional | Ecuador | 11,63% desocupadas | 11,6261 % | `V0201=4 * 100.0 / sum(V0201)` (766.776 / 6.595.318 * 100) | docs/qa/validacion_inec.md: 11,626% nacional V0201=4 | **Idéntico (100%)** |
| 1 | Nacional | Ecuador | 766.776 viviendas desocupadas | 766.776 | `sum(n) FILTER (WHERE variable='V0201' AND category='4')` | Tabulado oficial CPV 2022 vivienda.xlsx | **Idéntico (100%)** |
| 1 | Nacional | Ecuador | 6.595.318 viviendas particulares válidas | 6.595.318 | `sum(n) FILTER (WHERE variable='V0201')` | Tabulado oficial CPV 2022 vivienda.xlsx | **Idéntico (100%)** |
| 2 | Cantonal | Cañar (0302) | 26,41% desocupadas | 26,4081 % | `V0201=4 * 100.0 / sum(V0201)` (2.621 / 9.925 * 100) | Tabulado oficial cantonal vivienda.xlsx | **Verificado** |
| 2 | Cantonal | Suscal (0307) | 23,12% desocupadas | 23,1240 % | `V0201=4 * 100.0 / sum(V0201)` (567 / 2.452 * 100) | Tabulado oficial cantonal vivienda.xlsx | **Verificado** |
| 3 | Cantonal | Biblián (0303) | 21,57% desocupadas | 21,5695 % | `V0201=4 * 100.0 / sum(V0201)` (5.346 / 24.785 * 100) | Tabulado oficial cantonal vivienda.xlsx | **Verificado** |
| 3 | Cantonal | Gualaceo (0103) | 19,88% desocupadas | 19,8801 % | `V0201=4 * 100.0 / sum(V0201)` (4.177 / 21.011 * 100) | Tabulado oficial cantonal vivienda.xlsx | **Verificado** |
| 4 | Cantonal | Quito (1701) | Moran I = 0,389 (p < 0,001) | 0,38898 | `spatial_v1b2/moran_canton.parquet` (indicator='vacancy') | Matriz espacial analítica 1B-2 | **Verificado** |
| 5 | Sectorial | Guayaquil noroeste | Hacinamiento > 40% | 43,12 % - 51,80 % | `spatial_v1b2/lisa_sector.parquet` (indicator='overcrowding') | Agregado local LISA verificado 1B-2 | **Verificado** |
| 6 | Cantonal | Déleg (0306) | 2,42 viv/hogar | 2,4249 | `dwellings / households` (4.891 / 2.017) en `canton/data.parquet` | Conteos exactos agregados 1B-1 | **Verificado** |
| 6 | Cantonal | Sevilla de Oro (0112) | 2,36 viv/hogar | 2,3607 | `dwellings / households` (2.101 / 890) en `canton/data.parquet` | Conteos exactos agregados 1B-1 | **Verificado** |

---

## 4. Historia 4: "La brecha digital"

| Paso | Nivel | Entidad | Cifra Citada | Valor Calculado Exacto | Consulta SQL DuckDB | Contraste Fuente Oficial INEC | Estado |
|:---:|:---:|---|---|---:|---|---|:---:|
| 1 | Nacional | Ecuador | 86,98% hogares celular | 86,9840 % | `H1002=1 * 100.0 / sum(H1002)` (4.513.446 / 5.188.827 * 100) | Tabulado oficial CPV 2022 tic.xlsx | **Idéntico (100%)** |
| 1 | Nacional | Ecuador | 60,89% hogares internet fijo | 60,8921 % | `H1004=1 * 100.0 / sum(H1004)` (3.159.588 / 5.188.827 * 100) | indicators.yaml / validacion_inec.md: 60,892% | **Idéntico (100%)** |
| 1 | Nacional | Ecuador | 5.188.827 hogares clasificados | 5.188.827 | `sum(n) FILTER (WHERE variable='H1004')` | docs/qa/validacion_inec.md: 5.188.827 hogares H09 | **Idéntico (100%)** |
| 2 | Cantonal | Rumiñahui (1705) | 78,24% fijo en hogares | 78,2364 % | `H1004=1 * 100.0 / sum(H1004)` en `categories/canton` | Tabulado oficial cantonal tic.xlsx | **Verificado** |
| 2 | Cantonal | Cuenca (0101) | 75,30% fijo en hogares | 75,3010 % | `H1004=1 * 100.0 / sum(H1004)` en `categories/canton` | Tabulado oficial cantonal tic.xlsx | **Verificado** |
| 3 | Cantonal | Taisha (1409) | 14,82% fijo en hogares | 14,8215 % | `H1004=1 * 100.0 / sum(H1004)` en `categories/canton` | Tabulado oficial cantonal tic.xlsx | **Verificado** |
| 3 | Cantonal | Paján (1310) | 22,64% fijo en hogares | 22,6411 % | `H1004=1 * 100.0 / sum(H1004)` en `categories/canton` | Tabulado oficial cantonal tic.xlsx | **Verificado** |
| 4 | Cantonal | Paján (1310) | Brecha 57,84 puntos | 57,8412 | `pct_celular (80,48%) - pct_fijo (22,64%)` | Mismo universo de hogares `H1002` y `H1004` | **Verificado** |
| 4 | Cantonal | El Empalme (0908) | Brecha 51,71 puntos | 51,7130 | `pct_celular (87,74%) - pct_fijo (36,02%)` | Mismo universo de hogares `H1002` y `H1004` | **Verificado** |
| 5 | Parroquial | Iñaquito (170157) | 91,99% uso internet | 91,9866 % | `internet_person_5 * 100.0 / internet_response_5` en `cross_counts` | Agregado verificado Fase 1B-2 | **Verificado** |
| 5 | Parroquial | Pacto (170161) | 50,54% uso internet | 50,5356 % | `internet_person_5 * 100.0 / internet_response_5` en `cross_counts` | Agregado verificado Fase 1B-2 | **Verificado** |
| 6 | Cantonal | Quito jóvenes | 88,85% conectados | 88,8546 % | `digital_youth_yes * 100.0 / digital_youth_n` en `cross_counts` | Agregado verificado Fase 1B-2 | **Verificado** |
| 6 | Cantonal | Eloy Alfaro mayores | 8,72% conectados | 8,7232 % | `digital_senior_yes * 100.0 / digital_senior_n` en `cross_counts` | Agregado verificado Fase 1B-2 | **Verificado** |

---
*Fin del documento de verificación.*
