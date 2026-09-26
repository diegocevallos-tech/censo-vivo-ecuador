import { describe, expect, it } from 'vitest'
import { decodeRows, measure, rollup, total } from './variableData'
import type { VariableChoice } from './variableExplorer'

describe('variable-addressable exact aggregates', () => {
  it('decodes unsigned deltas and rolls whole blocks to their sector', () => {
    // Three cells: block 001, categories 0 and 1; block 002, category 0.
    const bytes = new Uint8Array([0, 0, 3, 0, 1, 4, 1, 0, 5])
    const keys = new Map([[0, '170150001001001'], [1, '170150001001002']])
    const cells = decodeRows(bytes.buffer, keys,
      { level: 'finest', offset: 0, bytes: 9, rows: 3, category_min: 0 })
    expect(total(cells.get('170150001001001')!)).toBe(7)
    const sectors = rollup(cells, 'sector')
    expect([...sectors.get('170150001001')!]).toEqual([[0, 8], [1, 4]])
    expect(total(sectors.get('170150001001')!)).toBe(12)
  })

  it('rejects a missing official unit key and a truncated row', () => {
    expect(() => decodeRows(new Uint8Array([1, 0, 5]).buffer, new Map(),
      { level: 'finest', offset: 0, bytes: 3, rows: 1, category_min: 0 }))
      .toThrow('Unknown census unit')
    expect(() => decodeRows(new Uint8Array([0, 0]).buffer, new Map([[0, '17']]),
      { level: 'finest', offset: 0, bytes: 2, rows: 1, category_min: 0 }))
      .toThrow('Truncated variable block')
  })

  it('uses the valid category universe for percentages and numeric means', () => {
    const variable = { id: 'V03', type: 'categorical', categories: [
      { id: 0, code: '1', midpoint: undefined }, { id: 1, code: '2', midpoint: undefined },
    ] } as unknown as VariableChoice['variable']
    const choice: VariableChoice = { variable, category: variable.categories[0], mode: 'percent' }
    const cells = new Map([[0, 3], [1, 7]])
    expect(measure(cells, choice)).toBe(30)
    choice.mode = 'count'
    expect(measure(cells, choice)).toBe(3)
    choice.mode = 'density'
    expect(measure(cells, choice, 2)).toBe(1.5)
    const numeric = { ...variable, type: 'numeric', categories: [
      { id: 0, code: '1' }, { id: 1, code: '3' }, { id: 2, code: '888' },
    ] } as VariableChoice['variable']
    expect(measure(new Map([[0, 2], [1, 2], [2, 10]]),
      { variable: numeric, category: null, mode: 'mean' })).toBe(2)
  })
})
