# Nombres oficiales en el tooltip

## Fuente y cobertura

Los nombres provienen de `CODIFICACIÓN_2022.xlsx`, clasificador geográfico del INEC; la geometría sigue siendo `marco-2021`. La unión usa exclusivamente la clave DPA. La tipografía se normaliza a Unicode NFC y tipo título; `de`, `del`, `la`, `las`, `los` y `y` quedan en minúscula salvo al inicio. El catálogo conserva `official_name`. Para el cantón 1701 presenta el nombre corto **Quito** y conserva **Distrito Metropolitano de Quito** como denominación oficial.

| Nivel | Unidades cartografiadas | Sin nombre | Claves faltantes |
|---|---:|---:|---|
| Provincia | 24 | 0 | Ninguna |
| Cantón | 221 | 0 | Ninguna |
| Parroquia | 1.042 | 0 | Ninguna |

La prueba de formato no halló mayúsculas sostenidas ni caracteres corruptos. Los PMTiles de los tres niveles incluyen la propiedad `name`; la metadata de los tres archivos se comprobó con `pmtiles verify` y `pmtiles show --metadata`. El buscador usa el mismo catálogo con 1.287 lugares y sus nombres normalizados.

La cartografía actual no publica una capa de **zona censal** ni una capa de **parroquias urbanas**. El clasificador contiene 270 códigos de parroquia urbana, pero ninguno se convirtió en límite censal ni se añadió al visor en esta corrección. El formateador ya reconoce `Zona <código>` y su ruta; si se publica una capa de parroquias urbanas más adelante, deberá identificarse como «límite no censal».

## Tooltip y selección

Hover y clic muestran nombre o código de la unidad, nivel, ruta superior, valor activo y población. Si el indicador solo existe a una escala superior, se muestra el dato de ese nivel y una nota gris. La población de manzanas sin polígono asignada al sector también lleva nota gris. El panel de análisis y la ruta de navegación usan el mismo formateador.

El [E2E local](../../web/scripts/test-tooltips.mjs) verificó hover en Pichincha, Quito, Calderón y el sector 170155025002; clic en Calderón y la ruta del panel; y la nota `min_level` de un indicador cantonal en el sector. **5 casos pasaron, 0 errores de navegador.** [Resultados JSON](../capturas/tooltip-results.json) y capturas: [provincia](../capturas/tooltip-provincia.png), [cantón](../capturas/tooltip-canton.png), [parroquia](../capturas/tooltip-parroquia.png), [sector](../capturas/tooltip-sector.png).

## Release y tamaño

El [Release público `data-derived-v2c`](https://github.com/diegocevallos-tech/censo-vivo-ecuador/releases/tag/data-derived-v2c) actualiza solo los PMTiles administrativos respecto de v2a. Los cinco assets se descargaron nuevamente y sus SHA256 coincidieron con [`DERIVED_MANIFEST.json`](../../data/DERIVED_MANIFEST.json).

| PMTiles | Antes (bytes) | Después (bytes) |
|---|---:|---:|
| Provincia | 110.732 | 114.623 |
| Cantón | 1.190.787 | 1.227.839 |
| Parroquia | 6.574.498 | 6.853.055 |

Datos restaurados para Pages: 436.832.021 bytes; tiles 154.831.429/450.000.000 bytes. El Release v2c conserva los conteos v2a. El PR de auditoría 1B-2 #53 sigue abierto y necesitará rebase y un Release combinado antes de fusionarse después de esta corrección.
