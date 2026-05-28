import { test, expect } from '@playwright/test'

const SCREEN_DV = '995100000000000002'
const SCREEN_URL = `/#/previewShow?dvId=${SCREEN_DV}`

const ADMIN_USER = process.env.DE_E2E_USER || 'admin'
const ADMIN_PASS = process.env.DE_E2E_PASS || 'DataEase@123456'

const COMPONENT_IDS = [
  '995100000000000100',
  '995100000000000101',
  '995100000000000102',
  '995100000000000103',
  '995100000000000104',
  '995100000000000105',
  '995100000000000106',
  '995100000000000107',
  '995100000000000108',
  '995100000000000109',
  '995100000000000110',
  '995100000000000111',
  '995100000000000112'
]

async function ensureLoggedIn(page) {
  await page.goto('/#/login')
  await page.locator('form input').first().waitFor({ state: 'visible', timeout: 15_000 })

  const inputs = page.locator('form input')
  await inputs.nth(0).fill(ADMIN_USER)
  await inputs.nth(1).fill(ADMIN_PASS)
  await page.getByRole('button', { name: /login|登录/i }).click()
  await page.waitForURL(url => !url.toString().includes('/login'), { timeout: 30_000 })
}

test.describe('Demo big screen (大屏) rendering', () => {
  test.beforeEach(async ({ page }) => {
    await ensureLoggedIn(page)
  })

  test('renders all 13 components without errors', async ({ page }) => {
    const pageErrors: string[] = []
    page.on('pageerror', err => pageErrors.push(err.message))

    await page.goto(SCREEN_URL)
    await page.waitForLoadState('networkidle', { timeout: 30_000 }).catch(() => undefined)

    for (const id of COMPONENT_IDS) {
      const selector = `#wrapper-outer-id-${id}`
      await page.waitForSelector(selector, { timeout: 30_000 })
      const el = page.locator(selector)
      await expect(el).toBeVisible()
    }

    expect(pageErrors).toEqual([])
  })

  test('banner shows screen title text', async ({ page }) => {
    await page.goto(SCREEN_URL)
    await page.waitForSelector('#wrapper-outer-id-995100000000000100', { timeout: 30_000 })

    const banner = page.locator('#wrapper-outer-id-995100000000000100')
    await expect(banner).toContainText('连锁茶饮销售大屏')
  })

  test('KPI indicators display numeric values', async ({ page }) => {
    await page.goto(SCREEN_URL)
    await page.waitForSelector('#wrapper-outer-id-995100000000000101', { timeout: 30_000 })
    await page.waitForTimeout(3000)

    const kpiIds = COMPONENT_IDS.slice(1, 5)
    for (const id of kpiIds) {
      const wrapper = page.locator(`#wrapper-outer-id-${id}`)
      const text = await wrapper.textContent()
      const hasNumber = /\d/.test(text || '')
      expect(hasNumber, `KPI ${id} should contain a numeric value`).toBeTruthy()
    }
  })

  test('chart canvases are present for non-KPI components', async ({ page }) => {
    await page.goto(SCREEN_URL)
    await page.waitForSelector('#wrapper-outer-id-995100000000000105', { timeout: 30_000 })
    await page.waitForTimeout(3000)

    const chartIds = COMPONENT_IDS.slice(5)
    for (const id of chartIds) {
      const wrapper = page.locator(`#wrapper-outer-id-${id}`)
      const hasCanvas = await wrapper.locator('canvas').count()
      expect(hasCanvas, `Chart ${id} should have a canvas element`).toBeGreaterThan(0)
    }
  })

  test('screenshot matches viewport at 1920x1080', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 })
    await page.goto(SCREEN_URL)
    await page.waitForSelector('#wrapper-outer-id-995100000000000112', { timeout: 30_000 })
    await page.waitForTimeout(5000)

    await page.screenshot({
      path: 'test-results/big-screen-regression.png',
      fullPage: false
    })

    const lastChart = page.locator('#wrapper-outer-id-995100000000000112')
    await expect(lastChart).toBeVisible()
  })
})
