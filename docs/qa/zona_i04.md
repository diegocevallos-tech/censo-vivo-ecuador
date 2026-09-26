# Zona censal I04 · QA

Fuente estadística: [conteos de sector](../../pipeline/13_zona.py) del CPV 2022. Geometría: capa oficial `zon_a` del Marco 2021, unida por `I01`–`I04`. `geom_version` permanece `marco-2021`; los conteos de sector y manzana no se modifican.

| Control | Resultado |
| --- | ---: |
| Sectores censales de origen | 53.513 |
| Zonas estadísticas distintas | 5.929 |
| Población en zonas y sectores | 16.938.986 |
| Polígonos de zona en el Marco 2021 | 5.888 |
| Polígonos con clave estadística | 5.885 |
| Zonas estadísticas sin polígono | 44 |
| Población de zonas sin polígono, conservada en agregados | 5.138 |
| Viviendas de zonas sin polígono, conservadas en agregados | 3.329 |
| Claves `888` entre las zonas sin polígono | 39 |
| Diferencia sector → zona → parroquia, en cada columna numérica | 0 |
| Indicadores precalculados en zona | 45 |

Los 44 códigos sin polígono no se dibujan ni se estiman espacialmente. Permanecen en los totales de parroquia, cantón, provincia y nación. Las 1.852 manzanas sin polígono siguen asignadas a su sector de origen; al sumar sector a zona no se pierden.

## Tamaño del paquete de Pages

| Grupo | v2c | v2d | Límite |
| --- | ---: | ---: | ---: |
| Conteos y Parquet | 149.130.353 B | 149.529.581 B | 150.000.000 B |
| PMTiles | 154.831.429 B | 164.125.611 B | 450.000.000 B |
| Chunks e índices binarios | 132.870.239 B | 134.293.256 B | 150.000.000 B |
| Total de datos | 436.832.021 B | 447.948.448 B | 800.000.000 B, incluida la reserva de app |

El nuevo Parquet ancho de zona ocupa 397.085 B; el PMTiles de zona, 9.294.084 B; el índice de indicadores, 1.422.971 B. El detalle categórico y los cruces de zona se generan de forma reproducible en `data/interim/` para calcular el índice, pero no se duplican en Pages: pueden derivarse por suma de los agregados publicados de menor nivel. Así se cumple el límite de 150 MB para Parquet sin omitir población ni indicadores del mapa.

Pruebas: [`verify_release_integrity.py`](../../pipeline/verify_release_integrity.py) dio diferencia cero de sector a zona y de zona a parroquia en todos los campos; [`09_qa_indicator_map.py`](../../pipeline/09_qa_indicator_map.py) comprobó las 5.929 claves y sus 45 indicadores; el E2E de tooltip local cubrió provincia, cantón, parroquia, zona, sector y dato heredado por `min_level` sin errores de consola.
