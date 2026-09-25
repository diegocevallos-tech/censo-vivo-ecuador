import { describe, expect, it } from 'vitest'
import cases from '../../tests/aggregation_cases.json'
import { aggregate } from './aggregation'

describe('official-unit aggregation', () => {
  it('matches shared Python cases within 1e-9', () => {
    for (const item of cases) {
      const result = aggregate(item.units)
      for (const [field, expected] of Object.entries(item.counts)) {
        expect(Math.abs(result.counts[field] - expected)).toBeLessThan(1e-9)
      }
      expect(result.quality).toBe(item.quality)
      expect(Math.abs(result.estimated_percent - item.estimated_percent)).toBeLessThan(1e-9)
    }
  })
})
