/** Browser QA for six optional municipal reference layers and Iñaquito. */
import { chromium } from '@playwright/test'
import * as turf from '@turf/turf'
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

const root = process.env.CENSO_SITE_URL ?? 'http://127.0.0.1:5173/censo-vivo-ecuador/'
const output = resolve('../docs/capturas')
mkdirSync(output, { recursive: true })
const boundaries = JSON.parse(readFileSync(resolve('public/data/municipal-urban/v1/boundaries.geojson'), 'utf8'))
const selected = new Map()
for (const feature of boundaries.features) {
  if (!selected.has(feature.properties.city)) selected.set(feature.properties.city, feature)
  if (feature.properties.urban_id === 'municipal:quito:170112') selected.set('Quito', feature)
}
if (selected.size !== 6) throw new Error(`Expected six municipal cities, got ${selected.size}`)
const browser = await chromium.launch({ headless: true })
const results = []
try {
  for (const [city, feature] of selected) {
    const [longitude, latitude] = turf.pointOnFeature(feature).geometry.coordinates
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
    const errors = []
    page.on('pageerror', error => errors.push(error.message))
    page.on('console', message => {
      if (message.type() === 'error') errors.push(message.text())
    })
    await page.goto(`${root}#map=${longitude},${latitude},10.5`, { waitUntil: 'domcontentloaded' })
    await page.locator('#toggle-urban').click()
    await page.locator('#urban-legend').waitFor({ state: 'visible', timeout: 15000 })
    await page.waitForTimeout(1200)
    await page.mouse.move(720, 450)
    await page.locator('.municipal-popup .unit-title').waitFor({ timeout: 12000 })
    const name = await page.locator('.municipal-popup .unit-title').innerText()
    const expected = feature.properties.name
    const note = await page.locator('.municipal-popup .unit-note').innerText()
    if (name !== expected || !note.includes('Límite no censal')) {
      throw new Error(`${city}: expected ${expected}, got ${name} / ${note}`)
    }
    if (city === 'Quito') {
      const metric = await page.locator('.municipal-popup .unit-value').innerText()
      if (name !== 'Iñaquito' || !metric.includes('149,5')) {
        throw new Error(`Iñaquito ageing index: ${name} / ${metric}`)
      }
      await page.screenshot({ path: resolve(output, 'parroquia-urbana-inaquito.png') })
    }
    await page.mouse.click(720, 450)
    const panelName = await page.locator('#analysis-content h3').innerText()
    const panelNote = await page.locator('#analysis-content .analysis-place-note').innerText()
    if (panelName !== expected || !panelNote.includes('No es una unidad censal') || errors.length) {
      throw new Error(JSON.stringify({ city, panelName, panelNote, errors }))
    }
    results.push({ city, name, panelName, errors })
    await page.close()
  }
  writeFileSync(resolve(output, 'parroquias-urbanas-e2e.json'), JSON.stringify(results, null, 2))
  console.log(JSON.stringify({ passed: results.length, results }))
} finally {
  await browser.close()
}
