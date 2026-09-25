import * as maplibregl from 'maplibre-gl'
import type { Map as MapLibreMap } from 'maplibre-gl'
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'
import { Protocol } from 'pmtiles'
import indicatorCatalog from './generated/indicators.json'
import placeCatalog from './generated/places.json'
import { classifyBreaks, indicatorFile } from './indicatorMaps'
import type { BreakMode, Level } from './indicatorMaps'
import 'maplibre-gl/dist/maplibre-gl.css'
import './style.css'

type Bounds = [number, number, number, number]
interface Catalog {
  geom_version: string
  province_bounds: Record<string, Bounds>
  tile_files: Record<Level, string[]>
  matched_geometries: Record<Level, number>
  assigned_manzanas_without_polygon: number
}

const base = import.meta.env.BASE_URL
const definitions = indicatorCatalog.indicators
const byId = new Map(definitions.map(definition => [definition.id, definition]))
const places = placeCatalog.places
const placeByKey = new Map(places.map(place => [place.key, place]))
const levels: Level[] = ['nacion', 'provincia', 'canton', 'parroquia', 'sector', 'manzana']
const params = new URLSearchParams(location.hash.slice(1))
let language: 'es' | 'en' = params.get('lang') === 'en' ? 'en' : 'es'
let indicator = byId.has(params.get('indicator') ?? '') ? params.get('indicator')! : 'density'
let breakMode: BreakMode = ['quantile', 'jenks', 'stddev'].includes(params.get('breaks') ?? '')
  ? params.get('breaks') as BreakMode : 'quantile'
let selectedKey = params.get('place') ?? ''
const copy = {
  es: { search: 'Buscar provincia, cantón, parroquia o código', indicator: 'Indicador',
    breaks: 'Cortes', density: 'Densidad de población', noData: 'Sin dato',
    small: 'Pocos casos: fuera de rankings', from: 'Disponible desde',
    quantile: 'Cuantiles', jenks: 'Jenks', stddev: 'Desviación estándar' },
  en: { search: 'Find province, canton, parish or code', indicator: 'Indicator',
    breaks: 'Breaks', density: 'Population density', noData: 'No data',
    small: 'Few cases: excluded from rankings', from: 'Available from',
    quantile: 'Quantiles', jenks: 'Jenks', stddev: 'Standard deviation' },
}
const app = document.querySelector<HTMLElement>('#app')
if (!app) throw new Error('Missing app root')
app.innerHTML = `
  <div class="shell">
    <div id="map" role="application" aria-label="Mapa de densidad del Censo de Ecuador 2022"></div>
    <header class="masthead">
      <div class="mark" aria-hidden="true">✳</div>
      <div><div class="eyebrow">INEC · CPV 2022 <b>EXPERIMENTAL</b></div>
        <h1>Censo <em>Vivo</em> Ecuador</h1><p>El país, a todas sus escalas.</p></div>
    </header>
    <nav class="breadcrumb" id="breadcrumb" aria-label="Ruta territorial">Ecuador</nav>
    <div class="search-box"><label class="sr-only" for="place-search">Buscar lugar</label>
      <input id="place-search" type="search" autocomplete="off" placeholder="Buscar provincia, cantón, parroquia o código" aria-controls="place-results" aria-expanded="false">
      <div id="place-results" class="search-results" role="listbox" hidden></div></div>
    <button id="language" class="language" type="button" aria-label="Cambiar idioma">EN</button>
    <section class="data-card" aria-label="Indicador activo">
      <div class="card-head"><span class="eyebrow">01 / TERRITORIO</span><span id="level">Cargando…</span></div>
      <label class="control-label" for="indicator-search" id="indicator-label">Indicador</label>
      <input id="indicator-search" type="search" placeholder="Filtrar 45 indicadores">
      <label class="sr-only" for="indicator-select">Indicador activo</label>
      <select id="indicator-select"></select>
      <h2 id="indicator-title">Densidad de población</h2><p id="indicator-description">Habitantes por kilómetro cuadrado de la unidad censal.</p>
      <div class="break-control"><label for="break-mode" id="break-label">Cortes</label>
        <select id="break-mode"><option value="quantile">Cuantiles</option><option value="jenks">Jenks</option><option value="stddev">Desviación estándar</option></select></div>
      <div class="ramp" aria-hidden="true"></div>
      <div class="ticks" id="legend-ticks"><span>0</span><span>50</span><span>200</span><span>1 mil</span><span>5 mil</span><span>15 mil+</span></div>
      <p id="availability" class="availability" role="status"></p>
      <div class="divider"></div>
      <div class="metric"><strong id="unit-count">—</strong><span>unidades con geometría</span></div>
      <p class="hint">Acércate para pasar de provincia a cantón, parroquia, sector y manzana. Pulsa una zona para ver sus conteos.</p>
    </section>
    <div class="scale-rail"><span>NACIONAL</span><div class="rail"><i id="scale-marker"></i></div><span>MANZANA</span></div>
    <footer class="footnote"><span class="signal"></span><span>Fuente: INEC, CPV 2022 · Geometría: Marco 2021</span>
      <span class="foot-sep">/</span><span id="assignment-note">Manzanas sin polígono: población asignada a nivel de sector</span></footer>
    <div class="status" id="status" role="status" aria-live="polite">Preparando cartografía…</div>
  </div>`

