import { describe, expect, it } from 'vitest'
import places from './generated/places.json'
import { breadcrumbNames, unitPresentation } from './placeLabels'

describe('official geographic names', () => {
  it('covers every published administrative unit without corrupt or uppercase names', () => {
    const expected = { provincia: 24, canton: 221, parroquia: 1042 }
    for (const [level, count] of Object.entries(expected)) {
      const rows = places.places.filter(place => place.level === level)
      expect(rows).toHaveLength(count)
      const missing = rows.filter(place => !place.name || place.name === place.key)
      expect(missing.map(place => place.key)).toEqual([])
      for (const place of rows) {
        expect(place.name).not.toMatch(/[�ÃÂ]/)
        expect(place.name).not.toBe(place.name.toUpperCase())
      }
    }
  })

  it('formats the requested names and full named route', () => {
    expect(unitPresentation('parroquia', '170155', 'es')).toMatchObject({
      primary: 'Calderón', route: 'Quito, Pichincha',
      headline: 'Parroquia Calderón · Quito, Pichincha',
    })
    expect(unitPresentation('sector', '170155025002', 'es')).toMatchObject({
      primary: 'Sector 170155025002', route: 'Calderón · Quito, Pichincha',
    })
    expect(unitPresentation('zona', '170155025', 'es')).toMatchObject({
      primary: 'Zona 170155-025', route: 'Calderón · Quito, Pichincha',
      headline: 'Zona 170155-025 · Calderón · Quito, Pichincha',
    })
    expect(unitPresentation('zona', '170150257', 'es')).toMatchObject({
      primary: 'Zona 170150-257', route: 'Quito, Pichincha',
      headline: 'Zona 170150-257 · Quito, Pichincha',
    })
    expect(breadcrumbNames('170155025002', 'es')).toEqual([
      'Ecuador', 'Pichincha', 'Quito', 'Calderón', 'Zona 170155-025',
      'Sector 170155025002',
    ])
  })
})
