# Parroquias urbanas municipales · asignación por centroide

La geometría de referencia proviene de seis servicios oficiales de los GAD.
Cada manzana del Marco 2021 se asigna al polígono municipal que contiene su
centroide. Las estadísticas son sumas de agregados por manzana del CPV 2022;
**la parroquia urbana municipal no es una unidad censal del INEC**.
Las manzanas sin polígono siguen en su sector censal y no se adjudican a
ninguna parroquia urbana. Las manzanas fuera de los límites municipales
permanecen en su parroquia censal oficial.

El paquete agregado quedó en el [prerelease público `data-derived-v2f`](https://github.com/diegocevallos-tech/censo-vivo-ecuador/releases/tag/data-derived-v2f), pendiente de aprobación para producción. Contiene 401 archivos (424.962.177 B) después de extraer seis assets; añade 483.672 B a v2e y mantiene los conteos/Parquet en 126.136.244 B, por debajo del presupuesto de 150 MB. Los seis GeoJSON originales se conservaron como assets del Release privado `data-raw-v1`; sus SHA256 constan en [`data/MUNICIPAL_SOURCES.json`](../../data/MUNICIPAL_SOURCES.json).

| Ciudad | Parroquias | Manzanas / total | Población / cabecera | Fuera | Sin geometría¹ |
| --- | ---: | ---: | ---: | ---: | ---: |
| Quito | 32 | 16,888 / 16,907 | 1,763,309 / 1,776,364 | 2,887 | 10,168 |
| Guayaquil | 15 | 27,339 / 30,580 | 2,470,928 / 2,665,392 | 182,722 | 11,742 |
| Cuenca | 15 | 4,047 / 4,049 | 360,150 / 361,524 | 209 | 1,165 |
| Loja | 6 | 2,897 / 2,910 | 201,763 / 214,296 | 400 | 12,133 |
| Ambato | 8 | 1,843 / 2,235 | 156,855 / 188,338 | 24,991 | 6,492 |
| Riobamba | 5 | 2,811 / 2,922 | 173,287 / 188,891 | 4,678 | 10,926 |

## Iñaquito

La fuente municipal identifica **Iñaquito (170112)**. El cruce asignó
**327 manzanas** con **55,879 personas**;
6,455 tienen 0–14 años y 9,648 tienen
65 años o más. El índice de envejecimiento es
**149.47 personas de 65+ por cada 100 de 0–14**
(100 × 9,648 / 6,455). Es un agregado
por centroides sobre un **límite no censal**, no una cifra oficial del INEC
para la parroquia urbana.

## QA y alcance

- **81 parroquias**: Quito 32, Guayaquil 15, Cuenca 15, Loja 6, Ambato 8 y
  Riobamba 5. Guayaquil devuelve 16 polígonos pero 15 nombres distintos;
  Tarqui tiene dos partes. El informe de fuentes dice 14 nombres únicos,
  discrepancia que aquí se corrige sin editar aquel documento.
- Ninguna manzana se asigna a dos polígonos. En cada ciudad, población asignada
  + fuera del límite + población sin geometría de manzana asignable = total
  oficial de la cabecera,
  **diferencia cero**. Los conteos por parroquia municipal coinciden con la
  tabla resumida; todos los SHA256 originales coinciden.
- ¹ «Sin geometría» incluye manzanas sin polígono y población que permanece
  solo en el sector disperso; no significa que todas sean manzanas sin match.
- La tabla manzana→parroquia municipal se conserva como intermedio privado.
  El navegador recibe únicamente geometrías de referencia y agregados por
  parroquia municipal. No se publican registros por persona.

## Fuentes verificadas

- Quito: [https://geoquito.quito.gob.ec/server/rest/services/Hosted/parroquias_ref_a/FeatureServer/0/query](https://geoquito.quito.gob.ec/server/rest/services/Hosted/parroquias_ref_a/FeatureServer/0/query) (SHA256 `bd999bfa19ab754010a96581247e402f408ab52938422bdf87cd8dc6b64f2e9e`, 2,677,904 B).
- Guayaquil: [https://geoportalcat.guayaquil.gob.ec/arcgis/rest/services/Geoportal_Actualizado/GEOPORTAL_ACTUALIZADO/MapServer/9/query](https://geoportalcat.guayaquil.gob.ec/arcgis/rest/services/Geoportal_Actualizado/GEOPORTAL_ACTUALIZADO/MapServer/9/query) (SHA256 `66e1afb37f144e491bb9ec46cfe36d0beabeb78edf08a2295964c1ea05afad38`, 341,849 B).
- Cuenca: [https://ide.cuenca.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=dgpt_limites:limite_parroquias_urbanas&outputFormat=application/json](https://ide.cuenca.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=dgpt_limites:limite_parroquias_urbanas&outputFormat=application/json) (SHA256 `f6835e2c15a57ad37e9ee080f7768b881d32975532768c475b0042b2cb78fe50`, 552,934 B).
- Loja: [http://sil.loja.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=pugs_2023_2033:limites_parroquias_urbanas_2023_2033&outputFormat=application/json](http://sil.loja.gob.ec/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=pugs_2023_2033:limites_parroquias_urbanas_2023_2033&outputFormat=application/json) (SHA256 `d598a1e254d93d3cffc1bd75d0a4c6bfce35da04e325779502003f0232a25dee`, 115,697 B).
- Ambato: [https://arcgis.ambato.gob.ec/mapas/rest/services/MXD/AMBATO/MapServer/1/query](https://arcgis.ambato.gob.ec/mapas/rest/services/MXD/AMBATO/MapServer/1/query) (SHA256 `45c2a0bce68aa8663ea82768ed05675981a63d79be35865dc4904ed77af960b4`, 247,718 B).
- Riobamba: [https://services9.arcgis.com/WR0heBS35BiLFAuA/arcgis/rest/services/parroquias_urbanas/FeatureServer/0/query](https://services9.arcgis.com/WR0heBS35BiLFAuA/arcgis/rest/services/parroquias_urbanas/FeatureServer/0/query) (SHA256 `3190e34f63352ba70385984aeeca39e41c4ba8ae6cceaea02862c5fa2193c344`, 56,399 B).
