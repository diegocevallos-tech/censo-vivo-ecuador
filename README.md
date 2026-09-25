# Censo Vivo Ecuador

Portal experimental para explorar los resultados del VIII Censo de Población y VII de Vivienda 2022 del Ecuador. La **fase 0** documentó las fuentes, las variables y la compatibilidad de claves geográficas. La **fase 1A** publica conteos geográficos; los mapas e indicadores siguen en desarrollo.

## Estado del trabajo

Cada fase se desarrolla en una rama y se presenta en un pull request antes de iniciar la siguiente. El [plan de trabajo](https://github.com/diegocevallos-tech/censo-vivo-ecuador/milestones) contiene las tareas y sus criterios de verificación.

## Fuentes y uso de datos

La fuente estadística es el [INEC, Censo Ecuador 2022](https://www.censoecuador.gob.ec/data-censo-ecuador/). El [informe de la fase 0](docs/fase0_report.md) presenta el inventario de variables, la validación de los CSV con DuckDB y el match cartográfico por provincia. El código tiene licencia MIT; las condiciones aplicables a los datos se explican en [DATA_LICENSE.md](DATA_LICENSE.md).

Este repositorio público publica únicamente **estadísticas agregadas**. No se distribuyen registros de personas ni hogares. El [informe de conteos](docs/fase1a_report.md) y el [esquema](docs/schema.md) explican los niveles, las variables y la QA. Los datos derivados completos se guardan en el [Release público `data-derived-v1a`](https://github.com/diegocevallos-tech/censo-vivo-ecuador/releases/tag/data-derived-v1a); git conserva el [manifiesto con SHA256](data/DERIVED_MANIFEST.json) y una muestra pequeña para desarrollo. El despliegue restaura los agregados verificados en Pages. Ningún workflow público tiene acceso a los originales.

## Reproducibilidad

Los originales verificados se recuperan desde un Release **privado** de la misma cuenta con `python pipeline/fetch_raw.py`, tras autenticarse con `gh auth login`. `data/MANIFEST.json` registra URL, fecha, tamaño y SHA256; el script comprueba cada archivo. Se necesita espacio local suficiente para los ZIP y su extracción. Ninguna cifra del censo se simula para desarrollar el portal.

El flujo privado de Actions usa únicamente el `GITHUB_TOKEN` automático de su propio repositorio; no hay un PAT compartido ni secret en el repositorio público. Para comprobar el entorno sin datos privados, el [workflow del devcontainer](.github/workflows/devcontainer.yml) construye la imagen y ejecuta pruebas de Python y el build web en cada PR. Se probó también en Codespaces `basicLinux32gb` (2 CPU, 8 GB RAM, 32 GB de almacenamiento): configuración y comprobaciones en **9 minutos**. Las versiones y resultados constan en el [informe de fase 0](docs/fase0_report.md).
