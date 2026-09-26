/** Browser regression: named hover, parent route, indicator and analysis. */
import { chromium } from '@playwright/test'
import { mkdirSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

const root = process.env.CENSO_SITE_URL ?? 'http://127.0.0.1:5173/censo-vivo-ecuador/'
const output = resolve('../docs/capturas')
mkdirSync(output, { recursive: true })
const cases = [
  { level: 'provincia', key: '17', camera: '-78.49534,-0.17422,5', title: 'Pichincha',
    route: 'Provincia · Ecuador' },
  { level: 'canton', key: '1701', camera: '-78.50754,-0.15662,7', title: 'Quito',
    route: 'Cantón · Pichincha' },
  { level: 'parroquia', key: '170155', camera: '-78.41675,-0.08285,9', title: 'Calderón',
    route: 'Parroquia · Quito, Pichincha' },
  { level: 'sector', key: '170155025002', camera: '-78.41362,-0.09485,11',
    title: 'Sector 170155025002', route: 'Sector · Calderón · Quito, Pichincha' },
]
const browser = await chromium.launch({ headless: true })
const results = []
const errors = []
try {
  for (const item of cases) {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
    page.on('pageerror', error => errors.push(`${item.level}: ${error.message}`))
    await page.goto(`${root}#map=${item.camera}`, { waitUntil: 'domcontentloaded' })
    await page.locator('#level').waitFor({ state: 'visible' })
    await page.waitForTimeout(2200)
    let found = false
    for (const [dx, dy] of [[0, 0], [10, 0], [-10, 0], [0, 10], [0, -10]]) {
      await page.mouse.move(720 + dx, 450 + dy)
      if (await page.locator('.unit-popup .unit-title').count()) {
        const title = await page.locator('.unit-popup .unit-title').innerText()
        if (title === item.title) { found = true; break }
      }
    }
    if (!found) throw new Error(`${item.level} ${item.key}: title absent; got ${
      await page.locator('.unit-popup .unit-title').allInnerTexts()}`)
    const context = await page.locator('.unit-popup .unit-context').innerText()
    const value = await page.locator('.unit-popup .unit-value').innerText()
    const population = await page.locator('.unit-popup .unit-population').innerText()
    if (context !== item.route || !value.includes('Densidad de población') ||
        !population.includes('Población:')) {
      throw new Error(`${item.level}: ${context} / ${value} / ${population}`)
    }
    await page.screenshot({ path: resolve(output, `tooltip-${item.level}.png`) })
    await page.mouse.click(720, 450)
    if (item.level === 'parroquia') {
      await page.locator('#analysis-content h3').waitFor({ timeout: 15000 })
      const analysis = await page.locator('#analysis-content h3').innerText()
      const analysisRoute = await page.locator('.analysis-place-context').innerText()
      const analysisMetric = await page.locator('.analysis-place-metric').innerText()
      const breadcrumb = await page.locator('#breadcrumb').innerText()
      if (analysis !== 'Calderón' || analysisRoute !== 'Parroquia · Quito, Pichincha' ||
          !analysisMetric.includes('Densidad de población:') ||
          !breadcrumb.includes('Pichincha › Quito › Calderón')) {
        throw new Error(`Analysis route: ${analysis} / ${analysisRoute} / ${analysisMetric} / ${breadcrumb}`)
      }
      await page.screenshot({ path: resolve(output, 'tooltip-analisis-parroquia.png') })
    }
    results.push({ level: item.level, key: item.key, title: item.title, context,
      value, population })
    await page.close()
  }
  const sector = cases.at(-1)
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  await page.goto(`${root}#indicator=crude_death_report_rate&map=${sector.camera}`,
    { waitUntil: 'domcontentloaded' })
  await page.waitForTimeout(2500)
  await page.mouse.move(720, 450)
  await page.locator('.unit-popup .unit-note').filter({ hasText: 'Dato de cantón' })
    .waitFor({ timeout: 10000 })
  results.push({ level: 'sector-min-level', note: await page.locator('.unit-popup .unit-note').innerText() })
  await page.close()
  if (errors.length) throw new Error(`Browser errors: ${errors.join('; ')}`)
  writeFileSync(resolve(output, 'tooltip-results.json'), JSON.stringify({ root, results, errors }, null, 2))
  console.log(JSON.stringify({ passed: results.length, errors }))
} finally {
  await browser.close()
}
