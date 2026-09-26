import profile from './generated/nationalProfile.json'
import indicatorCatalog from './generated/indicators.json'
import { evaluate } from './indicators'
import type { CantonPrior, IndicatorDefinition } from './indicators'
import { indicatorFile } from './indicatorMaps'
import { availableAtLevel } from './indicatorMaps'
import type { Level } from './indicatorMaps'
import { levelLabel, unitKeyAtLevel, unitPresentation } from './placeLabels'
import type { SelectionResult } from './selection'

const ageGroups = profile.age_groups
const definitions = new Map(indicatorCatalog.indicators.map(item => [item.id, item]))
const featured = ['female_share', 'aging_index', 'mean_schooling_25_plus',
  'potential_solitude_65', 'internet_use_5_plus', 'labour_gender_gap']

function number(value: number, language: 'es' | 'en', decimals = 0): string {
  return new Intl.NumberFormat(language === 'es' ? 'es-EC' : 'en-US',
    { maximumFractionDigits: decimals }).format(value)
}

function pyramid(counts: Record<string, number>, language: 'es' | 'en'): SVGSVGElement {
  const male = ageGroups.map(age => counts[`core:age_${age}_m`] ?? 0)
  const female = ageGroups.map(age => counts[`core:age_${age}_f`] ?? 0)
  const population = counts['core:population'] || 1
  const national = profile.population
  const max = Math.max(...male.map(v => v / population),
    ...female.map(v => v / population),
    ...profile.male_counts.map(v => v / national),
    ...profile.female_counts.map(v => v / national), 0.01)
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  svg.setAttribute('viewBox', '0 0 310 247')
  svg.setAttribute('role', 'img')
  svg.setAttribute('aria-label', language === 'es' ? 'Pirámide de edad por sexo con silueta nacional'
    : 'Age pyramid by sex with national outline')
  const add = (tag: string, attrs: Record<string, string>) => {
    const node = document.createElementNS('http://www.w3.org/2000/svg', tag)
    for (const [name, value] of Object.entries(attrs)) node.setAttribute(name, value)
    svg.append(node)
    return node
  }
  add('line', { x1: '155', x2: '155', y1: '9', y2: '224', stroke: '#879da4',
    'stroke-width': '1' })
  const nationalMale: string[] = []
  const nationalFemale: string[] = []
  for (let i = 0; i < ageGroups.length; i++) {
    const y = 10 + (20 - i) * 10
    const leftWidth = 122 * male[i] / population / max
    const rightWidth = 122 * female[i] / population / max
    add('rect', { x: String(155 - leftWidth), y: String(y), width: String(leftWidth),
      height: '8', fill: '#4b9cb2' })
    add('rect', { x: '155', y: String(y), width: String(rightWidth),
      height: '8', fill: '#f5b82e' })
    nationalMale.push(`${155 - 122 * profile.male_counts[i] / national / max},${y + 4}`)
    nationalFemale.push(`${155 + 122 * profile.female_counts[i] / national / max},${y + 4}`)
    if (i % 5 === 0 || i === 20) {
      const label = add('text', { x: '152', y: String(y + 7), 'text-anchor': 'end',
        fill: '#dbe7ea', 'font-size': '8' })
      label.textContent = ageGroups[i].replace('_', '–')
    }
  }
  add('polyline', { points: nationalMale.join(' '), fill: 'none', stroke: '#f4f9f8',
    'stroke-width': '1.3', opacity: '0.9' })
  add('polyline', { points: nationalFemale.join(' '), fill: 'none', stroke: '#f4f9f8',
    'stroke-width': '1.3', opacity: '0.9' })
  const maleLabel = add('text', { x: '75', y: '239', 'text-anchor': 'middle',
    fill: '#8fcedc', 'font-size': '10' })
  maleLabel.textContent = language === 'es' ? 'Hombres' : 'Men'
  const femaleLabel = add('text', { x: '235', y: '239', 'text-anchor': 'middle',
    fill: '#f5b82e', 'font-size': '10' })
  femaleLabel.textContent = language === 'es' ? 'Mujeres' : 'Women'
  return svg
}

