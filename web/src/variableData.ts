/** Variable-addressable census aggregates; each HTTP range contains one variable. */
import type { Level } from './indicatorMaps'
import { unitKeyAtLevel } from './placeLabels'
import type { VariableChoice } from './variableExplorer'

interface Range { offset: number; bytes: number; rows: number }
interface Block extends Range { level: 'finest' | 'sector' | 'canton'; category_min: number }
interface ProvinceIndex {
  bytes: number
  keys: Record<Block['level'], Range>
  blocks: Record<string, Block>
}
interface VariableIndex {
  format: 'CVEV1'
  geom_version: string
  provinces: Record<string, ProvinceIndex>
}
export type Categories = Map<number, number>
export type UnitCategories = Map<string, Categories>
export interface VariableProvince {
  sourceLevel: Block['level']
  packedBytes: number
  rows: UnitCategories
  atLevel: (level: Level) => UnitCategories
}

const indexCache = new Map<string, Promise<VariableIndex>>()
const keysCache = new Map<string, Promise<Map<number, string>>>()
const variableCache = new Map<string, Promise<VariableProvince>>()
let transferredBytes = 0
export function downloadedVariableBytes(): number { return transferredBytes }

async function indexFor(base: string): Promise<VariableIndex> {
  if (!indexCache.has(base)) {
    indexCache.set(base, fetch(`${base}data/variables/v2c/index.json`).then(async response => {
      if (!response.ok) throw new Error(`Variable index: ${response.status}`)
      const buffer = await response.arrayBuffer()
      transferredBytes += buffer.byteLength
      const index = JSON.parse(new TextDecoder().decode(buffer)) as VariableIndex
      if (index.format !== 'CVEV1' || index.geom_version !== 'marco-2021') {
        throw new Error('Unknown variable data format')
      }
      return index
    }))
  }
  return indexCache.get(base)!
}

async function rangeFor(base: string, province: string, part: Range): Promise<ArrayBuffer> {
  const end = part.offset + part.bytes - 1
  const response = await fetch(`${base}data/variables/v2c/${province}.bin`, {
    headers: { Range: `bytes=${part.offset}-${end}`, 'Accept-Encoding': 'identity' },
  })
  if (response.status !== 206 || !response.headers.get('content-range')?.startsWith(
    `bytes ${part.offset}-${end}/`)) {
    throw new Error(`Variable range unavailable: ${province} ${part.offset}-${end}`)
  }
  const data = await response.arrayBuffer()
  if (data.byteLength !== part.bytes) throw new Error('Truncated variable range')
  transferredBytes += data.byteLength
  return new Response(new Blob([data]).stream().pipeThrough(new DecompressionStream('gzip')))
    .arrayBuffer()
}

export function readVarint(bytes: Uint8Array, position: { value: number }): number {
  let result = 0
  let multiplier = 1
  for (let shift = 0; shift <= 49; shift += 7) {
    if (position.value >= bytes.length) throw new Error('Truncated variable block')
    const byte = bytes[position.value++]
    result += (byte & 127) * multiplier
    if ((byte & 128) === 0) return result
    multiplier *= 128
  }
  throw new Error('Oversized variable integer')
}

export function decodeRows(buffer: ArrayBuffer, keys: Map<number, string>, block: Block): UnitCategories {
  const bytes = new Uint8Array(buffer)
  const position = { value: 0 }
  const rows: UnitCategories = new Map()
  let index = 0
  let seen = 0
  while (position.value < bytes.length) {
    index += readVarint(bytes, position)
    const category = block.category_min + readVarint(bytes, position)
    const count = readVarint(bytes, position)
    const key = keys.get(index)
    if (!key) throw new Error(`Unknown census unit index ${index}`)
    const categories = rows.get(key) ?? new Map<number, number>()
    categories.set(category, (categories.get(category) ?? 0) + count)
    rows.set(key, categories)
    seen++
  }
  if (seen !== block.rows) throw new Error(`Variable row count ${seen} != ${block.rows}`)
  return rows
}

export function rollup(rows: UnitCategories, level: Level): UnitCategories {
  if (level === 'manzana') return rows
  const output: UnitCategories = new Map()
  for (const [key, categories] of rows) {
    const parent = unitKeyAtLevel(key, level)
    const totals = output.get(parent) ?? new Map<number, number>()
    for (const [category, count] of categories) {
      totals.set(category, (totals.get(category) ?? 0) + count)
    }
    output.set(parent, totals)
  }
  return output
}

export async function variableProvince(base: string, province: string,
                                       variable: string): Promise<VariableProvince> {
  const cacheKey = `${base}:${province}:${variable}`
  if (!variableCache.has(cacheKey)) {
    variableCache.set(cacheKey, (async () => {
      const index = await indexFor(base)
      const provinceSpec = index.provinces[province]
      const block = provinceSpec?.blocks[variable]
      if (!block) throw new Error(`Variable ${variable} unavailable in province ${province}`)
      const keysKey = `${base}:${province}:${block.level}`
      if (!keysCache.has(keysKey)) {
        keysCache.set(keysKey, rangeFor(base, province, provinceSpec.keys[block.level])
          .then(buffer => new Map(JSON.parse(new TextDecoder().decode(buffer)) as [number, string][])))
      }
      const [keys, bytes] = await Promise.all([keysCache.get(keysKey)!,
        rangeFor(base, province, block)])
      const rows = decodeRows(bytes, keys, block)
      const levels = new Map<Level, UnitCategories>()
      return { sourceLevel: block.level, packedBytes: block.bytes, rows,
        atLevel: level => {
          if (!levels.has(level)) levels.set(level, rollup(rows, level))
          return levels.get(level)!
        } } satisfies VariableProvince
    })())
  }
  return variableCache.get(cacheKey)!
}

export function total(categories: Categories): number {
  let sum = 0
  for (const value of categories.values()) sum += value
  return sum
}

export function measure(categories: Categories, choice: VariableChoice, areaKm2?: number): number | null {
  if (choice.variable.type === 'numeric') {
    let numerator = 0
    let denominator = 0
    for (const item of choice.variable.categories) {
      const value = item.midpoint ?? Number(item.code)
      if (!Number.isFinite(value) || value >= 888) continue
      const count = categories.get(item.id) ?? 0
      numerator += value * count
      denominator += count
    }
    return denominator ? numerator / denominator : null
  }
  if (!choice.category) return null
  const count = categories.get(choice.category.id) ?? 0
  if (choice.mode === 'count') return count
  if (choice.mode === 'density') return areaKm2 && areaKm2 > 0 ? count / areaKm2 : null
  const universe = total(categories)
  return universe ? 100 * count / universe : null
}
