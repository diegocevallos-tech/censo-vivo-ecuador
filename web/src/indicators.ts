import type { Aggregate } from './aggregation'

export interface IndicatorDefinition {
  id: string
  kind: 'ratio' | 'difference_of_ratios' | 'pca' | 'shannon' | 'median_grouped' | 'weighted_mean'
  min_level: string
  min_n: number
  numerator?: string[]
  denominator?: string[]
  first_numerator?: string[]
  first_denominator?: string[]
  second_numerator?: string[]
  second_denominator?: string[]
  factor?: number
  categories?: string[][]
  age_groups?: string[][]
  source_table?: string
  source_variable?: string
  valid_min?: number
  valid_max?: number
  bayesian?: boolean
  components?: Array<{
    numerator: string[]; denominator: string[]
    second_numerator?: string[]; second_denominator?: string[]
    mean: number; scale: number; lower: number; upper: number; weight: number
  }>
}

export interface CantonPrior { mean: number; strength: number }
export interface IndicatorResult {
  value: number | null
  denominator: number
  quality: Aggregate['quality']
  estimated_percent: number
  small_n: boolean
  rank_eligible: boolean
  uncertainty: { lower: number; upper: number; sd: number; prior_strength: number } | null
  unavailable_reason: string | null
}

const levels = ['manzana', 'sector', 'zona', 'parroquia', 'canton', 'provincia', 'nacion']
const sum = (counts: Record<string, number>, keys: string[]): number =>
  keys.reduce((total, key) => total + (counts[key] ?? 0), 0)

export function fitCantonPrior(peers: [number, number][]): CantonPrior | null {
  const valid = peers.filter(([, total]) => total > 0)
  if (valid.length < 2 || valid.some(([success, total]) => success < 0 || success > total)) return null
  const trials = valid.reduce((total, [, n]) => total + n, 0)
  const mean = valid.reduce((total, [x]) => total + x, 0) / trials
  const observed = valid.reduce((v, [x, n]) => v + (x / n - mean) ** 2, 0) / valid.length
  const sampling = valid.reduce((v, [, n]) => v + mean * (1 - mean) / n, 0) / valid.length
  const between = Math.max(0, observed - sampling)
  const strength = between > 0
    ? Math.min(1_000_000, Math.max(0, mean * (1 - mean) / between - 1))
    : 1_000_000
  return { mean, strength }
}

export function evaluate(
  definition: IndicatorDefinition,
  aggregate: Aggregate,
  options: { level?: string; smoothing?: boolean; cantonPrior?: CantonPrior } = {},
): IndicatorResult {
  // Dispersed rural areas use the sector itself as their finest unit.
  const level = options.level === 'sector_disperso' ? 'sector' : options.level ?? 'manzana'
  if (!levels.includes(level) || !levels.includes(definition.min_level)) throw new Error('Unknown census level')
  if (levels.indexOf(level) < levels.indexOf(definition.min_level)) {
    return { value: null, denominator: 0, quality: aggregate.quality,
      estimated_percent: aggregate.estimated_percent, small_n: false,
      rank_eligible: false, uncertainty: null,
      unavailable_reason: `Disponible desde ${definition.min_level}` }
  }
  const counts = aggregate.counts
  let numerator = 0
  let denominator = 0
  let value: number | null = null
  if (definition.kind === 'ratio') {
    numerator = sum(counts, definition.numerator ?? [])
    denominator = sum(counts, definition.denominator ?? [])
    if (denominator > 0) value = numerator / denominator * (definition.factor ?? 1)
  } else if (definition.kind === 'difference_of_ratios') {
    const firstN = sum(counts, definition.first_numerator ?? [])
    const firstD = sum(counts, definition.first_denominator ?? [])
    const secondN = sum(counts, definition.second_numerator ?? [])
    const secondD = sum(counts, definition.second_denominator ?? [])
    denominator = Math.min(firstD, secondD)
    if (denominator > 0) value = (firstN / firstD - secondN / secondD) * (definition.factor ?? 1)
  } else if (definition.kind === 'pca') {
    const pieces: number[] = []
    const sizes: number[] = []
    for (const component of definition.components ?? []) {
      const firstD = sum(counts, component.denominator)
      sizes.push(firstD)
      if (firstD === 0) break
      let raw = sum(counts, component.numerator) / firstD
      if (component.second_numerator && component.second_denominator) {
        const secondD = sum(counts, component.second_denominator)
        sizes.push(secondD)
        if (secondD === 0) break
        raw -= sum(counts, component.second_numerator) / secondD
      }
      const clipped = Math.min(component.upper, Math.max(component.lower, raw))
      pieces.push(component.weight * (clipped - component.mean) / component.scale)
    }
    denominator = sizes.length ? Math.min(...sizes) : 0
    if (pieces.length === (definition.components ?? []).length) {
      value = pieces.reduce((a, b) => a + b, 0)
    }
  } else if (definition.kind === 'shannon' || definition.kind === 'median_grouped') {
    const groups = definition.kind === 'shannon' ? definition.categories ?? [] : definition.age_groups ?? []
    const values = groups.map(group => sum(counts, group))
    denominator = values.reduce((a, b) => a + b, 0)
    if (denominator > 0) {
      if (definition.kind === 'shannon') {
        value = -values.reduce((entropy, count) => {
          const probability = count / denominator
          return entropy + (probability > 0 ? probability * Math.log(probability) : 0)
        }, 0) / Math.log(values.length)
      } else {
        const middle = denominator / 2
        let running = 0
        for (let index = 0; index < values.length; index++) {
          const count = values[index]
          if (count > 0 && running + count >= middle) {
            value = index * 5 + (index === 20 ? 21 : 5) * (middle - running) / count
            break
          }
          running += count
        }
      }
    }
  } else if (definition.kind === 'weighted_mean') {
    let weighted = 0
    for (let category = definition.valid_min ?? 0; category <= (definition.valid_max ?? -1); category++) {
      const count = counts[`cat:${definition.source_table}:${definition.source_variable}:${category}`] ?? 0
      denominator += count
      weighted += category * count
    }
    if (denominator > 0) value = weighted / denominator
  } else throw new Error(`Unsupported indicator kind: ${definition.kind}`)

  let uncertainty: IndicatorResult['uncertainty'] = null
  const prior = options.cantonPrior
  if (options.smoothing && definition.bayesian && prior && denominator > 0 && definition.kind === 'ratio') {
    if (numerator < 0 || numerator > denominator) throw new Error('Invalid binomial rate')
    const alpha = numerator + prior.mean * prior.strength
    const beta = denominator - numerator + (1 - prior.mean) * prior.strength
    const mean = alpha / (alpha + beta)
    const variance = alpha * beta / ((alpha + beta) ** 2 * (alpha + beta + 1))
    const sd = Math.sqrt(variance)
    const factor = definition.factor ?? 1
    value = factor * mean
    uncertainty = { lower: factor * Math.max(0, mean - 1.96 * sd),
      upper: factor * Math.min(1, mean + 1.96 * sd), sd: factor * sd,
      prior_strength: prior.strength }
  }
  const small_n = denominator < definition.min_n
  return { value, denominator, quality: aggregate.quality,
    estimated_percent: aggregate.estimated_percent, small_n,
    rank_eligible: !small_n && aggregate.quality === 'exacto', uncertainty,
    unavailable_reason: null }
}
