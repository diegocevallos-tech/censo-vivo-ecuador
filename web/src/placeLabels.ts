import placeCatalog from './generated/places.json'
import type { Level } from './indicatorMaps'
type DisplayLevel = Level

export function zoneLabel(key: string): string {
  return `${key.slice(0, 6)}-${key.slice(6, 9)}`
}

const places = placeCatalog.places
export const placeByKey = new Map(places.map(place => [place.key, place]))

const levelNames = {
  es: { nacion: 'Ecuador', provincia: 'Provincia', canton: 'Cantón',
    parroquia: 'Parroquia', zona: 'Zona', sector: 'Sector', manzana: 'Manzana' },
  en: { nacion: 'Ecuador', provincia: 'Province', canton: 'Canton',
    parroquia: 'Parish', zona: 'Zone', sector: 'Sector', manzana: 'Block' },
} as const

export function levelLabel(level: DisplayLevel, language: 'es' | 'en'): string {
  return levelNames[language][level]
}

export function unitKeyAtLevel(key: string, level: DisplayLevel): string {
  const lengths: Record<DisplayLevel, number> = {
    nacion: 0, provincia: 2, canton: 4, parroquia: 6, zona: 9, sector: 12, manzana: 15,
  }
  return level === 'nacion' ? 'EC' : key.slice(0, lengths[level])
}

export function parentNames(level: DisplayLevel, key: string): string[] {
  const names = [
    placeByKey.get(key.slice(0, 2))?.name,
    placeByKey.get(key.slice(0, 4))?.name,
    placeByKey.get(key.slice(0, 6))?.name,
  ]
  if (level === 'nacion') return []
  if (level === 'provincia') return ['Ecuador']
  if (level === 'canton') return names.slice(0, 1).filter((name): name is string => !!name)
  if (level === 'parroquia') return names.slice(0, 2).reverse().filter((name): name is string => !!name)
  return names.slice(0, 3).reverse().filter((name): name is string => !!name)
}

export function unitPresentation(level: DisplayLevel, key: string, language: 'es' | 'en') {
  const named = level === 'provincia' || level === 'canton' || level === 'parroquia'
  const primary = named ? placeByKey.get(key)?.name ?? key
    : level === 'nacion' ? 'Ecuador' : `${levelLabel(level, language)} ${
      level === 'zona' ? zoneLabel(key) : key}`
  const route = parentNames(level, key)
  const routeText = route.length > 2 ? `${route[0]} · ${route.slice(1).join(', ')}`
    : route.join(', ')
  return { primary, level: levelLabel(level, language), route: routeText,
    headline: routeText ? `${named ? `${levelLabel(level, language)} ` : ''}${primary} · ${routeText}`
      : primary }
}

export function breadcrumbNames(key: string, language: 'es' | 'en'): string[] {
  if (!key) return ['Ecuador']
  const path = ['Ecuador']
  for (const length of [2, 4, 6]) {
    if (key.length >= length) {
      const name = placeByKey.get(key.slice(0, length))?.name
      if (name) path.push(name)
    }
  }
  if (key.length >= 9) path.push(`${levelLabel('zona', language)} ${zoneLabel(key)}`)
  if (key.length >= 12) path.push(`${levelLabel('sector', language)} ${key.slice(0, 12)}`)
  if (key.length >= 15) path.push(`${levelLabel('manzana', language)} ${key.slice(0, 15)}`)
  return path
}
