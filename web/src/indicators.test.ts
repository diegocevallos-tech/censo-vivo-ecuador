import { describe, expect, it } from 'vitest'
import catalog from './generated/indicators.json'
import cases from '../../tests/indicator_cases.json'
import { evaluate, fitCantonPrior, type IndicatorDefinition } from './indicators'

const definitions = new Map(catalog.indicators.map(item => [item.id, item as IndicatorDefinition]))

describe('catalog-generated Python/TypeScript parity', () => {
  it('evaluates every indicator and quality variant within 1e-9', () => {
    expect(cases.length).toBeGreaterThan(100)
    for (const item of cases) {
      const definition = definitions.get(item.id)
      expect(definition).toBeDefined()
      const result = evaluate(definition!, item.aggregate as { counts: Record<string, number>; quality: 'exacto' | 'estimado'; estimated_percent: number }, {
        level: item.level, smoothing: item.smoothing,
        cantonPrior: item.prior ?? undefined,
      })
      const expected = item.expected
      expect(result.quality).toBe(expected.quality)
      expect(result.small_n).toBe(expected.small_n)
      expect(result.rank_eligible).toBe(expected.rank_eligible)
      expect(result.unavailable_reason).toBe(expected.unavailable_reason)
      if (expected.value === null) expect(result.value).toBeNull()
      else expect(Math.abs(result.value! - expected.value)).toBeLessThan(1e-9)
      expect(Math.abs(result.denominator - expected.denominator)).toBeLessThan(1e-9)
      if (expected.uncertainty === null) expect(result.uncertainty).toBeNull()
      else for (const key of ['lower', 'upper', 'sd', 'prior_strength'] as const) {
        expect(Math.abs(result.uncertainty![key] - expected.uncertainty[key])).toBeLessThan(1e-9)
      }
    }
  })

  it('fits the same canton prior', () => {
    const prior = fitCantonPrior([[4, 9], [30, 100], [8, 14]])
    expect(prior).not.toBeNull()
    expect(prior!.mean).toBeGreaterThan(0)
  })
})