const levelEl = document.querySelector<HTMLElement>('#level')!
const countEl = document.querySelector<HTMLElement>('#unit-count')!
const statusEl = document.querySelector<HTMLElement>('#status')!
const markerEl = document.querySelector<HTMLElement>('#scale-marker')!
const indicatorSelect = document.querySelector<HTMLSelectElement>('#indicator-select')!
const indicatorSearch = document.querySelector<HTMLInputElement>('#indicator-search')!
const indicatorTitle = document.querySelector<HTMLElement>('#indicator-title')!
const indicatorDescription = document.querySelector<HTMLElement>('#indicator-description')!
const availabilityEl = document.querySelector<HTMLElement>('#availability')!
const breaksEl = document.querySelector<HTMLSelectElement>('#break-mode')!
const legendEl = document.querySelector<HTMLElement>('#legend-ticks')!
const placeSearch = document.querySelector<HTMLInputElement>('#place-search')!
const placeResults = document.querySelector<HTMLElement>('#place-results')!
const breadcrumbEl = document.querySelector<HTMLElement>('#breadcrumb')!
const languageEl = document.querySelector<HTMLButtonElement>('#language')!
const names: Record<Level, string> = {
  nacion: 'Ecuador', provincia: 'Provincia', canton: 'Cantón',
  parroquia: 'Parroquia', sector: 'Sector censal', manzana: 'Manzana',
}
const zoomLevel = (z: number): Level => z < 3 ? 'nacion' : z < 6 ? 'provincia'
  : z < 8 ? 'canton' : z < 10 ? 'parroquia' : z < 13 ? 'sector' : 'manzana'
const color: maplibregl.ExpressionSpecification = [
  'case', ['!', ['has', 'density']], '#354050',
  ['interpolate', ['linear'], ['get', 'density'],
    0, '#203650', 50, '#2a6575', 200, '#48a292', 1000, '#c0c470',
    5000, '#f4a944', 15000, '#f17439'],
]
const integer = new Intl.NumberFormat('es-EC')
const decimal = new Intl.NumberFormat('es-EC', { maximumFractionDigits: 1 })
const palette = ['#203650', '#2a6575', '#48a292', '#c0c470', '#f4a944']
const formatValue = (value: number): string => new Intl.NumberFormat(language === 'es' ? 'es-EC' : 'en-US',
  { maximumFractionDigits: Math.abs(value) < 10 ? 2 : 1 }).format(value)
const norm = (value: string): string => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
function saveHash(map?: MapLibreMap) {
  const state = new URLSearchParams()
  if (indicator !== 'density') state.set('indicator', indicator)
  if (breakMode !== 'quantile') state.set('breaks', breakMode)
  if (language !== 'es') state.set('lang', language)
  if (selectedKey) state.set('place', selectedKey)
  if (map) {
    const center = map.getCenter()
    state.set('map', `${center.lng.toFixed(4)},${center.lat.toFixed(4)},${map.getZoom().toFixed(2)}`)
  }
  history.replaceState(null, '', `${location.pathname}${location.search}#${state}`)
}

function renderBreadcrumb() {
  breadcrumbEl.replaceChildren()
  const keys = selectedKey ? [selectedKey.slice(0, 2), selectedKey.slice(0, 4),
    selectedKey.slice(0, 6), selectedKey].filter((key, index, all) =>
    !!placeByKey.get(key) && all.indexOf(key) === index) : []
  const labels = ['Ecuador', ...keys.map(key => placeByKey.get(key)!.name)]
  for (let index = 0; index < labels.length; index++) {
    if (index) breadcrumbEl.append(' › ')
    const span = document.createElement('span')
    span.textContent = labels[index]
    breadcrumbEl.append(span)
  }
}

function indicatorAvailable(minLevel: string, level: Level): boolean {
  return levels.indexOf(level) >= levels.indexOf(minLevel as Level)
}

