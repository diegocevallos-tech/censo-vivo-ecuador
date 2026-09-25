/** Sum official census-unit counts; weight only units cut by the selection border. */
export interface SelectedUnit {
  key: string
  counts: Record<string, number>
  coverage?: number
}

export interface Aggregate {
  counts: Record<string, number>
  quality: 'exacto' | 'estimado'
  estimated_percent: number
}

export function aggregate(units: SelectedUnit[]): Aggregate {
  const values: Record<string, number> = {}
  let estimatedPopulation = 0
  let partial = false
  for (const unit of units) {
    const coverage = unit.coverage ?? 1
    if (!Number.isFinite(coverage) || coverage < 0 || coverage > 1) {
      throw new Error(`Invalid area coverage for ${unit.key}`)
    }
    for (const [name, count] of Object.entries(unit.counts)) {
      if (!Number.isFinite(count) || count < 0) {
        throw new Error(`Negative or invalid census count for ${unit.key}.${name}`)
      }
      values[name] = (values[name] ?? 0) + count * coverage
    }
    if (coverage > 0 && coverage < 1) {
      partial = true
      estimatedPopulation += (unit.counts.population ?? 0) * coverage
    }
  }
  const population = values.population ?? 0
  return {
    counts: values,
    quality: partial ? 'estimado' : 'exacto',
    estimated_percent: population > 0 ? 100 * estimatedPopulation / population : 0,
  }
}
