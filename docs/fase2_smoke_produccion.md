# FASE 2 · Smoke test en producción

URL pública: <https://diegocevallos-tech.github.io/censo-vivo-ecuador/>. Se probó el commit `988b78d` tras el [despliegue de Pages](https://github.com/diegocevallos-tech/censo-vivo-ecuador/actions/runs/36211854596) del 26 de septiembre de 2026. El script reproducible es [`web/scripts/smoke-production.mjs`](../web/scripts/smoke-production.mjs) y la salida detallada está en [`capturas/smoke-results.json`](capturas/smoke-results.json).

## Carga inicial y Lighthouse

| Entorno | Rendimiento | Accesibilidad | LCP | FCP | Peso indicado por Lighthouse |
| --- | ---: | ---: | ---: | ---: | ---: |
| Escritorio | 91 | 94 | 1,26 s | 1,12 s | 493.074 bytes |
| Móvil | 47 | 94 | 4,89 s | 4,44 s | 491.430 bytes |

Chrome CDP registró **487.698 bytes descargados en la primera carga** de escritorio, desde la navegación hasta cinco segundos después. Lighthouse 12.8.2 usó el preset de escritorio y el perfil móvil con su simulación de red/CPU. Los reportes completos están en [`lighthouse-escritorio.json`](capturas/lighthouse-escritorio.json) y [`lighthouse-movil.json`](capturas/lighthouse-movil.json). Lighthouse produjo ambos reportes válidos (`runtimeError: null`); su CLI en Windows devolvió `EPERM` al intentar limpiar el perfil temporal de Chrome después de guardarlos.

La meta móvil de rendimiento ≥85 y carga inicial <3 s aún no se cumple. Queda registrada en la [issue #51](https://github.com/diegocevallos-tech/censo-vivo-ecuador/issues/51).

## Interacciones verificadas

| Caso | Resultado |
| --- | --- |
| País → manzana mediante zoom | Ecuador → provincia → cantón → parroquia → sector censal → manzana, cambio automático |
| Círculo Quito | 18 manzanas, estimado 69,8 %; p95 del cálculo de vista previa 0,3 ms |
| Círculo Guayaquil | 25 manzanas, estimado 59,5 %; p95 0,3 ms |
| Círculo rural | Fallback a sector censal, 1 unidad, estimado 100 %; p95 0,2 ms |
| Lazo | 9 unidades |
| Multiselección | 8 unidades |
| Catálogo | 30 indicadores recorridos a nivel cantón, sin errores de consola |
| URL compartida | `aging_index` y la cámara en cantón se restauraron al abrirla de nuevo |
| Errores JavaScript/consola | 0 en todo el recorrido |

Capturas: [inicio escritorio](capturas/inicio-escritorio.png), [inicio móvil](capturas/inicio-movil.png), [zoom manzana](capturas/zoom-manzana.png), [círculo Quito](capturas/circulo-quito.png), [Guayaquil](capturas/circulo-guayaquil.png), [rural](capturas/circulo-rural.png), [lazo](capturas/lazo.png), [multiselección](capturas/multiseleccion.png) y [URL restaurada](capturas/url-restaurada.png).

El porcentaje estimado corresponde a unidades cortadas por el borde y ponderadas por área. El fallback rural usa el sector cuando no hay manzanas visibles en la vista. La medición p95 cubre el cálculo de vista previa, no demuestra 60 cuadros por segundo de extremo a extremo.