function renderControls(level: Level) {
  const t = copy[language]
  placeSearch.placeholder = t.search
  document.querySelector<HTMLElement>('#indicator-label')!.textContent = t.indicator
  document.querySelector<HTMLElement>('#break-label')!.textContent = t.breaks
  languageEl.textContent = language === 'es' ? 'EN' : 'ES'
  for (const mode of ['quantile', 'jenks', 'stddev'] as BreakMode[]) {
    breaksEl.querySelector<HTMLOptionElement>(`option[value="${mode}"]`)!.textContent = t[mode]
  }
  indicatorSelect.replaceChildren()
  const density = new Option(t.density, 'density')
  indicatorSelect.add(density)
  const groups = new Map<string, HTMLOptGroupElement>()
  const filter = norm(indicatorSearch.value)
  for (const definition of definitions) {
    const label = definition.name[language]
    if (filter && !norm(`${label} ${definition.id} ${definition.theme}`).includes(filter)) continue
    let group = groups.get(definition.theme)
    if (!group) {
      group = document.createElement('optgroup')
      group.label = definition.theme.replaceAll('_', ' ')
      groups.set(definition.theme, group)
      indicatorSelect.add(group)
    }
    const option = new Option(label, definition.id)
    option.disabled = !indicatorAvailable(definition.min_level, level)
    option.title = option.disabled ? `${t.from} ${definition.min_level}` : ''
    group.append(option)
  }
  if (indicator !== 'density' && !indicatorSelect.querySelector(`option[value="${indicator}"]`)) {
    const definition = byId.get(indicator)!
    const selected = new Option(definition.name[language], indicator)
    selected.disabled = !indicatorAvailable(definition.min_level, level)
    indicatorSelect.add(selected)
  }
  indicatorSelect.value = indicator
  breaksEl.value = breakMode
  indicatorTitle.textContent = indicator === 'density' ? t.density : byId.get(indicator)!.name[language]
  indicatorDescription.textContent = indicator === 'density'
    ? (language === 'es' ? 'Habitantes por kilómetro cuadrado de la unidad censal.'
      : 'Residents per square kilometre of the census unit.')
    : byId.get(indicator)!.population_reference
  availabilityEl.textContent = indicator !== 'density' &&
    !indicatorAvailable(byId.get(indicator)!.min_level, level)
    ? `${t.from} ${byId.get(indicator)!.min_level}` : ''
  renderBreadcrumb()
}
const protocol = new Protocol()
maplibregl.setWorkerUrl(workerUrl)
maplibregl.addProtocol('pmtiles', protocol.tile)

