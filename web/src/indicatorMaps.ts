export type Level = 'nacion' | 'provincia' | 'canton' | 'parroquia' | 'sector' | 'manzana'
export type BreakMode = 'quantile' | 'jenks' | 'stddev'

interface IndexSchema {
  format: 'CVEI1'
  geom_version: string
  key_bytes: number
  stride: number
  indicators: string[]
  files: Record<string, { rows: number; bytes: number }>
}

export interface IndicatorCell { value: number | null; status: 0 | 1 | 2 | 3 }
export interface IndicatorFile {
  keys: string[]
  cell: (key: string, indicator: string) => IndicatorCell | null
  eligibleValues: (indicator: string) => number[]
}

const cache = new Map<string, Promise<IndicatorFile>>()
let schemaPromise: Promise<IndexSchema> | null = null

export function indicatorSchema(base: string): Promise<IndexSchema> {
  schemaPromise ??= fetch(`${base}data/indicator-maps/v2a/schema.json`).then(async response => {
    if (!response.ok) throw new Error(`Indicator index schema: ${response.status}`)
    const schema = await response.json() as IndexSchema
    if (schema.format !== 'CVEI1' || schema.geom_version !== 'marco-2021') {
      throw new Error('Unknown indicator index schema')
    }
    return schema
  })
  return schemaPromise
}

function decode(data: ArrayBuffer, schema: IndexSchema): IndicatorFile {
  const view = new DataView(data)
  const magic = new TextDecoder().decode(new Uint8Array(data, 0, 5))
  const rows = view.getUint32(5, true)
  const width = view.getUint16(9, true)
  if (magic !== 'CVEI1' || width !== schema.indicators.length ||
      data.byteLength !== 11 + rows * schema.stride) {
    throw new Error('Corrupt indicator index')
  }
  const keys: string[] = []
  const positions = new Map<string, number>()
  const decoder = new TextDecoder()
  for (let row = 0; row < rows; row++) {
    const start = 11 + row * schema.stride
    const raw = new Uint8Array(data, start, schema.key_bytes)
    const end = raw.indexOf(0)
    const key = decoder.decode(end < 0 ? raw : raw.subarray(0, end))
    keys.push(key)
    positions.set(key, row)
  }
  const columns = new Map(schema.indicators.map((id, index) => [id, index]))
  function at(row: number, column: number): IndicatorCell {
    const offset = 11 + row * schema.stride + schema.key_bytes + column * 5
    const value = view.getFloat32(offset, true)
    return { value: Number.isFinite(value) ? value : null,
      status: view.getUint8(offset + 4) as IndicatorCell['status'] }
  }
  return {
    keys,
    cell(key, indicator) {
      const row = positions.get(key)
      const column = columns.get(indicator)
      return row == null || column == null ? null : at(row, column)
    },
    eligibleValues(indicator) {
      const column = columns.get(indicator)
      if (column == null) return []
      const values = []
      for (let row = 0; row < rows; row++) {
        const cell = at(row, column)
        if (cell.status === 0 && cell.value != null) values.push(cell.value)
      }
      return values
    },
  }
}

export async function indicatorFile(base: string, level: Level, province?: string): Promise<IndicatorFile> {
  const path = `${level === 'manzana' ? 'finest' : level}/${province ?? 'data'}.bin`
  if (!cache.has(path)) {
    cache.set(path, (async () => {
      const schema = await indicatorSchema(base)
      const expected = schema.files[path]
      if (!expected) throw new Error(`Indicator index absent: ${path}`)
      const response = await fetch(`${base}data/indicator-maps/v2a/${path}`)
      if (!response.ok) throw new Error(`Indicator index ${path}: ${response.status}`)
      const data = await response.arrayBuffer()
      if (data.byteLength !== expected.bytes) throw new Error(`Truncated indicator index: ${path}`)
      return decode(data, schema)
    })())
  }
  return cache.get(path)!
}

function jenksBreaks(sorted: number[], classes: number): number[] {
  // Fisher-Jenks exact on a deterministic, evenly spaced sample to bound UI cost.
  const sample = sorted.length <= 1024 ? sorted : Array.from({ length: 1024 }, (_, index) =>
    sorted[Math.round(index * (sorted.length - 1) / 1023)])
  const n = sample.length
  if (n < classes) return quantileBreaks(sorted)
  const prefix = [0]
  const squares = [0]
  for (const value of sample) {
    prefix.push(prefix.at(-1)! + value)
    squares.push(squares.at(-1)! + value * value)
  }
  const variance = (start: number, end: number): number => {
    const count = end - start
    const total = prefix[end] - prefix[start]
    return squares[end] - squares[start] - total * total / count
  }
  const costs = Array.from({ length: classes + 1 }, () => new Float64Array(n + 1).fill(Infinity))
  const split = Array.from({ length: classes + 1 }, () => new Uint16Array(n + 1))
  costs[0][0] = 0
  for (let group = 1; group <= classes; group++) {
    for (let end = group; end <= n; end++) {
      for (let start = group - 1; start < end; start++) {
        const cost = costs[group - 1][start] + variance(start, end)
        if (cost < costs[group][end]) {
          costs[group][end] = cost
          split[group][end] = start
        }
      }
    }
  }
  const breaks = []
  let end = n
  for (let group = classes; group > 1; group--) {
    const start = split[group][end]
    breaks.unshift(sample[start])
    end = start
  }
  return breaks
}

function quantileBreaks(sorted: number[]): number[] {
  return [1, 2, 3, 4].map(index => sorted[Math.min(sorted.length - 1,
    Math.floor(index * sorted.length / 5))])
}

export function classifyBreaks(values: number[], mode: BreakMode): number[] {
  const sorted = values.filter(Number.isFinite).sort((a, b) => a - b)
  if (!sorted.length) return []
  if (mode === 'quantile') return quantileBreaks(sorted)
  if (mode === 'jenks') return jenksBreaks(sorted, 5)
  const mean = sorted.reduce((total, value) => total + value, 0) / sorted.length
  const deviation = Math.sqrt(sorted.reduce((total, value) => total + (value - mean) ** 2, 0) / sorted.length)
  return [-1.5, -0.5, 0.5, 1.5].map(offset => mean + offset * deviation)
}
