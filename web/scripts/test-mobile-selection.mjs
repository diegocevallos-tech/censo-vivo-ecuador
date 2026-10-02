import assert from 'node:assert/strict'
import { mkdir } from 'node:fs/promises'
import { join } from 'node:path'
import { chromium } from '@playwright/test'

const origin = process.env.TEST_URL ?? 'http://127.0.0.1:5173/censo-vivo-ecuador/'
const captures = join(process.cwd(), '..', 'docs', 'capturas')
await mkdir(captures, { recursive: true })
const browser = await chromium.launch({ headless: true })
try {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 },
    deviceScaleFactor: 1, hasTouch: true, isMobile: true })
  const errors = []
  page.on('pageerror', error => errors.push(error.message))
  await page.goto(origin, { waitUntil: 'domcontentloaded' })
  await page.locator('#map canvas').waitFor()
  await page.waitForTimeout(1800)
  const initialLevel = await page.locator('#level').textContent()

  // Inspect a unit, then tap it again to deselect without hunting for Clear.
  await page.touchscreen.tap(195, 410)
  await page.locator('.mobile-panel-nav .has-selection').waitFor()
  await page.touchscreen.tap(195, 410)
  await page.locator('.mobile-panel-nav .has-selection').waitFor({ state: 'hidden' })
  await page.waitForTimeout(400)
  assert.equal(await page.locator('#level').textContent(), initialLevel,
    'tapping twice to deselect must not zoom the map')

  // A tap places a usable circle; the slider changes its radius and Clear exits drawing.
  await page.getByRole('button', { name: 'Círculo' }).click()
  assert.equal(await page.locator('#selection-guide').isVisible(), true)
  await page.touchscreen.tap(195, 410)
  await page.locator('.selection-circle').waitFor({ state: 'visible' })
  await page.locator('#circle-adjust').waitFor({ state: 'visible' })
  const originalCircle = await page.locator('.selection-circle').boundingBox()
  assert.ok(originalCircle?.width > 100)
  const radiusHandle = await page.locator('.selection-radius').boundingBox()
  assert.ok(radiusHandle?.width >= 44 && radiusHandle?.height >= 44)
  const cdp = await page.context().newCDPSession(page)
  const handleStart = { x: Math.round(radiusHandle.x + radiusHandle.width / 2),
    y: Math.round(radiusHandle.y + radiusHandle.height / 2) }
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [handleStart] })
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [
    { x: handleStart.x + 32, y: handleStart.y }] })
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] })
  const draggedCircle = await page.locator('.selection-circle').boundingBox()
  assert.ok(draggedCircle.width > originalCircle.width)
  await page.locator('#circle-radius').focus()
  await page.locator('#circle-radius').press('End')
  const largerCircle = await page.locator('.selection-circle').boundingBox()
  assert.ok(largerCircle.width > originalCircle.width)
  await page.locator('.mobile-panel-nav .has-selection').waitFor()
  await page.screenshot({ path: join(captures, 'mobile-circulo-control.png') })
  await page.getByRole('button', { name: 'Borrar selección' }).click()
  assert.equal(await page.locator('#selection-guide').isVisible(), false)
  assert.equal(await page.locator('.selection-circle').isVisible(), false)
  assert.equal(await page.getByRole('button', { name: 'Inspeccionar' }).getAttribute('aria-pressed'), 'true')
  assert.equal(await page.locator('.mobile-panel-nav .has-selection').count(), 0)

  // Lasso uses a finger path and closes when the finger is lifted.
  await page.getByRole('button', { name: 'Lazo' }).click()
  const path = [{ x: 120, y: 315 }, { x: 265, y: 315 }, { x: 265, y: 490 },
    { x: 120, y: 490 }, { x: 120, y: 315 }]
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [path[0]] })
  for (const point of path.slice(1)) {
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [point] })
  }
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] })
  await page.locator('.mobile-panel-nav .has-selection').waitFor()
  await page.screenshot({ path: join(captures, 'mobile-lazo-control.png') })
  await page.getByRole('button', { name: 'Limpiar' }).click()
  assert.equal(await page.getByRole('button', { name: 'Inspeccionar' }).getAttribute('aria-pressed'), 'true')

  // Multi keeps the map open and lets a second tap remove the same unit.
  await page.getByRole('button', { name: 'Multi' }).click()
  await page.touchscreen.tap(195, 410)
  await page.locator('.mobile-panel-nav .has-selection').waitFor()
  await page.screenshot({ path: join(captures, 'mobile-multi-control.png') })
  await page.waitForTimeout(400)
  await page.touchscreen.tap(300, 430)
  await page.locator('#selection-guide-preview').filter({ hasText: '2 unidades' }).waitFor()
  await page.touchscreen.tap(300, 430)
  await page.locator('#selection-guide-preview').filter({ hasText: '1 unidad' }).waitFor()
  await page.touchscreen.tap(195, 410)
  await page.locator('.mobile-panel-nav .has-selection').waitFor({ state: 'hidden' })
  await page.getByRole('button', { name: 'Hecho' }).click()
  assert.equal(await page.getByRole('button', { name: 'Inspeccionar' }).getAttribute('aria-pressed'), 'true')
  assert.equal(await page.locator('#selection-guide').isVisible(), false)
  assert.deepEqual(errors, [])
  await page.close()
  const city = await browser.newPage({ viewport: { width: 360, height: 640 },
    deviceScaleFactor: 1, hasTouch: true, isMobile: true })
  const cityUrl = new URL(origin)
  cityUrl.hash = 'map=-78.49,-0.2,12.5'
  await city.goto(cityUrl.toString(), { waitUntil: 'domcontentloaded' })
  await city.locator('#map canvas').waitFor()
  await city.waitForTimeout(1800)
  await city.getByRole('button', { name: 'Círculo' }).click()
  await city.touchscreen.tap(180, 270)
  await city.locator('.selection-circle').waitFor({ state: 'visible' })
  await city.locator('.mobile-panel-nav .has-selection').waitFor()
  await city.screenshot({ path: join(captures, 'mobile-circulo-quito.png') })
  await city.getByRole('button', { name: 'Borrar selección' }).click()
  assert.equal(await city.locator('#selection-guide').isVisible(), false)
  await city.close()
  console.log('Mobile inspect, circle, radius, lasso, multi and clear: OK')
} finally {
  await browser.close()
}