async function start() {
  const response = await fetch(`${base}data/tiles/v1b/catalog.json`)
  if (!response.ok) throw new Error(`Catálogo no disponible (${response.status})`)
  const catalog = await response.json() as Catalog
  if (catalog.geom_version !== 'marco-2021') throw new Error('Versión geométrica desconocida')
  document.querySelector<HTMLElement>('#assignment-note')!.textContent =
    `${integer.format(catalog.assigned_manzanas_without_polygon)} manzanas sin polígono: población asignada a nivel de sector`
  const camera = (params.get('map') ?? '').split(',').map(Number)
  const validCamera = camera.length === 3 && camera.every(Number.isFinite)
  const map: MapLibreMap = new maplibregl.Map({
    container: 'map', center: validCamera ? [camera[0], camera[1]] : [-79.45, -1.52],
    zoom: validCamera ? camera[2] : 5, minZoom: 2, maxZoom: 16.5,
    attributionControl: false,
    style: {
      version: 8,
      sources: {},
      layers: [{ id: 'background', type: 'background',
        paint: { 'background-color': '#101d2c' } }],
    },
  })
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right')
  map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right')
  const active = new Set<string>()
  let currentLevel = zoomLevel(map.getZoom())
  let paintGeneration = 0
  let paintedKey = ''

  function fillExpression(breaks: number[]): maplibregl.ExpressionSpecification {
    if (indicator === 'density') return color
    const distinct = [...new Set(breaks)].sort((a, b) => a - b)
    const step: unknown[] = ['step', ['to-number', ['feature-state', 'value'], 0], palette[0]]
    distinct.forEach((breakpoint, index) => step.push(breakpoint,
      palette[Math.min(palette.length - 1, index + 1)]))
    return ['case', ['in', ['feature-state', 'status'], ['literal', [0, 1]]],
      step, '#354050'] as unknown as maplibregl.ExpressionSpecification
  }

  async function colorize(level: Level, provinces: string[]) {
    const generation = ++paintGeneration
    if (indicator === 'density') {
      for (const id of active) {
        map.setPaintProperty(`${id}-fill`, 'fill-color', color)
        map.setPaintProperty(`${id}-fill`, 'fill-opacity', 0.79)
      }
      legendEl.replaceChildren(...['0', '50', '200', '1 mil', '5 mil', '15 mil+'].map(value => {
        const span = document.createElement('span'); span.textContent = value; return span
      }))
      return
    }
    const definition = byId.get(indicator)!
    if (!indicatorAvailable(definition.min_level, level)) {
      for (const id of active) {
        map.setPaintProperty(`${id}-fill`, 'fill-color', '#354050')
      }
      return
    }
    statusEl.textContent = language === 'es' ? 'Cargando indicador…' : 'Loading indicator…'
    try {
      const files = await Promise.all(provinces.map(province =>
        indicatorFile(base, level, level === 'sector' || level === 'manzana' ? province : undefined)))
      if (generation !== paintGeneration) return
      const values = files.flatMap(file => file.eligibleValues(indicator))
      const breaks = classifyBreaks(values, breakMode)
      const expression = fillExpression(breaks)
      for (const id of active) {
        map.setPaintProperty(`${id}-fill`, 'fill-color', expression)
        map.setPaintProperty(`${id}-fill`, 'fill-opacity', ['case',
          ['==', ['feature-state', 'status'], 1], 0.42, 0.82])
      }
      legendEl.replaceChildren(...breaks.map(value => {
        const span = document.createElement('span'); span.textContent = formatValue(value); return span
      }))
      for (let fileIndex = 0; fileIndex < files.length; fileIndex++) {
        const id = `${level}-${provinces[fileIndex]}`
        const file = files[fileIndex]
        for (let offset = 0; offset < file.keys.length; offset += 500) {
          if (generation !== paintGeneration || !active.has(id)) return
          for (const key of file.keys.slice(offset, offset + 500)) {
            const cell = file.cell(key, indicator)
            if (cell) map.setFeatureState({ source: id, sourceLayer: level, id: key },
              { value: cell.value, status: cell.status })
          }
          await new Promise<void>(resolve => requestAnimationFrame(() => resolve()))
        }
      }
      statusEl.textContent = `${names[level]} · ${values.length.toLocaleString(language)} ${language === 'es' ? 'casos fiables' : 'reliable units'}`
    } catch (error) {
      if (generation === paintGeneration) statusEl.textContent = String(error)
    }
  }

  function visibleProvinces(level: Level): string[] {
    const available = catalog.tile_files[level] ?? []
    if (level !== 'sector' && level !== 'manzana') return available
    const view = map.getBounds()
    return available.filter(province => {
      const b = catalog.province_bounds[province]
      return b && view.getWest() <= b[2] && view.getEast() >= b[0]
        && view.getSouth() <= b[3] && view.getNorth() >= b[1]
    })
  }

  function sync() {
    const level = zoomLevel(map.getZoom())
    const provinces = visibleProvinces(level)
    const wanted = new Set(provinces.map(p => `${level}-${p}`))
    for (const id of active) {
      if (!wanted.has(id)) {
        map.removeLayer(`${id}-outline`)
        map.removeLayer(`${id}-fill`)
        map.removeSource(id)
        active.delete(id)
      }
    }
    for (const province of provinces) {
      const id = `${level}-${province}`
      if (active.has(id)) continue
      const url = `${location.origin}${base}data/tiles/v1b/${level}/${province}.pmtiles`
      map.addSource(id, { type: 'vector', url: `pmtiles://${url}`, promoteId: 'unit_key' })
      map.addLayer({ id: `${id}-fill`, type: 'fill', source: id,
        'source-layer': level, paint: { 'fill-color': color, 'fill-opacity': 0.79 } })
      map.addLayer({ id: `${id}-outline`, type: 'line', source: id,
        'source-layer': level, paint: { 'line-color': '#8da4b2',
          'line-opacity': 0.27, 'line-width': level === 'manzana' ? 0.5 : 0.8 } })
      active.add(id)
    }
    levelEl.textContent = names[level]
    countEl.textContent = integer.format(catalog.matched_geometries[level] ?? 0)
    markerEl.style.top = `${Math.min(100, Math.max(0, (map.getZoom() - 2) / 14 * 100))}%`
    statusEl.textContent = `${names[level]} · ${provinces.length} archivo${provinces.length === 1 ? '' : 's'}`
    const key = `${level}:${provinces.join(',')}:${indicator}:${breakMode}`
    if (paintedKey !== key) {
      paintedKey = key
      void colorize(level, provinces)
    }
    if (currentLevel !== level) {
      currentLevel = level
      renderControls(level)
    }
    saveHash(map)
  }
  renderControls(currentLevel)
  indicatorSelect.addEventListener('change', () => {
    indicator = indicatorSelect.value
    paintedKey = ''
    renderControls(zoomLevel(map.getZoom()))
    sync()
  })
  indicatorSearch.addEventListener('input', () => renderControls(zoomLevel(map.getZoom())))
  breaksEl.addEventListener('change', () => {
    breakMode = breaksEl.value as BreakMode
    paintedKey = ''
    sync()
  })
  languageEl.addEventListener('click', () => {
    language = language === 'es' ? 'en' : 'es'
    renderControls(zoomLevel(map.getZoom()))
    saveHash(map)
  })
  placeSearch.addEventListener('input', () => {
    const query = norm(placeSearch.value.trim())
    placeResults.replaceChildren()
    if (query.length < 2) {
      placeResults.hidden = true; placeSearch.setAttribute('aria-expanded', 'false'); return
    }
    const matches = places.filter(place => norm(`${place.name} ${place.key} ${place.parent}`).includes(query)).slice(0, 8)
    for (const place of matches) {
      const button = document.createElement('button')
      button.type = 'button'
      button.setAttribute('role', 'option')
      button.textContent = `${place.name} · ${place.parent} (${place.key})`
      button.addEventListener('click', () => {
        selectedKey = place.key
        placeSearch.value = place.name
        placeResults.hidden = true
        placeSearch.setAttribute('aria-expanded', 'false')
        renderBreadcrumb()
        map.fitBounds(place.bbox as Bounds, { padding: 85, duration: 900, maxZoom: 12.5 })
        saveHash(map)
      })
      placeResults.append(button)
    }
    placeResults.hidden = !matches.length
    placeSearch.setAttribute('aria-expanded', String(!!matches.length))
  })
  placeSearch.addEventListener('keydown', event => {
    if (event.key === 'Escape') { placeResults.hidden = true; placeSearch.setAttribute('aria-expanded', 'false') }
    if (event.key === 'Enter') placeResults.querySelector<HTMLButtonElement>('button')?.click()
  })
  map.on('load', sync)
  map.on('moveend', sync)
  map.on('mousemove', event => {
    const layers = [...active].map(id => `${id}-fill`)
    map.getCanvas().style.cursor = layers.length && map.queryRenderedFeatures(event.point, { layers }).length
      ? 'pointer' : ''
  })
  map.on('click', async event => {
    const layers = [...active].map(id => `${id}-fill`)
    if (!layers.length) return
    const p = map.queryRenderedFeatures(event.point, { layers })[0]?.properties
    if (!p) return
    const level = zoomLevel(map.getZoom())
    selectedKey = String(p.unit_key)
    renderBreadcrumb()
    saveHash(map)
    const people = p.population == null ? 'Sin dato' : integer.format(Number(p.population))
    const density = p.density == null ? 'Sin dato' : decimal.format(Number(p.density))
    const card = document.createElement('div')
    card.className = 'popup'
    const title = document.createElement('small')
    title.textContent = `${names[level]} · ${selectedKey}`
    const number = document.createElement('strong')
    number.textContent = people
    const label = document.createElement('span')
    label.textContent = language === 'es' ? 'personas' : 'people'
    const detail = document.createElement('div')
    detail.textContent = `${density} hab./km²`
    card.append(title, number, label, detail)
    if (Number(p.assigned_population) > 0) {
      const note = document.createElement('div')
      note.className = 'popup-note'
      note.textContent = `${integer.format(Number(p.assigned_population))} personas de manzanas sin polígono asignadas al sector`
      card.append(note)
    }
    if (indicator !== 'density') {
      try {
        const file = await indicatorFile(base, level,
          level === 'sector' || level === 'manzana' ? selectedKey.slice(0, 2) : undefined)
        const cell = file.cell(selectedKey, indicator)
        const value = document.createElement('div')
        value.textContent = `${byId.get(indicator)!.name[language]}: ${cell?.value == null ? copy[language].noData : formatValue(cell.value)}`
        card.append(value)
        if (cell?.status === 1) {
          const warning = document.createElement('div')
          warning.className = 'popup-note'
          warning.textContent = copy[language].small
          card.append(warning)
        }
      } catch (error) { statusEl.textContent = String(error) }
    }
    new maplibregl.Popup({ maxWidth: '290px' }).setLngLat(event.lngLat)
      .setDOMContent(card).addTo(map)
  })
  map.on('error', event => { statusEl.textContent = `Error de cartografía: ${event.error?.message ?? 'desconocido'}` })
}

start().catch(error => { statusEl.textContent = `No se pudo abrir el mapa: ${String(error)}` })
