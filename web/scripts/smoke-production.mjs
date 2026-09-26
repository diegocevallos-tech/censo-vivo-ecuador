/** End-to-end smoke test of the deployed, public Phase 2 viewer. */
import { chromium } from '@playwright/test'
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { resolve } from 'node:path'

const url = process.env.CENSO_SITE_URL ?? 'https://diegocevallos-tech.github.io/censo-vivo-ecuador/'
const output = resolve('../docs/capturas')
mkdirSync(output, { recursive: true })
const definitions = JSON.parse(readFileSync(resolve('src/generated/indicators.json'), 'utf8')).indicators
const browser = await chromium.launch({ headless: true })
const results = { url, captured_at_utc: new Date().toISOString(), errors: [], cases: {} }
const errors = results.errors

async function openPage(width, height, hash = '') {
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 })
  page.on('pageerror', error => errors.push(`page: ${error.message}`))
  page.on('console', message => {
    if (message.type() === 'error') errors.push(`console: ${message.text()}`)
  })
  await page.goto(url + hash, { waitUntil: 'domcontentloaded' })
  await page.locator('#level').waitFor({ state: 'visible' })
  await page.waitForTimeout(3000)
  return page
}

async function circle(city, camera, x = 800, y = 440) {
  const page = await openPage(1440, 900, `#map=${camera},14.30`)
  await page.waitForTimeout(2500)
  const level = await page.locator('#level').innerText()
  await page.locator('[data-mode="circle"]').click()
  await page.mouse.move(x, y)
  await page.mouse.down()
  await page.mouse.move(x + 55, y + 35, { steps: 16 })
  await page.mouse.up()
  await page.locator('#analysis-content h3').waitFor({ timeout: 12000 })
  await page.waitForTimeout(300)
  const result = {
    level, status: await page.locator('#status').innerText(),
    quality: await page.locator('#analysis-content .quality').innerText(),
    preview_p95_ms: Number(await page.locator('#selection-preview').getAttribute('data-preview-p95-ms')),
  }
  await page.screenshot({ path: resolve(output, `circulo-${city}.png`) })
  await page.close()
  return result
}

try {
  const desktop = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 })
  desktop.on('pageerror', error => errors.push(`desktop: ${error.message}`))
  desktop.on('console', message => {
    if (message.type() === 'error') errors.push(`desktop console: ${message.text()}`)
  })
  const cdp = await desktop.context().newCDPSession(desktop)
  await cdp.send('Network.enable')
  let firstLoadBytes = 0
  cdp.on('Network.loadingFinished', event => { firstLoadBytes += event.encodedDataLength })
  await desktop.goto(url, { waitUntil: 'domcontentloaded' })
  await desktop.waitForTimeout(5000)
  results.cases.desktop = { level: await desktop.locator('#level').innerText(),
    first_load_bytes: firstLoadBytes }
  await desktop.screenshot({ path: resolve(output, 'inicio-escritorio.png') })
  await desktop.close()

  const mobile = await openPage(390, 844)
  results.cases.mobile = { level: await mobile.locator('#level').innerText(),
    toolbar_scrollable: await mobile.locator('.toolbar').evaluate(node => node.scrollWidth > node.clientWidth) }
  await mobile.screenshot({ path: resolve(output, 'inicio-movil.png') })
  await mobile.close()

  const zoom = await openPage(1440, 900, '#map=-78.4900,-0.1800,2.30')
  const levels = []
  for (let step = 0; step <= 12; step++) {
    const level = await zoom.locator('#level').innerText()
    if (levels.at(-1) !== level) levels.push(level)
    if (step < 12) {
      await zoom.locator('.maplibregl-ctrl-zoom-in').click()
      await zoom.waitForTimeout(800)
    }
  }
  results.cases.zoom = { levels }
  await zoom.screenshot({ path: resolve(output, 'zoom-manzana.png') })
  await zoom.close()

  results.cases.circle_quito = await circle('quito', '-78.4900,-0.1800')
  results.cases.circle_guayaquil = await circle('guayaquil', '-79.9000,-2.1700')
  results.cases.circle_rural = await circle('rural', '-78.1612,-2.3000', 720, 450)

  const tools = await openPage(1440, 900, '#map=-78.4900,-0.1800,14.30')
  await tools.waitForTimeout(2500)
  await tools.locator('[data-mode="lasso"]').click()
  await tools.mouse.move(800, 390)
  await tools.mouse.down()
  await tools.mouse.move(950, 390, { steps: 6 })
  await tools.mouse.move(950, 540, { steps: 6 })
  await tools.mouse.move(800, 540, { steps: 6 })
  await tools.mouse.up()
  await tools.locator('#analysis-content h3').waitFor({ timeout: 12000 })
  results.cases.lasso = { heading: await tools.locator('#analysis-content h3').innerText() }
  await tools.screenshot({ path: resolve(output, 'lazo.png') })
  await tools.locator('[data-mode="multi"]').click()
  await tools.mouse.click(880, 450)
  await tools.waitForTimeout(1000)
  results.cases.multi = { heading: await tools.locator('#analysis-content h3').innerText() }
  await tools.screenshot({ path: resolve(output, 'multiseleccion.png') })
  await tools.close()

  const thematic = await openPage(1440, 900, '#map=-78.4900,-0.1800,7.30')
  const hierarchy = ['manzana', 'sector', 'parroquia', 'canton', 'provincia', 'nacion']
  const ids = definitions.filter(item => hierarchy.indexOf(item.min_level) <= hierarchy.indexOf('canton'))
    .slice(0, 30).map(item => item.id)
  for (const id of ids) {
    await thematic.locator('#indicator-select').selectOption(id)
    await thematic.waitForTimeout(230)
  }
  await thematic.waitForTimeout(1400)
  results.cases.indicators = { tested: ids.length, ids, active: await thematic.locator('#indicator-select').inputValue(),
    status: await thematic.locator('#status').innerText() }
  await thematic.locator('#indicator-select').selectOption('aging_index')
  await thematic.waitForTimeout(400)
  const shared = thematic.url()
  const restored = await openPage(1440, 900, new URL(shared).hash)
  results.cases.shared_url = { url: shared,
    indicator_restored: await restored.locator('#indicator-select').inputValue(),
    level_restored: await restored.locator('#level').innerText() }
  await restored.screenshot({ path: resolve(output, 'url-restaurada.png') })
  await restored.close()
  await thematic.close()
} finally {
  await browser.close()
  writeFileSync(resolve(output, 'smoke-results.json'), JSON.stringify(results, null, 2) + '\n')
}
console.log(JSON.stringify(results, null, 2))
if (errors.length) process.exitCode = 1
