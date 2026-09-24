# Censo Vivo Ecuador

Portal experimental para explorar los resultados del VIII Censo de Población y VII de Vivienda 2022 del Ecuador. La **fase 0** documenta las fuentes, las variables y la compatibilidad de claves geográficas. Aún no se publican mapas ni indicadores.

## Estado del trabajo

Cada fase se desarrolla en una rama y se presenta en un pull request antes de iniciar la siguiente. El [plan de trabajo](https://github.com/diegocevallos-tech/censo-vivo-ecuador/milestones) contiene las tareas y sus criterios de verificación.

## Fuentes y uso de datos

La fuente estadística es el [INEC, Censo Ecuador 2022](https://www.censoecuador.gob.ec/data-censo-ecuador/). El [informe de la fase 0](docs/fase0_report.md) presenta el inventario de variables, la validación de los CSV con DuckDB y el match cartográfico por provincia. El código tiene licencia MIT; las condiciones aplicables a los datos se explican en [DATA_LICENSE.md](DATA_LICENSE.md).

Este repositorio público publicará únicamente **estadísticas agregadas**. No se distribuirán registros de personas ni hogares.

## Reproducibilidad

Los originales verificados se recuperan desde un Release **privado** de la misma cuenta con `python pipeline/fetch_raw.py`, tras autenticarse con `gh auth login`. `data/MANIFEST.json` registra URL, fecha, tamaño y SHA256; el script comprueba cada archivo. Se necesita espacio local suficiente para los ZIP y su extracción. Ninguna cifra del censo se simula para desarrollar el portal.
