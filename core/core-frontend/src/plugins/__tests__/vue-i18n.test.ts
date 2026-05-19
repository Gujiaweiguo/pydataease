import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('vue-i18n', () => ({
  createI18n: vi.fn().mockReturnValue({ global: { t: (k: string) => k } })
}))

vi.mock('@/store/modules/locale', () => ({
  useLocaleStoreWithOut: () => ({
    getCurrentLocale: { lang: 'zh-CN' },
    getLocaleMap: Promise.resolve([{ lang: 'zh-CN', custom: false, name: '中文' }]),
    setLang: vi.fn(),
    setCurrentLocale: vi.fn()
  })
}))

vi.mock('@/config/axios/service', () => ({
  PATH_URL: './',
  service: {} as any,
  cancelMap: new Map()
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('../vue-i18n/helper', () => ({
  setHtmlPageLang: vi.fn()
}))

vi.mock('@/../src/locales/zh-CN', () => ({
  default: { hello: '你好', common: { confirm: '确认' } }
}))

describe('vue-i18n plugin', () => {
  let app: { use: ReturnType<typeof vi.fn> }

  beforeEach(() => {
    vi.clearAllMocks()
    app = { use: vi.fn() }
  })

  it('setupI18n should call app.use with the i18n instance', async () => {
    const { setupI18n } = await import('../vue-i18n/index')
    await setupI18n(app as any)
    expect(app.use).toHaveBeenCalledTimes(1)
    expect(app.use).toHaveBeenCalledWith(expect.objectContaining({ global: expect.any(Object) }))
  })

  it('setupI18n should call createI18n with legacy: false', async () => {
    const { createI18n } = await import('vue-i18n')
    const { setupI18n } = await import('../vue-i18n/index')
    await setupI18n(app as any)
    expect(createI18n).toHaveBeenCalledWith(expect.objectContaining({ legacy: false }))
  })

  it('after setupI18n the exported i18n variable is set', async () => {
    const mod = await import('../vue-i18n/index')
    await mod.setupI18n(app as any)
    expect(mod.i18n).toBeDefined()
    expect(mod.i18n).toEqual(expect.objectContaining({ global: expect.any(Object) }))
  })
})
