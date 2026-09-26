/** Optional municipal reference boundaries, separate from INEC census units. */
import type { FeatureCollection } from 'geojson'
import * as maplibregl from 'maplibre-gl'
import type { Map as MapLibreMap, MapMouseEvent } from 'maplibre-gl'

type Language = 'es' | 'en'
interface Parish {
  urban_id: string
  name: string
  city: string
  source_code: string
  population: number
  blocks: number
  age_0_14: number
  age_65_plus: number
  aging_index: number | null
}
interface Package {
  geom_version: string
  parishes: Parish[]
}

const sourceId = 'municipal-urban'
const fillId = 'municipal-urban-fill'
const lineId = 'municipal-urban-line'

export function mountUrbanParishes(
  map: MapLibreMap, base: string, panel: HTMLElement,
  language: () => Language,
) {
  let loaded: Promise<void> | null = null
  let enabled = false
  let selected: string | null = null
  let hover: maplibregl.Popup | null = null
  let hoveredId = ''
  const parishes = new Map<string, Parish>()
  const number = (value: number) => new Intl.NumberFormat(language() === 'es' ? 'es-EC' : 'en-US')
    .format(value)
  const decimal = (value: number) => new Intl.NumberFormat(language() === 'es' ? 'es-EC' : 'en-US',
    { maximumFractionDigits: 1 }).format(value)

  async function load() {
    loaded ??= (async () => {
      const [boundaryResponse, countResponse] = await Promise.all([
        fetch(`${base}data/municipal-urban/v1/boundaries.geojson`),
        fetch(`${base}data/municipal-urban/v1/summary.json`),
      ])
      if (!boundaryResponse.ok || !countResponse.ok) {
        throw new Error(`Municipal layer: ${boundaryResponse.status}/${countResponse.status}`)
      }
      const boundaries = await boundaryResponse.json() as FeatureCollection
      const counts = await countResponse.json() as Package
      if (counts.geom_version !== 'marco-2021' || counts.parishes.length !== 81 ||
          boundaries.features.length !== 81) throw new Error('Unknown municipal layer version')
      for (const item of counts.parishes) parishes.set(item.urban_id, item)
      map.addSource(sourceId, { type: 'geojson', data: boundaries })
      map.addLayer({ id: fillId, type: 'fill', source: sourceId, minzoom: 8,
        paint: { 'fill-color': '#F5B82E', 'fill-opacity': 0.075 } })
      map.addLayer({ id: lineId, type: 'line', source: sourceId, minzoom: 8,
        paint: { 'line-color': '#F5B82E', 'line-width': 2, 'line-opacity': 0.9 } })
    })()
    try { await loaded } catch (error) { loaded = null; throw error }
  }

  function moveToTop() {
    if (enabled && map.getLayer(fillId)) {
      map.moveLayer(fillId)
      map.moveLayer(lineId)
    }
  }

  async function toggle(): Promise<boolean> {
    if (enabled) {
      enabled = false
      selected = null
      hover?.remove(); hover = null; hoveredId = ''
      if (map.getLayer(lineId)) map.removeLayer(lineId)
      if (map.getLayer(fillId)) map.removeLayer(fillId)
      if (map.getSource(sourceId)) map.removeSource(sourceId)
      loaded = null
      return false
    }
    await load()
    enabled = true
    moveToTop()
    return true
  }

  function atPoint(event: MapMouseEvent) {
    return enabled && map.getLayer(fillId) && map.getZoom() >= 8
      ? map.queryRenderedFeatures(event.point, { layers: [fillId] })[0] : undefined
  }

  function card(item: Parish): HTMLElement {
    const node = document.createElement('div')
    node.className = 'popup unit-popup municipal-popup'
    node.setAttribute('role', 'tooltip')
    const name = document.createElement('strong')
    name.className = 'unit-title'
    name.textContent = item.name
    const route = document.createElement('small')
    route.className = 'unit-context'
    route.textContent = item.city
    const metric = document.createElement('div')
    metric.className = 'unit-value'
    metric.textContent = `${language() === 'es' ? 'Índice de envejecimiento' : 'Ageing index'}: ${
      item.aging_index == null ? '—' : decimal(item.aging_index)}`
    const pop = document.createElement('div')
    pop.className = 'unit-population'
    pop.textContent = `${language() === 'es' ? 'Población asignada' : 'Assigned population'}: ${
      number(item.population)}`
    const note = document.createElement('div')
    note.className = 'unit-note'
    note.textContent = language() === 'es'
      ? 'Límite no censal · manzanas asignadas por centroide'
      : 'Non-census boundary · blocks assigned by centroid'
    node.append(name, route, metric, pop, note)
    return node
  }

  function handleHover(event: MapMouseEvent): boolean {
    const feature = atPoint(event)
    const id = String(feature?.properties?.urban_id ?? '')
    const item = parishes.get(id)
    if (!item) {
      hover?.remove(); hover = null; hoveredId = ''
      return false
    }
    if (id !== hoveredId) {
      hover?.remove()
      hover = new maplibregl.Popup({ closeButton: false, closeOnClick: false,
        className: 'unit-hover-popup', maxWidth: '240px', offset: 14 })
        .setLngLat(event.lngLat).setDOMContent(card(item)).addTo(map)
      hoveredId = id
    } else hover?.setLngLat(event.lngLat)
    return true
  }

  function handleClick(event: MapMouseEvent): boolean {
    const feature = atPoint(event)
    const id = String(feature?.properties?.urban_id ?? '')
    if (!parishes.has(id)) return false
    selected = id
    hover?.remove(); hover = null; hoveredId = ''
    renderSelected()
    return true
  }

  function renderSelected(): boolean {
    const item = parishes.get(selected ?? '')
    if (!item) return false
    panel.replaceChildren()
    const heading = document.createElement('h3')
    heading.textContent = item.name
    const context = document.createElement('p')
    context.className = 'analysis-place-context'
    context.textContent = `${item.city} · ${language() === 'es' ? 'límite no censal' : 'non-census boundary'}`
    const metric = document.createElement('p')
    metric.className = 'analysis-place-metric'
    metric.textContent = `${language() === 'es' ? 'Índice de envejecimiento' : 'Ageing index'}: ${
      item.aging_index == null ? '—' : decimal(item.aging_index)}`
    const population = document.createElement('p')
    population.className = 'analysis-place-population'
    population.textContent = `${language() === 'es' ? 'Población asignada' : 'Assigned population'}: ${
      number(item.population)} · ${item.blocks} ${language() === 'es' ? 'manzanas' : 'blocks'}`
    const note = document.createElement('small')
    note.className = 'analysis-place-note'
    note.textContent = language() === 'es'
      ? 'Agregado de manzanas INEC 2022 asignadas por centroide al límite municipal. No es una unidad censal.'
      : 'INEC 2022 block aggregates assigned by centroid to a municipal boundary. Not a census unit.'
    panel.append(heading, context, metric, population, note)
    return true
  }

  return { toggle, moveToTop, handleHover, handleClick, renderSelected,
    clearHover: () => { hover?.remove(); hover = null; hoveredId = '' },
    clearSelected: () => { selected = null }, get enabled() { return enabled } }
}
