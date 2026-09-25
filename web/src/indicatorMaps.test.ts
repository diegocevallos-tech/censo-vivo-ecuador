import { describe, expect, it } from 'vitest'
import { availableAtLevel, classifyBreaks } from './indicatorMaps'

describe('choropleth breaks', () => {
  it('enables indicators at their minimum scale and coarser scales', () => {
    expect(availableAtLevel('sector', 'provincia')).toBe(true)
    expect(availableAtLevel('sector', 'sector')).toBe(true)
    expect(availableAtLevel('sector', 'manzana')).toBe(false)
  })
  it('keeps quantile thresholds in data order', () => {
    expect(classifyBreaks([9, 1, 7, 3, 5, 2, 4, 6, 8, 10], 'quantile'))
      .toEqual([3, 5, 7, 9])
  })

  it('separates a natural high cluster', () => {
    const values = [...Array.from({ length: 100 }, (_, index) => index / 100),
      ...Array.from({ length: 100 }, (_, index) => 100 + index / 100)]
    const breaks = classifyBreaks(values, 'jenks')
    expect(breaks.some(value => value > 1 && value < 101)).toBe(true)
    expect(breaks).toHaveLength(4)
  })

  it('does not emit invalid thresholds for constant values', () => {
    expect(classifyBreaks([5, 5, 5, 5], 'stddev')).toEqual([5, 5, 5, 5])
    expect(classifyBreaks([], 'quantile')).toEqual([])
  })
})
