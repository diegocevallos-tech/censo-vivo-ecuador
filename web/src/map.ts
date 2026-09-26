import * as maplibregl from 'maplibre-gl'
import type { Map as MapLibreMap } from 'maplibre-gl'
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'
import { Protocol } from 'pmtiles'
import indicatorCatalog from './generated/indicators.json'
import placeCatalog from './generated/places.json'
import { breadcrumbNames, levelLabel, unitKeyAtLevel, unitPresentation } from './placeLabels'
import { availableAtLevel, classifyBreaks, indicatorFile } from './indicatorMaps'
import type { BreakMode, Level } from './indicatorMaps'
import { createSelection } from './selection'
import type { SelectionMode, SelectionResult } from './selection'
import { renderAnalysis } from './analysisPanel'
import { countChunk } from './countChunks'
import { evaluate, fitCantonPrior } from './indicators'
import type { CantonPrior, IndicatorDefinition } from './indicators'
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
    quantile: 'Cuantiles', jenks: 'Jenks', stddev: 'Desviación estándar',
    units: 'unidades con geometría', hint: 'Acércate para pasar de provincia a cantón, parroquia, sector y manzana. Pulsa una zona para ver sus conteos.',
    analyze: 'ANÁLISIS', smoothing: 'Suavizado EB', inspect: 'Inspeccionar', circle: 'Círculo',
    lasso: 'Lazo', multi: 'Multi', clear: 'Limpiar', densityToggle: 'Densidad',
    unitsToggle: 'Unidades', source: 'Fuente: INEC, CPV 2022 · Geometría: Marco 2021' },
  en: { search: 'Find province, canton, parish or code', indicator: 'Indicator',
    breaks: 'Breaks', density: 'Population density', noData: 'No data',
    small: 'Few cases: excluded from rankings', from: 'Available from',
    quantile: 'Quantiles', jenks: 'Jenks', stddev: 'Standard deviation',
    units: 'units with geometry', hint: 'Zoom from province to canton, parish, sector and block. Choose a unit to see its counts.',
    analyze: 'ANALYSIS', smoothing: 'EB smoothing', inspect: 'Inspect', circle: 'Circle',
    lasso: 'Lasso', multi: 'Multi', clear: 'Clear', densityToggle: 'Density',
    unitsToggle: 'Units', source: 'Source: INEC, Census 2022 · Geometry: 2021 framework' },
}
const app = document.querySelector<HTMLElement>('#app')
if (!app) throw new Error('Missing app root')
const shell = app
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
      <p class="break-scope" id="break-scope"></p>
      <div class="ramp" aria-hidden="true"></div>
      <div class="ticks" id="legend-ticks"><span>0</span><span>50</span><span>200</span><span>1 mil</span><span>5 mil</span><span>15 mil+</span></div>
      <p id="availability" class="availability" role="status"></p>
      <div class="divider"></div>
      <div class="metric"><strong id="unit-count">—</strong><span>unidades con geometría</span></div>
      <p class="hint">Acércate para pasar de provincia a cantón, parroquia, sector y manzana. Pulsa una zona para ver sus conteos.</p>
      <div class="analysis-head"><span class="eyebrow">02 / ANÁLISIS</span>
        <label><input type="checkbox" id="smooth-toggle"><span id="smooth-label">Suavizado EB</span></label></div>
      <div id="selection-preview" class="selection-preview" role="status" aria-live="polite"></div>
      <div id="analysis-content" class="analysis-content"></div>
    </section>
    <aside class="theme-chips" id="theme-chips" aria-label="Temas"></aside>
    <div class="toolbar" role="toolbar" aria-label="Herramientas de análisis">
      <button type="button" data-mode="inspect" aria-pressed="true">Inspeccionar</button>
      <button type="button" data-mode="circle" aria-pressed="false">Círculo</button>
      <button type="button" data-mode="lasso" aria-pressed="false">Lazo</button>
      <button type="button" data-mode="multi" aria-pressed="false">Multi</button>
      <button type="button" id="clear-selection">Limpiar</button>
      <button type="button" id="toggle-density" aria-pressed="true">Densidad</button>
      <button type="button" id="toggle-units" aria-pressed="true">Unidades</button>
      <button type="button" id="toggle-3d" aria-pressed="false">3D</button>
    </div>
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
const breakScopeEl = document.querySelector<HTMLElement>('#break-scope')!
const analysisEl = document.querySelector<HTMLElement>('#analysis-content')!
const previewEl = document.querySelector<HTMLElement>('#selection-preview')!
const smoothEl = document.querySelector<HTMLInputElement>('#smooth-toggle')!
const themeEl = document.querySelector<HTMLElement>('#theme-chips')!
const placeSearch = document.querySelector<HTMLInputElement>('#place-search')!
const placeResults = document.querySelector<HTMLElement>('#place-results')!
const breadcrumbEl = document.querySelector<HTMLElement>('#breadcrumb')!
const languageEl = document.querySelector<HTMLButtonElement>('#language')!
const names: Record<Level, string> = {
  nacion: 'Ecuador', provincia: 'Provincia', canton: 'Cantón',
  parroquia: 'Parroquia', sector: 'Sector censal', manzana: 'Manzana',
}
const englishNames: Record<Level, string> = {
  nacion: 'Ecuador', provincia: 'Province', canton: 'Canton',
  parroquia: 'Parish', sector: 'Census sector', manzana: 'Census block',
}
const levelName = (level: Level): string => language === 'es' ? names[level] : englishNames[level]
const englishThemes: Record<string, string> = {
  demografia: 'Demography', hogar: 'Households', vivienda: 'Housing',
  digital: 'Digital', trabajo: 'Work', movilidad: 'Mobility', diaspora: 'Diaspora',
  diversidad: 'Diversity', fecundidad: 'Fertility', mortalidad: 'Mortality',
  educacion: 'Education', compuesto: 'Composite',
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
const palettes: Record<string, string[]> = {
  density: ['#203650', '#2a6575', '#48a292', '#c0c470', '#f4a944'],
  Viridis: ['#440154', '#3b528b', '#21918c', '#5ec962', '#fde725'],
  PuRd: ['#f1eef6', '#d7b5d8', '#df65b0', '#dd1c77', '#980043'],
  RdBu: ['#2166ac', '#92c5de', '#f7f7f7', '#f4a582', '#b2182b'],
  YlOrRd: ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026'],
}
function activePalette(): string[] {
  return indicator === 'density' ? palettes.density :
    palettes[byId.get(indicator)!.palette] ?? palettes.Viridis
}
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
  const labels = breadcrumbNames(selectedKey, language)
  for (let index = 0; index < labels.length; index++) {
    if (index) breadcrumbEl.append(' › ')
    const span = document.createElement('span')
    span.textContent = labels[index]
    breadcrumbEl.append(span)
  }
}

