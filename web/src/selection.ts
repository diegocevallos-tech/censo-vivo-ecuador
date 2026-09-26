import KDBush from 'kdbush'
import * as turf from '@turf/turf'
import type { Feature, Polygon, MultiPolygon } from 'geojson'
import type { Map as MapLibreMap, MapGeoJSONFeature } from 'maplibre-gl'
import { aggregate } from './aggregation'
import type { Aggregate, SelectedUnit } from './aggregation'
import { countChunk } from './countChunks'
import type { Level } from './indicatorMaps'

export type SelectionMode = 'inspect' | 'circle' | 'lasso' | 'multi'
export interface SelectionResult {
  aggregate: Aggregate
  unitCount: number
  keys: string[]
  label: string
  assignedPopulation: number
  officialUnitKey?: string
  density?: number
}

interface Options {
  map: MapLibreMap
  base: string
  shell: HTMLElement
  getLevel: () => Level
  getLanguage: () => 'es' | 'en'
  getLayers: () => string[]
  onPreview: (population: number, radiusKm: number, computeMs: number) => void
  onResult: (result: SelectionResult | null) => void
  onHighlight: (keys: Set<string>) => void
  onStatus: (message: string) => void
}

interface PointUnit { key: string; x: number; y: number; population: number }
type AreaFeature = Feature<Polygon | MultiPolygon>

