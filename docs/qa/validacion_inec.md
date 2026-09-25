# Validación externa con cifras del CPV 2022 del INEC

Se usan los Parquet agregados exactos del Release `data-derived-v1b1`; este script no abre filas por persona. El valor oficial de hogares corresponde a hogares clasificados (`H09=1..6`); el conteo operativo `core:households` incluye también registros sin clasificación. Las fichas provinciales y el boletín nacional se citan en cada fila.

| Área | Indicador | Valor propio | Valor oficial | Fuente INEC | Diferencia (propio − oficial) |
| --- | --- | ---: | ---: | --- | ---: |
| Nacional | Población censada (personas) | 16,938,986 | 16,938,986 | [INEC](https://www.censoecuador.gob.ec/public/Boletin_Nacional.htm) | 0 |
| Nacional | Hogares clasificados H09 (hogares) | 5,188,827 | 5,188,827 | [INEC](https://www.censoecuador.gob.ec/public/Boletin_Nacional.htm) | 0 |
| Nacional | Viviendas ocupadas V0201=1+2 (viviendas) | 5,062,650 | 5,062,650 | [INEC](https://www.censoecuador.gob.ec/public/Boletin_Nacional.htm) | 0 |
| Nacional | Personas por hogar (personas/hogar) | 3.262 | 3.300 | [INEC](https://www.censoecuador.gob.ec/public/Boletin_Nacional.htm) | -0.038 |
| Nacional | Edad mediana aproximada (años) | 29.182 | 29.000 | [INEC](https://www.censoecuador.gob.ec/public/Boletin_Nacional.htm) | 0.182 |
| Nacional | Razón de masculinidad (hombres/100 mujeres) | 95.004 | 95.000 | [INEC](https://www.censoecuador.gob.ec/public/Boletin_Nacional.htm) | 0.004 |
| Nacional | Hogares unipersonales (%) | 16.611 | 16.600 | [INEC](https://www.censoecuador.gob.ec/public/Boletin_Nacional.htm) | 0.011 |
| Nacional | Tenencia propia (%) | 61.050 | 61.000 | [INEC](https://www.censoecuador.gob.ec/public/Boletin_Nacional.htm) | 0.050 |
| Nacional | Tenencia arrendada (%) | 20.929 | 20.900 | [INEC](https://www.censoecuador.gob.ec/public/Boletin_Nacional.htm) | 0.029 |
| Nacional | Autoidentificación mestiza (%) | 77.468 | 77.500 | [INEC](https://www.censoecuador.gob.ec/public/Boletin_Nacional.htm) | -0.032 |
| Nacional | Mujeres (%) | 51.281 | 51.300 | [INEC](https://www.censoecuador.gob.ec/public/Boletin_Nacional.htm) | -0.019 |
| Pichincha | Población censada (personas) | 3,089,473 | 3,089,473 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Pichincha.pdf) | 0 |
| Pichincha | Hogares clasificados H09 (hogares) | 994,599 | 994,599 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Pichincha.pdf) | 0 |
| Pichincha | Viviendas ocupadas V0201=1+2 (viviendas) | 983,801 | 983,801 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Pichincha.pdf) | 0 |
| Pichincha | Personas por hogar (personas/hogar) | 3.104 | 3.100 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Pichincha.pdf) | 0.004 |
| Pichincha | Edad mediana aproximada (años) | 31.921 | 31.000 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Pichincha.pdf) | 0.921 |
| Pichincha | Razón de masculinidad (hombres/100 mujeres) | 93.223 | 93.000 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Pichincha.pdf) | 0.223 |
| Pichincha | Hogares unipersonales (%) | 17.263 | 17.200 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Pichincha.pdf) | 0.063 |
| Pichincha | Tenencia propia (%) | 55.893 | 55.900 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Pichincha.pdf) | -0.007 |
| Pichincha | Tenencia arrendada (%) | 32.524 | 32.500 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Pichincha.pdf) | 0.024 |
| Pichincha | Autoidentificación mestiza (%) | 87.400 | 87.400 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Pichincha.pdf) | 0.000 |
| Pichincha | Mujeres (%) | 51.754 | 51.800 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Pichincha.pdf) | -0.046 |
| Guayas | Población censada (personas) | 4,391,923 | 4,391,923 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Guayas.pdf) | 0 |
| Guayas | Hogares clasificados H09 (hogares) | 1,319,163 | 1,319,163 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Guayas.pdf) | 0 |
| Guayas | Viviendas ocupadas V0201=1+2 (viviendas) | 1,289,733 | 1,289,733 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Guayas.pdf) | 0 |
| Guayas | Personas por hogar (personas/hogar) | 3.327 | 3.300 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Guayas.pdf) | 0.027 |
| Guayas | Edad mediana aproximada (años) | 29.124 | 29.000 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Guayas.pdf) | 0.124 |
| Guayas | Razón de masculinidad (hombres/100 mujeres) | 96.276 | 96.000 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Guayas.pdf) | 0.276 |
| Guayas | Hogares unipersonales (%) | 16.831 | 16.800 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Guayas.pdf) | 0.031 |
| Guayas | Tenencia propia (%) | 67.402 | 67.400 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Guayas.pdf) | 0.002 |
| Guayas | Tenencia arrendada (%) | 17.120 | 17.100 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Guayas.pdf) | 0.020 |
| Guayas | Autoidentificación mestiza (%) | 81.026 | 81.000 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Guayas.pdf) | 0.026 |
| Guayas | Mujeres (%) | 50.949 | 50.900 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_Guayas.pdf) | 0.049 |
| Azuay | Población censada (personas) | 801,609 | 801,609 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_azuay.pdf) | 0 |
| Azuay | Hogares clasificados H09 (hogares) | 246,867 | 246,867 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_azuay.pdf) | 0 |
| Azuay | Viviendas ocupadas V0201=1+2 (viviendas) | 242,168 | 242,168 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_azuay.pdf) | 0 |
| Azuay | Personas por hogar (personas/hogar) | 3.244 | 3.200 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_azuay.pdf) | 0.044 |
| Azuay | Edad mediana aproximada (años) | 30.155 | 30.000 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_azuay.pdf) | 0.155 |
| Azuay | Razón de masculinidad (hombres/100 mujeres) | 88.530 | 89.000 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_azuay.pdf) | -0.470 |
| Azuay | Hogares unipersonales (%) | 16.846 | 16.800 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_azuay.pdf) | 0.046 |
| Azuay | Tenencia propia (%) | 58.649 | 58.700 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_azuay.pdf) | -0.051 |
| Azuay | Tenencia arrendada (%) | 26.979 | 27.000 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_azuay.pdf) | -0.021 |
| Azuay | Autoidentificación mestiza (%) | 94.673 | 94.700 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_azuay.pdf) | -0.027 |
| Azuay | Mujeres (%) | 53.042 | 53.000 | [INEC](https://www.censoecuador.gob.ec/wp-content/uploads/2024/01/Info_azuay.pdf) | 0.042 |

## Diferencias que superan 0,5 puntos/unidades o 1 % relativo

- **Nacional, Personas por hogar**: propio 3.2615, INEC 3.3000, diferencia -0.0385. El INEC publica este promedio con un decimal: el error relativo calculado contra la cifra redondeada no implica discrepancia de conteos. Además, el catálogo usa población total (incluida población colectiva) y todos los hogares operativos, no solo personas de hogares particulares.
- **Pichincha, Edad mediana aproximada**: propio 31.9206, INEC 31.0000, diferencia +0.9206. Mediana interpolada sobre grupos quinquenales de edad frente a la mediana calculada por el INEC con edad simple; se conserva el rótulo «aproximada».
- **Azuay, Personas por hogar**: propio 3.2439, INEC 3.2000, diferencia +0.0439. El INEC publica este promedio con un decimal: el error relativo calculado contra la cifra redondeada no implica discrepancia de conteos. Además, el catálogo usa población total (incluida población colectiva) y todos los hogares operativos, no solo personas de hogares particulares.

## Definiciones que no se deben equiparar

- **Viviendas desocupadas:** el catálogo usa solo `V0201=4` (desocupada). El boletín nacional agrupa `V0201=4+5` (incluye en construcción): 11,626 % frente a 13,925 %. Es una diferencia de definición de 2,299 puntos, no una pérdida de registros. La fórmula del catálogo se mantiene explícita.
- **Internet:** el 69,4 % del [boletín nacional](https://www.censoecuador.gob.ec/public/Boletin_Nacional.htm) mide uso individual desde los 5 años. `fixed_internet` mide hogares con internet fijo (60,892 % nacional); no son el mismo indicador.
- **Analfabetismo 15+ y jefatura femenina:** el INEC publica 3,7 % y 38,5 % nacionales en el mismo boletín. El agregado de 1B-1 carece de edad × alfabetismo y parentesco × sexo; quedan pendientes para 1B-2 y no se han fabricado valores propios.
- **Viviendas ocupadas:** los recuentos de las fichas provinciales coinciden con `V0201=1+2`. Algunas fichas los describen como «con personas presentes»; la categoría 2 corresponde a ocupada con personas ausentes. Se valida el recuento, dejando constancia de esa imprecisión de rótulo.

## Reproducción

Desde la raíz del repo, tras descargar y verificar el Release agregado:

```sh
python pipeline/08_validate_inec.py \
  --base data/interim/exact_public/counts/v1b1 \
  --write docs/qa/validacion_inec.md
```
