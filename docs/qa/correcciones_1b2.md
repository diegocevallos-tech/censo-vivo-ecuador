# Correcciones de la auditoría 1B-2

La [auditoría independiente](auditoria_1b2.md) se atiende en el PR `fix/1b2-auditoria`. La rama de la auditoría permanece intacta.

## Estadística espacial

- Se define una sola matriz de contigüidad Queen con todos los sectores con geometría de cada cantón. Los polígonos aislados se enlazan a su centroide vecino más próximo de forma simétrica. La matriz se reutiliza para los seis índices; las tasas con denominador menor a 30 se reemplazan por la media cantonal ponderada y se identifican como regularizadas.
- Moran global y LISA usan 999 permutaciones, semilla 2022. Los seis índices son envejecimiento, educación superior 25+, hogares sin internet fijo, hacinamiento, viviendas particulares desocupadas y soledad potencial 65+.
- La disimilitud educativa mantiene sus conteos exactos. El uso de Queen cambia los resultados de Moran y LISA respecto de los publicados en `data-derived-v2a`; el siguiente Release debe llevar los nuevos binarios y tablas.

## Tipología y gemelos

- Ocho supergrupos y dos grupos anidados por supergrupo producen 16 tipos. Se conservan los diagnósticos silhouette/gap y se registra su elección diagnóstica; la jerarquía de 16 tipos responde al alcance fijado para el portal.
- Los vectores de 40 características se calculan sobre conteos exactos de sector, parroquia y cantón. La búsqueda usa similitud coseno y permite excluir el mismo cantón.

## Datos de diáspora

`03b_mobility.py` agrega Emigración por cantón × sexo × edad de salida × país de destino. La prueba local produjo 32.123 filas agregadas, 46.081 bytes y 124.992 emigrantes, exactamente los mismos que el perfil parroquial. No incluye identificadores personales.
