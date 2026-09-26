import { chromium } from '@playwright/test'
import { resolve } from 'node:path'

const root = process.env.CENSO_SITE_URL ?? 'http://127.0.0.1:5173/censo-vivo-ecuador/'
const browser = await chromium.launch({ headless: true })
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  const errors = []
  page.on('pageerror', error => errors.push(error.message))
  await page.goto(`${root}#map=-78.41362,-0.09485,11`, { waitUntil: 'domcontentloaded' })
  await page.locator('.explorer-tab[data-tab="variables"]').click()
  await page.waitForFunction(() => document.querySelector('#variable-select')?.querySelector('option'))
  await page.locator('#variable-search').fill('P08P')
  await page.locator('#variable-select').selectOption('P08P')
  await page.waitForFunction(() => document.querySelector('#level')?.textContent
    ?.toLowerCase().includes('cantón'), null, { timeout: 30000 })
  const note = await page.locator('#availability').innerText()
  if (!note.includes('Mapa ajustado a Cantón') && !note.includes('Mapa ajustado a cantón')) {
    throw new Error(`Missing min_level note: ${note}`)
  }
  await page.screenshot({ path: resolve('../docs/capturas/fase2c_min_level_canton.png') })
  await page.locator('#variable-search').fill('P03')
  await page.locator('#variable-select').selectOption('P03')
  await page.waitForFunction(() => document.querySelector('#status')?.textContent
    ?.includes('Años cumplidos'), null, { timeout: 30000 })
  const age = await page.locator('#variable-details').innerText()
  if (!age.includes('Media aproximada') || errors.length) {
    throw new Error(JSON.stringify({ age, errors }))
  }
  console.log(JSON.stringify({ minLevel: note, ageMean: 'aproximada', errors }))
  await page.close()
} finally {
  await browser.close()
}
