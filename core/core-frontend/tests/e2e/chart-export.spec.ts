import { test, expect } from '@playwright/test'

const DASHBOARD_URL =
  process.env.DE_E2E_DASHBOARD_URL ||
  '/#/panel/index?dvId=985192741891870720'

const CHART_WRAPPER_SELECTOR =
  process.env.DE_E2E_CHART_SELECTOR ||
  '#wrapper-outer-id-985192540141654016'

const ADMIN_USER = process.env.DE_E2E_USER || 'admin'
const ADMIN_PASS = process.env.DE_E2E_PASS || 'DataEase@123456'

async function ensureLoggedIn(page) {
  await page.goto('/#/login')

  const firstInput = page.locator('form input').first()
  await firstInput.waitFor({ state: 'visible', timeout: 15_000 })

  const inputs = page.locator('form input')
  await inputs.nth(0).fill(ADMIN_USER)
  await inputs.nth(1).fill(ADMIN_PASS)

  await page.getByRole('button', { name: /login|登录/i }).click()

  await page.waitForURL(
    url => !url.toString().includes('/login'),
    { timeout: 30_000 }
  )
}

test.describe('Chart Excel export', () => {
  test('dispatches innerExportDetails request without crashing', async ({ page }) => {
    const pageErrors: string[] = []
    page.on('pageerror', err => pageErrors.push(err.message))

    await ensureLoggedIn(page)
    await page.goto(DASHBOARD_URL)

    await page.waitForSelector(CHART_WRAPPER_SELECTOR, { timeout: 30_000 })
    await page.waitForLoadState('networkidle')

    await page.locator(CHART_WRAPPER_SELECTOR).hover()

    const trigger = page.locator(`${CHART_WRAPPER_SELECTOR} i[role="button"]`).first()
    await trigger.click({ force: true })

    const excelItem = page.getByRole('menuitem', { name: 'Excel' })
    await excelItem.waitFor({ state: 'visible', timeout: 5_000 })

    const [exportReq] = await Promise.all([
      page.waitForRequest(
        req => req.method() === 'POST' && req.url().includes('/chartData/innerExportDetails'),
        { timeout: 15_000 }
      ),
      excelItem.click()
    ])

    await expect(page.locator('body')).toContainText(/数据导出中心|Export Center/, {
      timeout: 10_000
    })

    expect(pageErrors).toEqual([])
  })
})