function indicatorAvailable(minLevel: string, level: Level): boolean {
  return availableAtLevel(minLevel as Level, level)
}

function renderControls(level: Level) {
  const t = copy[language]
  document.documentElement.lang = language
  placeSearch.placeholder = t.search
  indicatorSearch.placeholder = language === 'es' ? 'Filtrar 45 indicadores' : 'Filter 45 indicators'
  levelEl.textContent = levelName(level)
  document.querySelector<HTMLElement>('.card-head .eyebrow')!.textContent = language === 'es' ? '01 / TERRITORIO' : '01 / TERRITORY'
  document.querySelector<HTMLElement>('.masthead p')!.textContent = language === 'es'
    ? 'El país, a todas sus escalas.' : 'The country at every scale.'
  document.querySelector<HTMLElement>('.metric span')!.textContent = t.units
  document.querySelector<HTMLElement>('.data-card .hint')!.textContent = t.hint
  document.querySelector<HTMLElement>('.analysis-head .eyebrow')!.textContent = `02 / ${t.analyze}`
  document.querySelector<HTMLElement>('#smooth-label')!.textContent = t.smoothing
  document.querySelector<HTMLElement>('.footnote span:nth-child(2)')!.textContent = t.source
  const toolbarLabels: Record<string, string> = { inspect: t.inspect, circle: t.circle,
    lasso: t.lasso, multi: t.multi }
  for (const button of Array.from(document.querySelectorAll<HTMLButtonElement>('.toolbar [data-mode]'))) {
    button.textContent = toolbarLabels[button.dataset.mode ?? 'inspect']
  }
  document.querySelector<HTMLElement>('#clear-selection')!.textContent = t.clear
  document.querySelector<HTMLElement>('#toggle-density')!.textContent = t.densityToggle
  document.querySelector<HTMLElement>('#toggle-units')!.textContent = t.unitsToggle
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
    : language === 'es' ? byId.get(indicator)!.population_reference
      : 'Reference population and definition in the methodology.'
  availabilityEl.textContent = indicator !== 'density' &&
    !indicatorAvailable(byId.get(indicator)!.min_level, level)
    ? `${t.from} ${byId.get(indicator)!.min_level}` : ''
  breakScopeEl.textContent = language === 'es'
    ? (indicator === 'density' ? 'Cortes del mapa visible.'
      : level === 'sector' || level === 'manzana' ? 'Cortes de las provincias cargadas.'
        : 'Cortes nacionales.')
    : (indicator === 'density' ? 'Breaks use visible map units.'
      : level === 'sector' || level === 'manzana' ? 'Breaks use loaded provinces.'
        : 'Nationwide breaks.')
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
  let densityPaintKey = ''
  let lastSelection: SelectionResult | null = null
  let selectedHighlight = new Set<string>()
  let analysisGeneration = 0
  let densityOn = true
  let unitsOn = true
  let mode3d = false
  let sectorFallback = false
  const effectiveLevel = (): Level => sectorFallback && zoomLevel(map.getZoom()) === 'manzana'
    ? 'sector' : zoomLevel(map.getZoom())

  function applySelectionPaint() {
    for (const id of active) {
      const fill = `${id}-fill`
      const line = `${id}-outline`
      map.setLayoutProperty(fill, 'visibility', unitsOn ? 'visible' : 'none')
      map.setLayoutProperty(line, 'visibility', unitsOn ? 'visible' : 'none')
      const defaultOpacity: maplibregl.ExpressionSpecification | number = indicator === 'density' ? 0.79
        : ['case', ['==', ['feature-state', 'status'], 1], 0.42, 0.82]
      const opacity: maplibregl.ExpressionSpecification | number = !densityOn && indicator === 'density' ? 0
        : selectedHighlight.size ? ['case', ['==', ['feature-state', 'selected'], true],
          defaultOpacity, 0] : defaultOpacity
      map.setPaintProperty(fill, 'fill-opacity', opacity)
      map.setPaintProperty(line, 'line-opacity', selectedHighlight.size
        ? ['case', ['==', ['feature-state', 'selected'], true], 0.4, 0] : 0.27)
      if (map.getLayer(`${id}-extrusion`)) {
        map.setLayoutProperty(`${id}-extrusion`, 'visibility', unitsOn && mode3d ? 'visible' : 'none')
        map.setPaintProperty(`${id}-extrusion`, 'fill-extrusion-opacity', selectedHighlight.size
          ? ['case', ['==', ['feature-state', 'selected'], true], 0.65, 0] : 0.65)
      }
    }
  }

  function extrusion(id: string, level: Level) {
    map.addLayer({ id: `${id}-extrusion`, type: 'fill-extrusion', source: id,
      'source-layer': level, paint: {
        'fill-extrusion-color': color,
        'fill-extrusion-height': ['min', 450, ['*', 4,
          ['sqrt', ['to-number', ['get', 'population'], 0]]]],
        'fill-extrusion-base': 0, 'fill-extrusion-opacity': 0.65,
      } })
  }

  async function refreshAnalysis() {
    const generation = ++analysisGeneration
    let prior: CantonPrior | null = null
    if (lastSelection && smoothEl.checked && indicator !== 'density') {
      const definition = byId.get(indicator) as unknown as IndicatorDefinition | undefined
      const cantons = new Set(lastSelection.keys.map(key => key.slice(0, 4)))
      if (definition?.bayesian && definition.kind === 'ratio' && cantons.size === 1) {
        const canton = [...cantons][0]
        const chunk = await countChunk(base, canton.slice(0, 2), 'sector')
        const peers: [number, number][] = []
        for (const key of chunk.keysWithPrefix(canton)) {
          const counts = chunk.counts(key)
          if (!counts) continue
          const result = evaluate(definition, { counts, quality: 'exacto',
            estimated_percent: 0 }, { level: 'sector' })
          if (result.value != null && result.denominator > 0) {
            peers.push([result.value / (definition.factor ?? 1) * result.denominator,
              result.denominator])
          }
        }
        prior = fitCantonPrior(peers)
      }
    }
    if (generation !== analysisGeneration) return
    const labels: Record<string, string> = language === 'en'
      ? { 'Círculo': 'Circle', 'Lazo': 'Lasso', 'Multiselección': 'Multiple units',
        'Unidad oficial': 'Official unit' }
      : { Circle: 'Círculo', Lasso: 'Lazo', 'Multiple units': 'Multiselección',
        'Official unit': 'Unidad oficial' }
    const localized = lastSelection ? { ...lastSelection,
      label: lastSelection.officialUnitKey
        ? unitPresentation(currentLevel, lastSelection.officialUnitKey, language).headline
        : labels[lastSelection.label] ?? lastSelection.label } : null
    await renderAnalysis(analysisEl, localized, { language, level: currentLevel,
      base, smooth: smoothEl.checked, activeIndicator: indicator, prior })
  }

  const selection = createSelection({ map, base, shell,
    getLanguage: () => language,
    getLevel: () => currentLevel,
    getLayers: () => [...active].map(id => `${id}-fill`),
    onPreview: (population, radiusKm, computeMs) => {
      previewEl.textContent = `${integer.format(population)} ${language === 'es' ? 'personas aprox.' : 'people approx.'} · ${decimal.format(radiusKm)} km`
      previewEl.dataset.computeMs = computeMs.toFixed(2)
    },
    onResult: result => {
      lastSelection = result
      if (selection.mode === 'multi') {
        selectedKey = result?.officialUnitKey ?? ''
        renderBreadcrumb()
        saveHash(map)
      }
      previewEl.textContent = result ? `${integer.format(result.aggregate.counts.population ?? 0)} ${language === 'es' ? 'personas en la selección' : 'people in selection'}` : ''
      if (result) previewEl.dataset.previewP95Ms = selection.previewP95Ms.toFixed(2)
      statusEl.textContent = result ? `${result.label} · ${integer.format(result.unitCount)} ${result.unitCount === 1 ? (language === 'es' ? 'unidad' : 'unit') : (language === 'es' ? 'unidades' : 'units')}` : levelName(currentLevel)
      void refreshAnalysis().catch(error => { statusEl.textContent = `Error de análisis: ${String(error)}` })
    },
    onHighlight: keys => {
      for (const key of selectedHighlight) {
        const id = `${currentLevel}-${currentLevel === 'sector' || currentLevel === 'manzana'
          ? key.slice(0, 2) : 'data'}`
        if (active.has(id)) map.setFeatureState({ source: id, sourceLayer: currentLevel,
          id: key }, { selected: false })
      }
      selectedHighlight = new Set(keys)
      for (const key of keys) {
        const id = `${currentLevel}-${currentLevel === 'sector' || currentLevel === 'manzana'
          ? key.slice(0, 2) : 'data'}`
        if (active.has(id)) map.setFeatureState({ source: id, sourceLayer: currentLevel,
          id: key }, { selected: true })
      }
      applySelectionPaint()
    },
    onStatus: message => { statusEl.textContent = message },
  })

  function fillExpression(breaks: number[]): maplibregl.ExpressionSpecification {
    const palette = activePalette()
    const distinct = [...new Set(breaks)].sort((a, b) => a - b)
    const step: unknown[] = ['step', ['to-number', ['feature-state', 'value'], 0], palette[0]]
    distinct.forEach((breakpoint, index) => step.push(breakpoint,
      palette[Math.min(palette.length - 1, index + 1)]))
    if (indicator === 'density') {
      step[1] = ['to-number', ['get', 'density'], 0]
      return ['case', ['has', 'density'], step, '#354050'] as unknown as maplibregl.ExpressionSpecification
    }
    return ['case', ['in', ['feature-state', 'status'], ['literal', [0, 1]]],
      step, '#354050'] as unknown as maplibregl.ExpressionSpecification
  }

  async function colorize(level: Level, provinces: string[]) {
    const generation = ++paintGeneration
    const ramp = document.querySelector<HTMLElement>('.ramp')!
    const colors = activePalette()
    ramp.style.background = `linear-gradient(90deg, ${colors.map((hex, index) =>
      `${hex} ${index * 20}%,${hex} ${(index + 1) * 20}%`).join(',')})`
    if (indicator === 'density') {
      densityPaintKey = ''
      for (const id of active) {
        map.setPaintProperty(`${id}-fill`, 'fill-color', color)
        map.setPaintProperty(`${id}-fill`, 'fill-opacity', 0.79)
        if (map.getLayer(`${id}-extrusion`)) map.setPaintProperty(`${id}-extrusion`, 'fill-extrusion-color', color)
      }
      legendEl.replaceChildren(...['0', '50', '200', '1 mil', '5 mil', '15 mil+'].map(value => {
        const span = document.createElement('span'); span.textContent = value; return span
      }))
      applySelectionPaint()
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
        if (map.getLayer(`${id}-extrusion`)) map.setPaintProperty(`${id}-extrusion`, 'fill-extrusion-color', expression)
      }
      applySelectionPaint()
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

  function updateDensityBreaks() {
    if (indicator !== 'density' || !active.size) return
    const seen = new Set<string>()
    const values: number[] = []
    for (const id of active) {
      const level = currentLevel
      for (const feature of map.querySourceFeatures(id, { sourceLayer: level })) {
        const key = String(feature.properties.unit_key)
        const density = Number(feature.properties.density)
        if (!seen.has(key) && Number.isFinite(density)) {
          values.push(density)
          seen.add(key)
        }
      }
    }
    if (values.length < 5) return
    const breaks = classifyBreaks(values, breakMode).map(value => Math.max(0, value))
    const next = `${currentLevel}:${breakMode}:${breaks.join(',')}`
    if (next === densityPaintKey) return
    densityPaintKey = next
    const expression = fillExpression(breaks)
    for (const id of active) map.setPaintProperty(`${id}-fill`, 'fill-color', expression)
    legendEl.replaceChildren(...breaks.map(value => {
      const span = document.createElement('span'); span.textContent = formatValue(value); return span
    }))
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
    const level = effectiveLevel()
    const provinces = visibleProvinces(level)
    const wanted = new Set(provinces.map(p => `${level}-${p}`))
    for (const id of active) {
      if (!wanted.has(id)) {
        if (map.getLayer(`${id}-extrusion`)) map.removeLayer(`${id}-extrusion`)
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
      if (mode3d) extrusion(id, level)
      active.add(id)
    }
    applySelectionPaint()
    levelEl.textContent = levelName(level)
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
      selection.clear()
      renderControls(level)
      renderThemes()
    }
    saveHash(map)
  }
  renderControls(currentLevel)
  void refreshAnalysis()
  function renderThemes() {
    themeEl.replaceChildren()
    const themes = [...new Set(definitions.map(item => item.theme))]
    for (const theme of themes) {
      const available = definitions.find(item => item.theme === theme &&
        indicatorAvailable(item.min_level, currentLevel))
      const button = document.createElement('button')
      button.type = 'button'
      button.textContent = language === 'en' ? englishThemes[norm(theme)] ?? theme.replaceAll('_', ' ')
        : theme.replaceAll('_', ' ')
      button.disabled = !available
      button.classList.toggle('active', indicator !== 'density' && byId.get(indicator)?.theme === theme)
      button.setAttribute('aria-pressed', String(button.classList.contains('active')))
      button.title = available ? '' : `${copy[language].from} ${definitions.find(item => item.theme === theme)?.min_level}`
      button.addEventListener('click', () => {
        if (!available) return
        indicator = available.id
        paintedKey = ''
        renderControls(currentLevel)
        renderThemes()
        sync()
        void refreshAnalysis()
      })
      themeEl.append(button)
    }
  }
  renderThemes()
  for (const button of Array.from(document.querySelectorAll<HTMLButtonElement>('.toolbar [data-mode]'))) {
    button.addEventListener('click', () => {
      const next = button.dataset.mode as SelectionMode
      selection.setMode(next)
      for (const peer of Array.from(document.querySelectorAll<HTMLButtonElement>('.toolbar [data-mode]'))) {
        const activeMode = peer === button
        peer.setAttribute('aria-pressed', String(activeMode))
        peer.classList.toggle('active', activeMode)
      }
    })
  }
  document.querySelector<HTMLButtonElement>('#clear-selection')!.addEventListener('click', () => selection.clear())
  document.querySelector<HTMLButtonElement>('#toggle-density')!.addEventListener('click', event => {
    densityOn = !densityOn
    const button = event.currentTarget as HTMLButtonElement
    button.setAttribute('aria-pressed', String(densityOn))
    applySelectionPaint()
  })
  document.querySelector<HTMLButtonElement>('#toggle-units')!.addEventListener('click', event => {
    unitsOn = !unitsOn
    const button = event.currentTarget as HTMLButtonElement
    button.setAttribute('aria-pressed', String(unitsOn))
    applySelectionPaint()
  })
  document.querySelector<HTMLButtonElement>('#toggle-3d')!.addEventListener('click', event => {
    mode3d = !mode3d
    const button = event.currentTarget as HTMLButtonElement
    button.setAttribute('aria-pressed', String(mode3d))
    for (const id of active) {
      if (mode3d && !map.getLayer(`${id}-extrusion`)) extrusion(id, currentLevel)
      else if (!mode3d && map.getLayer(`${id}-extrusion`)) map.removeLayer(`${id}-extrusion`)
    }
    map.easeTo({ pitch: mode3d ? 55 : 0, bearing: mode3d ? -20 : 0, duration: 550 })
    applySelectionPaint()
  })
  smoothEl.addEventListener('change', () => { void refreshAnalysis() })
  indicatorSelect.addEventListener('change', () => {
    indicator = indicatorSelect.value
    paintedKey = ''
    renderControls(currentLevel)
    renderThemes()
    sync()
    void refreshAnalysis()
  })
  indicatorSearch.addEventListener('input', () => renderControls(currentLevel))
  breaksEl.addEventListener('change', () => {
    breakMode = breaksEl.value as BreakMode
    paintedKey = ''
    sync()
  })
  languageEl.addEventListener('click', () => {
    language = language === 'es' ? 'en' : 'es'
    document.querySelector<HTMLElement>('#assignment-note')!.textContent = language === 'es'
      ? `${integer.format(catalog.assigned_manzanas_without_polygon)} manzanas sin polígono: población asignada a nivel de sector`
      : `${integer.format(catalog.assigned_manzanas_without_polygon)} blocks without polygons: population assigned at sector level`
    renderControls(currentLevel)
    renderThemes()
    saveHash(map)
    void refreshAnalysis()
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
  function unitCard(level: Level, key: string, properties: Record<string, unknown>): HTMLElement {
    const presentation = unitPresentation(level, key, language)
    const card = document.createElement('div')
    card.className = 'popup unit-popup'
    card.setAttribute('role', 'tooltip')
    const title = document.createElement('strong')
    title.className = 'unit-title'
    title.textContent = presentation.primary
    const context = document.createElement('small')
    context.className = 'unit-context'
    context.textContent = [presentation.level, presentation.route].filter(Boolean).join(' · ')
    const value = document.createElement('div')
    value.className = 'unit-value'
    const population = document.createElement('div')
    population.className = 'unit-population'
    population.textContent = `${language === 'es' ? 'Población' : 'Population'}: ${
      properties.population == null ? copy[language].noData : integer.format(Number(properties.population))}`
    card.append(title, context, value, population)
    const assigned = Number(properties.assigned_population) || 0
    if (assigned > 0) {
      const note = document.createElement('div')
      note.className = 'unit-note'
      note.textContent = language === 'es'
        ? `${integer.format(assigned)} personas de manzanas sin polígono: población asignada a nivel de sector`
        : `${integer.format(assigned)} people from blocks without polygons: assigned at sector level`
      card.append(note)
    }
    if (indicator === 'density') {
      const density = properties.density == null ? copy[language].noData
        : `${formatValue(Number(properties.density))} hab./km²`
      value.textContent = `${copy[language].density}: ${density}`
    } else {
      const definition = byId.get(indicator)!
      const sourceLevel = indicatorAvailable(definition.min_level, level) ? level
        : definition.min_level as Level
      const sourceKey = unitKeyAtLevel(key, sourceLevel)
      value.textContent = `${definition.name[language]}: …`
      if (sourceLevel !== level) {
        const note = document.createElement('div')
        note.className = 'unit-note'
        note.textContent = language === 'es'
          ? `Dato de ${levelLabel(sourceLevel, language).toLowerCase()}: disponible desde ese nivel`
          : `Value from ${levelLabel(sourceLevel, language).toLowerCase()}: available at that level`
        card.append(note)
      }
      void indicatorFile(base, sourceLevel,
        sourceLevel === 'sector' || sourceLevel === 'manzana' ? sourceKey.slice(0, 2) : undefined)
        .then(file => {
          const cell = file.cell(sourceKey, indicator)
          value.textContent = `${definition.name[language]}: ${cell?.value == null
            ? copy[language].noData : formatValue(cell.value)}`
          if (cell?.status === 1) {
            const note = document.createElement('div')
            note.className = 'unit-note'
            note.textContent = copy[language].small
            card.append(note)
          }
        }).catch(error => { value.textContent = `${definition.name[language]}: ${String(error)}` })
    }
    return card
  }
  let hoverPopup: maplibregl.Popup | null = null
  let hoveredSignature = ''
  map.on('load', sync)
  map.on('moveend', () => { sectorFallback = false; sync() })
  map.on('idle', () => {
    updateDensityBreaks()
    if (zoomLevel(map.getZoom()) !== 'manzana' || sectorFallback || currentLevel !== 'manzana'
      || !active.size || ![...active].every(id => map.isSourceLoaded(id))) return
    const canvas = map.getCanvas()
    const visibleBlocks = map.queryRenderedFeatures([[0, 0], [canvas.clientWidth, canvas.clientHeight]],
      { layers: [...active].map(id => `${id}-fill`) })
    if (!visibleBlocks.length) {
      sectorFallback = true
      sync()
    }
  })
  map.on('mousemove', event => {
    if (selection.mode === 'circle' || selection.mode === 'lasso') {
      hoverPopup?.remove(); hoverPopup = null; hoveredSignature = ''; return
    }
    const layers = [...active].map(id => `${id}-fill`)
    const feature = layers.length ? map.queryRenderedFeatures(event.point, { layers })[0] : null
    map.getCanvas().style.cursor = feature ? 'pointer' : ''
    const key = String(feature?.properties?.unit_key ?? '')
    if (!key) { hoverPopup?.remove(); hoverPopup = null; hoveredSignature = ''; return }
    const signature = `${currentLevel}:${key}:${indicator}:${language}`
    if (hoveredSignature !== signature) {
      hoverPopup?.remove()
      hoverPopup = new maplibregl.Popup({ closeButton: false, closeOnClick: false,
        maxWidth: '320px', offset: 14 })
        .setLngLat(event.lngLat)
        .setDOMContent(unitCard(currentLevel, key, feature!.properties as Record<string, unknown>))
        .addTo(map)
      hoveredSignature = signature
    } else hoverPopup?.setLngLat(event.lngLat)
  })
  map.getCanvas().addEventListener('mouseleave', () => {
    hoverPopup?.remove(); hoverPopup = null; hoveredSignature = ''
  })
  map.on('click', async event => {
    if (selection.mode === 'circle' || selection.mode === 'lasso') return
    const layers = [...active].map(id => `${id}-fill`)
    if (!layers.length) return
    const feature = map.queryRenderedFeatures(event.point, { layers })[0]
    const p = feature?.properties
    if (!p) return
    hoverPopup?.remove(); hoverPopup = null; hoveredSignature = ''
    await selection.click(feature)
    if (selection.mode === 'multi') return
    const level = currentLevel
    selectedKey = String(p.unit_key)
    renderBreadcrumb()
    saveHash(map)
    const card = unitCard(level, selectedKey, p as Record<string, unknown>)
    new maplibregl.Popup({ maxWidth: '290px' }).setLngLat(event.lngLat)
      .setDOMContent(card).addTo(map)
  })
  map.on('error', event => { statusEl.textContent = `Error de cartografía: ${event.error?.message ?? 'desconocido'}` })
}

start().catch(error => { statusEl.textContent = `No se pudo abrir el mapa: ${String(error)}` })
