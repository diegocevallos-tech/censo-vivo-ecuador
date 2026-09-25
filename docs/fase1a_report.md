# Fase 1A: conteos geográficos y publicación controlada

## Fuentes, geometría y flujo

Los cinco CSV oficiales MANLOC del CPV 2022 se restauran desde `data-raw-v1` del [almacén privado](https://github.com/diegocevallos-tech/censo-vivo-ecuador-raw) y se comprueban con [`data/MANIFEST.json`](../data/MANIFEST.json). [`01_filter_to_parquet.py`](../pipeline/01_filter_to_parquet.py) crea intermedios privados con registros individuales; [`02_counts_by_unit.py`](../pipeline/02_counts_by_unit.py) calcula los agregados completos; [`07_qa.py`](../pipeline/07_qa.py) comprueba la aditividad y los totales oficiales; [`02b_pack_public.py`](../pipeline/02b_pack_public.py) aplica supresión y compresión antes de publicar. Los originales y los intermedios permanecen fuera de git y de Pages.

La unidad fina es manzana cuando existe polígono. Las localidades rurales dispersas, los códigos reservados `888` y las **1.852 manzanas reales sin polígono** contribuyen a su sector. Esas manzanas aportan **36.040 personas** y **18.701 viviendas**; ninguna se descarta. Los conteos se unen a la cartografía solo por clave y llevan `geom_version: "marco-2021"`. Una cartografía nueva requiere regenerar tiles, sin recalcular los conteos.

| Nivel | Unidades |
| --- | ---: |
| Fino, manzana o sector | 231.464 |
| Sector | 53.513 |
| Parroquia | 1.042 |
| Cantón | 221 |
| Provincia | 24 |
| Nación | 1 |

El [esquema](schema.md) identifica 59 conteos numéricos, las categorías de las cinco tablas MANLOC, autoidentificación desde SECTOR, fuentes y poblaciones de referencia. Los campos densos usan formato ancho. Las categorías dispersas usan formato largo con un codebook Parquet y enteros `uint8`, `uint16` o `uint32` según el máximo real. Todos los Parquet públicos usan zstd. No hay claves de persona, hogar o vivienda ni cruces categóricos por individuo.

## Tamaño y ubicación de los datos

La tabla compara el artifact anterior del PR con el paquete compactado. La [tabla por archivo](qa/size_comparison.csv) incluye cada ruta, sus bytes antes y después y el total, incluso archivos retirados o nuevos. El paquete final se distribuye en el [Release público `data-derived-v1a`](https://github.com/diegocevallos-tech/censo-vivo-ecuador/releases/tag/data-derived-v1a); [`data/DERIVED_MANIFEST.json`](../data/DERIVED_MANIFEST.json) registra tamaño, SHA256 y asset de cada archivo. Los únicos datos versionados para desarrollo son una [muestra agregada de 221 cantones](../web/public/data/sample/canton.parquet) de 36.625 bytes.

| Grupo | Antes, bytes | Después, bytes |
| --- | ---: | ---: |
| Categorías Parquet | 461.373.636 | 108.762.811 |
| Conteos anchos Parquet | 9.115.617 | 8.516.767 |
| Esquemas y QA | 10.041 | 25.611 |
| **Total de datos derivados** | **470.499.294** | **117.305.189** |

Los tres assets comprimidos del Release ocupan **115.862.670 bytes** en conjunto; el mayor, **59.520.338 bytes**. El archivo individual para Pages más grande mide **15.300.498 bytes**. Los conteos están bajo el presupuesto de **150 MB**; [`config.yaml`](../config.yaml) reserva 450 MB para tiles, 150 MB para chunks binarios y 20 MB para la app, con objetivo de 800 MB para el sitio completo. Tiles y chunks corresponden a fases posteriores y no se incluyen en este paquete.

La rama del PR se reescribió a partir de `origin/main` para retirar del historial propuesto los archivos derivados grandes. El chequeo `git rev-list --objects origin/main..HEAD | git cat-file --batch-check` no encuentra blobs mayores de 1 MB. Git ignora `web/public/data/**`, salvo la muestra. [`ci.yml`](../.github/workflows/ci.yml) prueba la muestra y falla si el manifiesto excede el presupuesto, un archivo excede 95 MB o un Markdown contiene rutas locales absolutas. [`deploy.yml`](../.github/workflows/deploy.yml) restaura los assets del Release público con el token automático del propio repositorio, verifica los SHA256 y los incorpora a `dist/data`; ningún workflow público lee microdatos ni el repositorio privado.

El [workflow privado de generación](https://github.com/diegocevallos-tech/censo-vivo-ecuador-raw/actions/runs/36091057990) terminó correctamente. Se descargó su artifact agregado, se comprobó el esquema y se comparó el contenido de sus **151 Parquet** y dos JSON con la ejecución local; los valores fueron equivalentes. La diferencia de 772 bytes en el paquete total local se debe a la representación física de Parquet y JSON. El Release público se forma con los archivos del workflow privado, más el `fase0_qa.json` de Fase 0 previamente verificado por SHA256.

## Control estadístico

La [metodología](metodologia.md) explica supresión primaria y secundaria. Una manzana con menos de 10 personas o menos de 3 viviendas ocupadas publica solo sus tres totales: población, viviendas y hogares. Sus desagregaciones permanecen en sector y lleva `detalle_en_sector`. En las otras manzanas se retienen las celdas positivas de 1 o 2; se retiene una segunda celda cuando existe un único valor primariamente suprimido que podría obtenerse restando del sector. Las banderas distinguen detalle retenido de ceros reales.

| Provincia | Manzanas | Sin detalle | Población afectada | Viviendas afectadas |
| --- | ---: | ---: | ---: | ---: |
| 01 | 7.493 | 1.242 | 5.428 | 4.590 |
| 02 | 2.010 | 317 | 1.623 | 1.058 |
| 03 | 3.323 | 683 | 2.890 | 2.175 |
| 04 | 2.471 | 311 | 1.589 | 843 |
| 05 | 3.659 | 523 | 2.491 | 1.628 |
| 06 | 5.804 | 1.048 | 5.372 | 3.788 |
| 07 | 12.332 | 1.544 | 7.700 | 4.373 |
| 08 | 7.190 | 796 | 4.141 | 3.464 |
| 09 | 53.052 | 4.161 | 19.148 | 15.085 |
| 10 | 6.417 | 929 | 5.038 | 2.579 |
| 11 | 6.591 | 1.295 | 6.175 | 4.036 |
| 12 | 10.873 | 968 | 5.079 | 2.640 |
| 13 | 22.491 | 3.370 | 17.572 | 10.993 |
| 14 | 2.908 | 786 | 3.696 | 2.349 |
| 15 | 1.642 | 272 | 1.305 | 819 |
| 16 | 1.227 | 214 | 1.140 | 656 |
| 17 | 28.096 | 1.779 | 8.393 | 6.030 |
| 18 | 5.470 | 727 | 3.597 | 2.298 |
| 19 | 1.980 | 414 | 1.991 | 1.133 |
| 20 | 717 | 120 | 643 | 374 |
| 21 | 3.202 | 524 | 2.786 | 1.740 |
| 22 | 2.993 | 459 | 2.520 | 1.393 |
| 23 | 7.203 | 651 | 3.258 | 1.775 |
| 24 | 10.229 | 2.767 | 10.399 | 14.257 |
| **Total** | **209.373** | **25.900** | **123.974** | **90.076** |

En los campos anchos se retuvieron **2.726.346 celdas primarias** y **214.705 secundarias**; en categorías, **37.612.668 primarias** y **2.880.935 secundarias**. Estos conteos describen celdas, no personas distintas. La supresión no modifica los totales de sector o superiores.

## QA de integridad

El resultado completo `counts/v1a/qa.json` está dentro del Release público. La QA compara los 59 campos y cada categoría entre niveles completos, las pirámides y `geom_version`. Los 221 cantones y 24 provincias coinciden exactamente con la desagregación oficial CANTÓN para población y viviendas. Las cinco tablas fuente aportan 16.938.986 personas, 6.611.555 viviendas, 5.193.548 hogares, 124.992 emigrantes y 250.746 defunciones. La comparación externa con CANTÓN cubre población y viviendas; los otros universos se controlan mediante aditividad y total de registros fuente.

| Comprobación | Resultado |
| --- | ---: |
| Población nacional | 16.938.986 |
| Viviendas nacionales | 6.611.555 |
| Diferencia de campos numéricos entre niveles | 0 |
| Diferencia de categorías entre niveles | 0 |
| Cantones y provincias distintos de los CSV oficiales | 0 |
| Unidades cuya pirámide no suma la población | 0 |

El empaquetador vuelve a comparar los conteos y las categorías desde sector hasta nación, rechaza celdas finas positivas menores que 3 y rechaza cualquier desagregación publicada en una manzana marcada `detalle_en_sector`. El [verificador de artefactos](../pipeline/verify_public_artifacts.py) inspecciona extensiones, columnas y tamaños antes de preparar el Release.