export function createSelection(options: Options) {
  const { map, base, shell } = options
  let mode: SelectionMode = 'inspect'
  let pointUnits: PointUnit[] = []
  let index: KDBush | null = null
  let selected = new Set<string>()
  let circleCenter: { x: number; y: number } | null = null
  let radius = 0
  let drag: 'create' | 'center' | 'radius' | 'lasso' | null = null
  let lasso: { x: number; y: number }[] = []
  let pendingFrame = 0
  const previewTimes: number[] = []
  const overlay = document.createElement('div')
  overlay.className = 'selection-overlay'
  overlay.innerHTML = `<div class="selection-circle" hidden><button class="selection-center"
    type="button" aria-label="Mover centro del círculo"></button><button class="selection-radius"
    type="button" aria-label="Cambiar radio del círculo"></button></div>
    <svg class="selection-lasso" aria-hidden="true"><path></path></svg>`
  shell.append(overlay)
  const circle = overlay.querySelector<HTMLElement>('.selection-circle')!
  const centerHandle = overlay.querySelector<HTMLButtonElement>('.selection-center')!
  const radiusHandle = overlay.querySelector<HTMLButtonElement>('.selection-radius')!
  const lassoPath = overlay.querySelector<SVGPathElement>('.selection-lasso path')!

  function point(event: { clientX: number; clientY: number }) {
    const bounds = map.getCanvas().getBoundingClientRect()
    return { x: event.clientX - bounds.left, y: event.clientY - bounds.top }
  }

  function redraw() {
    if (circleCenter && radius > 0) {
      circle.hidden = false
      circle.style.left = `${circleCenter.x - radius}px`
      circle.style.top = `${circleCenter.y - radius}px`
      circle.style.width = `${radius * 2}px`
      circle.style.height = `${radius * 2}px`
    } else circle.hidden = true
    lassoPath.setAttribute('d', lasso.length
      ? `M ${lasso.map(p => `${p.x} ${p.y}`).join(' L ')}${drag ? '' : ' Z'}` : '')
  }

  function rebuildIndex() {
    const canvas = map.getCanvas()
    const features = map.queryRenderedFeatures([[0, 0], [canvas.clientWidth, canvas.clientHeight]],
      { layers: options.getLayers() })
    const units = new Map<string, PointUnit>()
    for (const feature of features) {
      const key = String(feature.properties.unit_key ?? '')
      if (!key || units.has(key)) continue
      const center = turf.centroid(feature.geometry as Polygon | MultiPolygon).geometry.coordinates
      const pixel = map.project(center as [number, number])
      units.set(key, { key, x: pixel.x, y: pixel.y,
        population: Number(feature.properties.population) || 0 })
    }
    pointUnits = [...units.values()]
    index = new KDBush(pointUnits.length)
    for (const unit of pointUnits) index.add(unit.x, unit.y)
    index.finish()
  }

  function preview() {
    pendingFrame = 0
    if (!drag || !circleCenter || !index || radius <= 0) return
    const start = performance.now()
    let population = 0
    for (const row of index.within(circleCenter.x, circleCenter.y, radius)) {
      population += pointUnits[row].population
    }
    const edge = map.unproject([circleCenter.x + radius, circleCenter.y])
    const center = map.unproject([circleCenter.x, circleCenter.y])
    const km = turf.distance([center.lng, center.lat], [edge.lng, edge.lat])
    const computeMs = performance.now() - start
    previewTimes.push(computeMs)
    if (previewTimes.length > 120) previewTimes.shift()
    options.onPreview(population, km, computeMs)
  }

  function schedulePreview() {
    if (!pendingFrame) pendingFrame = requestAnimationFrame(preview)
  }

  function shape(): AreaFeature | null {
    if (mode === 'circle' && circleCenter && radius > 0) {
      const center = map.unproject([circleCenter.x, circleCenter.y])
      const edge = map.unproject([circleCenter.x + radius, circleCenter.y])
      const km = turf.distance([center.lng, center.lat], [edge.lng, edge.lat])
      return turf.circle([center.lng, center.lat], km, { steps: 64, units: 'kilometers' })
    }
    if (mode === 'lasso' && lasso.length >= 3) {
      const coordinates = lasso.map(p => {
        const location = map.unproject([p.x, p.y])
        return [location.lng, location.lat]
      })
      coordinates.push(coordinates[0])
      return turf.polygon([coordinates])
    }
    return null
  }

  function candidateFeatures(): MapGeoJSONFeature[] {
    if (mode === 'circle' && circleCenter) {
      const west = Math.max(0, circleCenter.x - radius)
      const east = Math.min(map.getCanvas().clientWidth, circleCenter.x + radius)
      const north = Math.max(0, circleCenter.y - radius)
      const south = Math.min(map.getCanvas().clientHeight, circleCenter.y + radius)
      return map.queryRenderedFeatures([[west, north], [east, south]],
        { layers: options.getLayers() })
    }
    if (mode === 'lasso' && lasso.length) {
      const x = lasso.map(p => p.x)
      const y = lasso.map(p => p.y)
      return map.queryRenderedFeatures([[Math.min(...x), Math.min(...y)],
        [Math.max(...x), Math.max(...y)]], { layers: options.getLayers() })
    }
    return []
  }

  function coverageByKey(selection: AreaFeature): Map<string, number> {
    const areas = new Map<string, { included: number; total: number }>()
    const seen = new Set<string>()
    for (const item of candidateFeatures()) {
      const key = String(item.properties.unit_key ?? '')
      if (!key || !['Polygon', 'MultiPolygon'].includes(item.geometry.type)) continue
      const polygon = turf.feature(item.geometry as Polygon | MultiPolygon)
      const signature = `${key}:${JSON.stringify((item.geometry as Polygon | MultiPolygon).coordinates)}`
      if (seen.has(signature)) continue
      seen.add(signature)
      const overlap = turf.intersect(turf.featureCollection([polygon, selection]))
      if (!overlap) continue
      const area = turf.area(overlap)
      if (area <= 0) continue
      const current = areas.get(key) ?? { included: 0, total: Number(item.properties.area_km2) * 1e6 }
      current.included += area
      areas.set(key, current)
    }
    return new Map([...areas].map(([key, item]) => [key,
      item.total > 0 ? Math.min(1, item.included / item.total > 0.995 ? 1 :
        item.included / item.total) : 0]))
  }

  async function countSelection(coverages: Map<string, number>, label: string,
                                officialUnitKey?: string, density?: number) {
    const level = options.getLevel()
    const provinceKeys = level === 'nacion'
      ? Array.from({ length: 24 }, (_, index) => String(index + 1).padStart(2, '0'))
      : [...new Set([...coverages.keys()].map(key => key.slice(0, 2)))]
    const sourceLevel = level === 'manzana' ? 'finest' : 'sector'
    const chunks = await Promise.all(provinceKeys.map(province => countChunk(base, province, sourceLevel)))
    const byProvince = new Map(provinceKeys.map((province, i) => [province, chunks[i]]))
    const rows: SelectedUnit[] = []
    const selectedKeys = [...coverages.keys()]
    for (const [key, coverage] of coverages) {
      const targetChunks = level === 'nacion' ? chunks : [byProvince.get(key.slice(0, 2))!]
      for (const chunk of targetChunks) {
        const units = level === 'nacion' ? chunk.keys
          : level === 'manzana' || level === 'sector' ? [key] : chunk.keysWithPrefix(key)
        for (const unit of units) {
          const counts = chunk.counts(unit)
          if (counts) rows.push({ key: unit, counts, coverage })
        }
      }
    }
    let assignedPopulation = 0
    // Unmapped blocks remain at sector level. Include that row only when all
    // mapped blocks of the sector are selected whole; there is no defensible
    // polygon with which to apportion it inside a partial spatial selection.
    if (level === 'manzana') {
      const sectors = new Set<string>()
      for (const row of rows) {
        sectors.add(row.key.slice(0, 12))
      }
      for (const sector of sectors) {
        const chunk = byProvince.get(sector.slice(0, 2))!
        const remainder = chunk.counts(sector)
        if (!remainder || !remainder.population) continue
        const mapped = chunk.keysWithPrefix(sector).filter(key => key.length === 15)
        if (mapped.length && mapped.every(key => coverages.get(key) === 1)) {
          rows.push({ key: sector, counts: remainder, coverage: 1 })
          assignedPopulation += remainder.population
        }
      }
    }
    const result = aggregate(rows)
    selected = new Set(selectedKeys)
    options.onHighlight(selected)
    options.onResult({ aggregate: result, unitCount: selectedKeys.length,
      keys: selectedKeys, label, assignedPopulation, officialUnitKey, density })
  }

  async function finishShape() {
    const polygon = shape()
    if (!polygon) return
    options.onStatus(options.getLanguage() === 'es' ? 'Calculando selección…' : 'Calculating selection…')
    try {
      const english = options.getLanguage() === 'en'
      await countSelection(coverageByKey(polygon), mode === 'circle'
        ? (english ? 'Circle' : 'Círculo') : (english ? 'Lasso' : 'Lazo'))
    } catch (error) { options.onStatus(`Error de selección: ${String(error)}`) }
  }

  function beginDrag(kind: 'create' | 'center' | 'radius' | 'lasso', event: MouseEvent | PointerEvent) {
    drag = kind
    const cursor = point(event)
    if (kind === 'create') { circleCenter = cursor; radius = 1; redraw() }
    if (kind === 'lasso') { lasso = [cursor]; redraw() }
    event.preventDefault()
  }

  function move(event: PointerEvent) {
    if (!drag) return
    const cursor = point(event)
    if (drag === 'create' || drag === 'radius') {
      if (circleCenter) radius = Math.max(2, Math.hypot(cursor.x - circleCenter.x,
        cursor.y - circleCenter.y))
    } else if (drag === 'center') circleCenter = cursor
    else if (drag === 'lasso') {
      if (!lasso.length || Math.hypot(cursor.x - lasso.at(-1)!.x,
        cursor.y - lasso.at(-1)!.y) >= 5) lasso.push(cursor)
    }
    redraw()
    schedulePreview()
  }

  async function end() {
    if (!drag) return
    const finished = drag
    drag = null
    if (pendingFrame) cancelAnimationFrame(pendingFrame)
    pendingFrame = 0
    redraw()
    if (finished === 'lasso' || (circleCenter && radius >= 5)) await finishShape()
  }

  map.getCanvas().addEventListener('pointerdown', event => {
    if (event.button !== 0) return
    if (mode === 'circle') beginDrag('create', event)
    else if (mode === 'lasso') beginDrag('lasso', event)
  })
  centerHandle.addEventListener('pointerdown', event => beginDrag('center', event))
  radiusHandle.addEventListener('pointerdown', event => beginDrag('radius', event))
  window.addEventListener('pointermove', move)
  window.addEventListener('pointerup', () => { void end() })
  map.on('moveend', () => { rebuildIndex(); redraw() })
  map.on('idle', rebuildIndex)

  return {
    get mode() { return mode },
    get keys() { return selected },
    get previewP95Ms() {
      const times = [...previewTimes].sort((a, b) => a - b)
      return times.length ? times[Math.floor(times.length * 0.95)] : 0
    },
    setMode(next: SelectionMode) {
      mode = next
      if (next === 'circle' || next === 'lasso') map.dragPan.disable()
      else map.dragPan.enable()
      shell.classList.toggle('drawing', next === 'circle' || next === 'lasso')
      if (next !== 'circle') { circleCenter = null; radius = 0 }
      if (next !== 'lasso') lasso = []
      redraw()
    },
    clear() {
      selected = new Set()
      circleCenter = null; radius = 0; lasso = []
      redraw()
      options.onHighlight(selected)
      options.onResult(null)
    },
    async click(feature: MapGeoJSONFeature) {
      if (mode === 'circle' || mode === 'lasso') return
      const key = String(feature.properties.unit_key)
      if (mode === 'multi') {
        if (selected.has(key)) selected.delete(key)
        else selected.add(key)
      } else selected = new Set([key])
      if (!selected.size) { this.clear(); return }
      options.onStatus(options.getLanguage() === 'es' ? 'Cargando conteos oficiales…' : 'Loading official counts…')
      try { await countSelection(new Map([...selected].map(item => [item, 1])),
        mode === 'multi' ? (options.getLanguage() === 'es' ? 'Multiselección' : 'Multiple units')
          : (options.getLanguage() === 'es' ? 'Unidad oficial' : 'Official unit'),
        selected.size === 1 ? [...selected][0] : undefined,
        selected.size === 1 ? Number(feature.properties.density) : undefined) }
      catch (error) { options.onStatus(`Error de selección: ${String(error)}`) }
    },
  }
}