function ageBand(counts: Record<string, number>, start: number, stop: number): number {
  return ageGroups.slice(start, stop).reduce((sum, age) => sum +
    (counts[`core:age_${age}_m`] ?? 0) + (counts[`core:age_${age}_f`] ?? 0), 0)
}

export async function renderAnalysis(panel: HTMLElement, selection: SelectionResult | null,
                                     options: { language: 'es' | 'en'; level: Level;
                                       base: string; smooth: boolean;
                                       activeIndicator?: string;
                                       prior?: CantonPrior | null }) {
  panel.replaceChildren()
  const { language, level, base, smooth, prior } = options
  if (!selection) {
    panel.textContent = language === 'es'
      ? 'Selecciona una unidad, dibuja un círculo o traza un lazo para abrir el análisis.'
      : 'Choose a unit, draw a circle, or trace a lasso to start the analysis.'
    return
  }
  const { aggregate: values, assignedPopulation } = selection
  const counts = values.counts
  const place = selection.officialUnitKey
    ? unitPresentation(level, selection.officialUnitKey, language) : null
  const heading = document.createElement('h3')
  heading.textContent = place?.primary ?? `${selection.label} · ${number(selection.unitCount, language)} ${
    selection.unitCount === 1 ? (language === 'es' ? 'unidad' : 'unit')
      : (language === 'es' ? 'unidades' : 'units')}`
  panel.append(heading)
  if (place) {
    const context = document.createElement('p')
    context.className = 'analysis-place-context'
    context.textContent = [place.level, place.route].filter(Boolean).join(' · ')
    panel.append(context)
    const active = document.createElement('p')
    active.className = 'analysis-place-metric'
    let sourceNote: HTMLElement | null = null
    if (options.activeIndicator === 'density') {
      active.textContent = `${language === 'es' ? 'Densidad de población' : 'Population density'}: ${
        Number.isFinite(selection.density) ? `${number(selection.density!, language, 1)} hab./km²` : '—'}`
    } else if (options.activeIndicator) {
      const definition = definitions.get(options.activeIndicator)
      const sourceLevel = definition && !availableAtLevel(definition.min_level as Level, level)
        ? definition.min_level as Level : level
      const sourceKey = unitKeyAtLevel(selection.officialUnitKey!, sourceLevel)
      try {
        const file = await indicatorFile(base, sourceLevel,
          sourceLevel === 'sector' || sourceLevel === 'manzana' ? sourceKey.slice(0, 2) : undefined)
        const cell = file.cell(sourceKey, options.activeIndicator)
        active.textContent = `${definition?.name[language] ?? options.activeIndicator}: ${
          cell?.value == null ? '—' : number(cell.value, language, 2)}`
        if (sourceLevel !== level) {
          sourceNote = document.createElement('small')
          sourceNote.className = 'analysis-place-note'
          sourceNote.textContent = language === 'es'
            ? `Dato de ${levelLabel(sourceLevel, language).toLowerCase()}`
            : `Value from ${levelLabel(sourceLevel, language).toLowerCase()}`
        }
      } catch {
        active.textContent = `${definition?.name[language] ?? options.activeIndicator}: —`
      }
    }
    panel.append(active)
    if (sourceNote) panel.append(sourceNote)
    const people = document.createElement('p')
    people.className = 'analysis-place-population'
    people.textContent = `${language === 'es' ? 'Población' : 'Population'}: ${
      number(counts['core:population'] ?? 0, language)}`
    panel.append(people)
  }
  const quality = document.createElement('p')
  quality.className = 'quality'
  quality.textContent = values.quality === 'exacto' ? (language === 'es' ? 'Exacto' : 'Exact')
    : `${language === 'es' ? 'Estimado' : 'Estimated'} · ${number(values.estimated_percent, language, 1)} %`
  panel.append(quality)
  if (assignedPopulation > 0) {
    const assigned = document.createElement('p')
    assigned.className = 'assigned-note'
    assigned.textContent = `${number(assignedPopulation, language)} ${language === 'es'
      ? 'personas asignadas a nivel de sector por falta de polígono'
      : 'people assigned at sector level due to missing blocks'}`
    panel.append(assigned)
  }
  const population = counts['core:population'] ?? 0
  const female = counts['core:sex_female'] ?? 0
  const male = counts['core:sex_male'] ?? 0
  const femalePercent = male + female > 0 ? 100 * female / (male + female) : 0
  const donut = document.createElement('div')
  donut.className = 'donut-row'
  const ring = document.createElement('div')
  ring.className = 'donut'
  ring.style.background = `conic-gradient(#f5b82e 0 ${femalePercent}%, #4b9cb2 ${femalePercent}% 100%)`
  ring.setAttribute('role', 'img')
  ring.setAttribute('aria-label', `${number(femalePercent, language, 1)}% ${language === 'es' ? 'mujeres' : 'women'}`)
  const summary = document.createElement('div')
  summary.innerHTML = `<strong>${number(population, language)}</strong><small>${language === 'es'
    ? 'personas' : 'people'}</small><span>${number(male, language)} ${language === 'es'
    ? 'hombres' : 'men'} · ${number(female, language)} ${language === 'es' ? 'mujeres' : 'women'}</span>`
  donut.append(ring, summary)
  panel.append(donut)
  const pyramidTitle = document.createElement('h4')
  pyramidTitle.textContent = language === 'es' ? 'Pirámide de edades' : 'Age pyramid'
  panel.append(pyramidTitle, pyramid(counts, language))
  const nationalLine = document.createElement('p')
  nationalLine.className = 'chart-note'
  nationalLine.textContent = language === 'es' ? 'Línea blanca: silueta nacional.'
    : 'White line: national outline.'
  panel.append(nationalLine)
  const barsTitle = document.createElement('h4')
  barsTitle.textContent = language === 'es' ? 'Estructura por edad' : 'Age composition'
  panel.append(barsTitle)
  for (const [label, value] of [
    ['0–14', ageBand(counts, 0, 3)],
    ['15–64', ageBand(counts, 3, 13)],
    ['65+', ageBand(counts, 13, 21)],
  ] as const) {
    const row = document.createElement('div')
    row.className = 'bar-row'
    const percent = population > 0 ? 100 * value / population : 0
    row.innerHTML = `<span>${label}</span><div class="bar-track"><i style="width:${Math.min(100, percent)}%"></i></div><strong>${number(percent, language, 1)}%</strong>`
    panel.append(row)
  }
  const indexTitle = document.createElement('h4')
  indexTitle.textContent = language === 'es' ? 'Índices clave' : 'Key indicators'
  panel.append(indexTitle)
  let referenceFile: Awaited<ReturnType<typeof indicatorFile>> | null = null
  try {
    referenceFile = await indicatorFile(base, 'parroquia')
  } catch { /* The index cards still work without percentile data. */ }
  const cardIds = options.activeIndicator && options.activeIndicator !== 'density'
    ? [...new Set([options.activeIndicator, ...featured])] : featured
  for (const id of cardIds) {
    const definition = definitions.get(id) as unknown as IndicatorDefinition & {
      name: { es: string; en: string }
    }
    if (!definition) continue
    const result = evaluate(definition, values, { level, smoothing: smooth, cantonPrior: prior ?? undefined })
    if (result.value == null || result.unavailable_reason) continue
    const card = document.createElement('div')
    card.className = 'index-card'
    const title = document.createElement('span')
    title.textContent = definition.name[language]
    const figure = document.createElement('strong')
    figure.textContent = number(result.value, language, 1)
    card.append(title, figure)
    if (result.small_n) {
      const warning = document.createElement('small')
      warning.textContent = language === 'es' ? 'Pocos casos · sin percentil'
        : 'Few cases · no percentile'
      card.append(warning)
    } else if (result.rank_eligible && referenceFile) {
      const reference = referenceFile.eligibleValues(id)
      if (reference.length) {
      const percent = 100 * reference.filter(value => value <= result.value!).length / reference.length
      const rank = document.createElement('small')
      rank.textContent = `${language === 'es' ? 'Percentil parroquial' : 'Parish percentile'} ${number(percent, language, 0)}`
      card.append(rank)
      }
    }
    panel.append(card)
  }
}
