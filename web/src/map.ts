import * as maplibregl from 'maplibre-gl'
import type { Map } from 'maplibre-gl'
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url'
import { Protocol } from 'pmtiles'
import 'maplibre-gl/dist/maplibre-gl.css'
import './style.css'

type Level = 'nacion' | 'provincia' | 'canton' | 'parroquia' | 'sector' | 'manzana'
type Bounds = [number, number, number, number]
interface Catalog {
  geom_version: string
  province_bounds: Record<string, Bounds>
  tile_files: Record<Level, string[]>
  matched_geometries: Record<Level, number>
  assigned_manzanas_without_polygon: number
}

const base = import.meta.env.BASE_URL
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
    <section class="data-card" aria-label="Indicador activo">
      <div class="card-head"><span class="eyebrow">01 / TERRITORIO</span><span id="level">Cargando…</span></div>
      <h2>Densidad de población</h2><p>Habitantes por kilómetro cuadrado de la unidad censal.</p>
      <div class="ramp" aria-hidden="true"></div>
      <div class="ticks"><span>0</span><span>50</span><span>200</span><span>1 mil</span><span>5 mil</span><span>15 mil+</span></div>
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
  const map: Map = new maplibregl.Map({
    container: 'map', center: [-79.45, -1.52], zoom: 5, minZoom: 2, maxZoom: 16.5,
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
      map.addSource(id, { type: 'vector', url: `pmtiles://${url}` })
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
  }
  map.on('load', sync)
  map.on('moveend', sync)
  map.on('mousemove', event => {
    const layers = [...active].map(id => `${id}-fill`)
    map.getCanvas().style.cursor = layers.length && map.queryRenderedFeatures(event.point, { layers }).length
      ? 'pointer' : ''
  })
  map.on('click', event => {
    const layers = [...active].map(id => `${id}-fill`)
    if (!layers.length) return
    const p = map.queryRenderedFeatures(event.point, { layers })[0]?.properties
    if (!p) return
    const level = zoomLevel(map.getZoom())
    const people = p.population == null ? 'Sin dato' : integer.format(Number(p.population))
    const density = p.density == null ? 'Sin dato' : decimal.format(Number(p.density))
    const assigned = Number(p.assigned_population) > 0
      ? `<div class="popup-note">${integer.format(Number(p.assigned_population))} personas de manzanas sin polígono asignadas al sector</div>` : ''
    new maplibregl.Popup({ maxWidth: '280px' }).setLngLat(event.lngLat)
      .setHTML(`<div class="popup"><small>${names[level]} · ${p.unit_key}</small><strong>${people}</strong><span>personas</span><div>${density} hab./km²</div>${assigned}</div>`)
      .addTo(map)
  })
  map.on('error', event => { statusEl.textContent = `Error de cartografía: ${event.error?.message ?? 'desconocido'}` })
}

start().catch(error => { statusEl.textContent = `No se pudo abrir el mapa: ${String(error)}` })
