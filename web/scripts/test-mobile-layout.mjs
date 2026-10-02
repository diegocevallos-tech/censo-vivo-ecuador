import assert from 'node:assert/strict'
import { mkdir } from 'node:fs/promises'
import { join } from 'node:path'
import { chromium } from '@playwright/test'

const origin = process.env.TEST_URL ?? 'http://127.0.0.1:5173/censo-vivo-ecuador/'
const captures = join(process.cwd(), '..', 'docs', 'capturas')
await mkdir(captures, { recursive: true })
const browser = await chromium.launch({ headless: true })
try {
  for (const viewport of [{ width: 390, height: 844 }, { width: 360, height: 640 }]) {
    const page = await browser.newPage({ viewport, deviceScaleFactor: 1, hasTouch: true })
    const errors = []
    page.on('pageerror', error => errors.push(error.message))
    await page.goto(origin, { waitUntil: 'domcontentloaded' })
    await page.locator('#map canvas').waitFor()
    await page.waitForTimeout(1800)

    const mapView = page.getByRole('button', { name: 'Mapa' })
    const exploreView = page.getByRole('button', { name: 'Explorar' })
    const analysisView = page.getByRole('button', { name: 'Análisis' })
    assert.equal(await mapView.getAttribute('aria-pressed'), 'true')
    assert.equal(await page.locator('.data-card').isVisible(), false)
    assert.equal(await page.locator('.explorer-panel').isVisible(), false)
    const status = await page.locator('#status').boundingBox()
    const nav = await page.locator('.mobile-panel-nav').boundingBox()
    assert.ok(status && nav && nav.y - (status.y + status.height) >= 200,
      `Map opening too small at ${viewport.width}×${viewport.height}`)
    if (viewport.width === 390) {
      await page.screenshot({ path: join(captures, 'mobile-mapa.png') })
      await page.mouse.click(195, 410)
      await page.locator('.mobile-panel-nav .has-selection').waitFor()
      assert.equal(await mapView.getAttribute('aria-pressed'), 'true')
      assert.equal(await page.locator('.data-card').isVisible(), false)
      await page.screenshot({ path: join(captures, 'mobile-seleccion.png') })
    }

    await exploreView.click()
    assert.equal(await page.locator('.explorer-panel').isVisible(), true)
    assert.equal(await page.locator('.data-card').isVisible(), false)
    const explorer = await page.locator('.explorer-panel').boundingBox()
    assert.ok(explorer && status && explorer.y - (status.y + status.height) >= 90,
      'Explorer covers the entire map')
    if (viewport.width === 390) {
      await page.screenshot({ path: join(captures, 'mobile-explorar.png') })
    }

    await analysisView.click()
    assert.equal(await page.locator('.data-card').isVisible(), true)
    assert.equal(await page.locator('.explorer-panel').isVisible(), false)
    const analysis = await page.locator('.data-card').boundingBox()
    assert.ok(analysis && status && analysis.y - (status.y + status.height) >= 90,
      'Analysis covers the entire map')
    if (viewport.width === 390) {
      await page.screenshot({ path: join(captures, 'mobile-analisis.png') })
    }

    await page.getByRole('button', { name: 'Lazo' }).click()
    assert.equal(await mapView.getAttribute('aria-pressed'), 'true')
    assert.equal(await page.locator('.data-card').isVisible(), false)
    assert.equal(await page.getByRole('button', { name: 'Lazo' }).getAttribute('aria-pressed'), 'true')
    if (viewport.width === 390) {
      await page.getByRole('button', { name: 'Cambiar idioma' }).click()
      assert.equal(await page.getByRole('button', { name: 'Map' }).isVisible(), true)
      assert.equal(await page.getByRole('button', { name: 'Explore' }).isVisible(), true)
      assert.equal(await page.getByRole('button', { name: /Analysis/ }).isVisible(), true)
    }
    assert.deepEqual(errors, [], `JavaScript errors at ${viewport.width}×${viewport.height}`)
    await page.close()
  }

  const desktop = await browser.newPage({ viewport: { width: 1280, height: 800 } })
  await desktop.goto(origin, { waitUntil: 'domcontentloaded' })
  assert.equal(await desktop.locator('.mobile-panel-nav').isVisible(), false)
  assert.equal(await desktop.locator('.data-card').isVisible(), true)
  assert.equal(await desktop.locator('.explorer-panel').isVisible(), true)
  await desktop.close()
  console.log('Mobile map, explorer, analysis, toolbar and desktop layout: OK')
} finally {
  await browser.close()
}
