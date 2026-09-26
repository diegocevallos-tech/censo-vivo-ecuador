/** Read exact official-unit counts from province chunks without person rows. */
export interface ChunkColumn { name: string; type: 'uint8' | 'uint16' | 'uint32' | 'uint64'; offset: number; max: number }
interface ChunkSchema {
  format: 'CVEB1'
  geom_version: string
  key_bytes: number
  chunks: Record<string, { rows: number; columns: ChunkColumn[] }>
}

export interface CountChunk {
  keys: string[]
  has: (key: string) => boolean
  population: (key: string) => number
  counts: (key: string) => Record<string, number> | null
  keysWithPrefix: (prefix: string) => string[]
}

let schemaPromise: Promise<ChunkSchema> | null = null
const cache = new Map<string, Promise<CountChunk>>()

function schema(base: string): Promise<ChunkSchema> {
  schemaPromise ??= fetch(`${base}data/chunks/v1b/schema.json`).then(async response => {
    if (!response.ok) throw new Error(`Count schema: ${response.status}`)
    const value = await response.json() as ChunkSchema
    if (value.format !== 'CVEB1' || value.geom_version !== 'marco-2021') {
      throw new Error('Unknown count chunk format')
    }
    return value
  })
  return schemaPromise
}

export async function countChunk(base: string, province: string,
                                 level: 'finest' | 'sector'): Promise<CountChunk> {
  const path = `${level}/${province}.bin`
  if (!cache.has(path)) {
    cache.set(path, (async () => {
      const index = await schema(base)
      const spec = index.chunks[path]
      if (!spec) throw new Error(`Unknown count chunk ${path}`)
      const response = await fetch(`${base}data/chunks/v1b/${path}`)
      if (!response.ok) throw new Error(`Count chunk ${path}: ${response.status}`)
      const buffer = await response.arrayBuffer()
      const view = new DataView(buffer)
      const magic = new TextDecoder().decode(new Uint8Array(buffer, 0, 5))
      const rows = view.getUint32(5, true)
      if (magic !== 'CVEB1' || rows !== spec.rows) throw new Error(`Truncated count chunk ${path}`)
      const decoder = new TextDecoder()
      const keys: string[] = []
      const positions = new Map<string, number>()
      for (let row = 0; row < rows; row++) {
        const raw = new Uint8Array(buffer, 9 + row * index.key_bytes, index.key_bytes)
        const end = raw.indexOf(0)
        const key = decoder.decode(end < 0 ? raw : raw.subarray(0, end))
        keys.push(key)
        positions.set(key, row)
      }
      const columns = new Map(spec.columns.map(column => [column.name, column]))
      const widths = { uint8: 1, uint16: 2, uint32: 4, uint64: 8 }
      for (const column of spec.columns) {
        if (column.offset + rows * widths[column.type] > buffer.byteLength) {
          throw new Error(`Count column beyond chunk ${path}: ${column.name}`)
        }
      }
      function value(row: number, column: ChunkColumn): number {
        const offset = column.offset + row * widths[column.type]
        if (column.type === 'uint8') return view.getUint8(offset)
        if (column.type === 'uint16') return view.getUint16(offset, true)
        if (column.type === 'uint32') return view.getUint32(offset, true)
        const integer = view.getBigUint64(offset, true)
        if (integer > BigInt(Number.MAX_SAFE_INTEGER)) throw new Error('Count exceeds JS safe integer')
        return Number(integer)
      }
      const population = columns.get('population')
      if (!population) throw new Error(`Population absent in ${path}`)
      return {
        keys,
        has: key => positions.has(key),
        population: key => {
          const row = positions.get(key)
          return row == null ? 0 : value(row, population)
        },
        counts: key => {
          const row = positions.get(key)
          if (row == null) return null
          const counts: Record<string, number> = {}
          for (const column of spec.columns) {
            if (column.name === 'unit_index') continue
            const count = value(row, column)
            counts[`core:${column.name}`] = count
            counts[`cross:${column.name}`] = count
          }
          counts.population = value(row, population)
          return counts
        },
        keysWithPrefix: prefix => keys.filter(key => key.startsWith(prefix)),
      } satisfies CountChunk
    })())
  }
  return cache.get(path)!
}
