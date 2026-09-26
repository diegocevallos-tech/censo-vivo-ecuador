/** End-to-end: dictionary search, category change, circle and distribution. */
import { chromium } from '@playwright/test'
import { mkdirSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

const root = process.env.CENSO_SITE_URL ?? 'http://127.0.0.1:5173/censo-vivo-ecuador/'
const output = resolve('../docs/capturas')
mkdirSync(output, { recursive: true })
const browser = await chromium.launch({ headless: true })
const errors = []
const ranges = []
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  page.on('pageerror', error => errors.push(error.message))
  page.on('console', message => {
    if (message.type() === 'error') errors.push(message.text())
  })
  page.on('response', response => {
    if (!response.url().includes('/data/variables/v2c/') || !response.url().endsWith('.bin')) return
    const range = response.headers()['content-range'] ?? ''
    const match = /^bytes (\d+)-(\d+)\/\d+$/.exec(range)
    ranges.push({ status: response.status(), bytes: match ? Number(match[2]) - Number(match[1]) + 1 : 0 })
  })
  await page.goto(`${root}#map=-78.41362,-0.09485,11`, { waitUntil: 'domcontentloaded' })
  await page.locator('.explorer-tab[data-tab="variables"]').click()
  await page.waitForFunction(() => document.querySelector('#variable-select')?.querySelector('option'),
    null, { timeout: 20000 })
  await page.locator('#variable-search').fill('techo')
  await page.locator('#variable-select').selectOption('V03')
  await page.waitForFunction(() => document.querySelector('#status')?.textContent
    ?.includes('Material predominante del techo'), null, { timeout: 30000 })
  const first = await page.locator('#variable-transfer').innerText()
  await page.locator('#variable-category').selectOption('1')
  await page.locator('#variable-category').selectOption('2')
  await page.waitForTimeout(1200)
  await page.locator('.toolbar [data-mode="circle"]').click()
  await page.mouse.move(720, 450)
  await page.mouse.down()
  await page.mouse.move(825, 450, { steps: 8 })
  await page.mouse.up()
  await page.locator('.variable-distribution .variable-bar').first().waitFor({ timeout: 30000 })
  const bars = await page.locator('.variable-distribution .variable-bar').count()
  const question = await page.locator('#variable-details').innerText()
  const status = await page.locator('#status').innerText()
  if (bars < 6 || !question.includes('techo') || errors.length || !ranges.length ||
      ranges.some(item => item.status !== 206 || item.bytes <= 0 || item.bytes >= 2_000_000)) {
    throw new Error(JSON.stringify({ bars, question, status, errors, ranges }))
  }
  await page.screenshot({ path: resolve(output, 'fase2c_variables_techo.png') })
  const result = { variable: 'V03', search: 'techo', firstDownload: first,
    category: '2', bars, status, ranges: ranges.length,
    largestRangeBytes: Math.max(...ranges.map(item => item.bytes)), errors }
  writeFileSync(resolve(output, 'fase2c_variables_e2e.json'), JSON.stringify(result, null, 2))
  console.log(JSON.stringify(result))
  await page.close()
} finally {
  await browser.close()
}
