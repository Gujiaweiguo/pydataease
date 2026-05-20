import { describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store', () => ({ store: {} }))

vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  storeToRefs: vi.fn(() => ({})),
  createPinia: vi.fn()
}))

vi.mock('vue-i18n', () => ({
  createI18n: (options: any) => ({
    global: { locale: options.locale },
    install: vi.fn()
  })
}))

vi.mock('@/store/modules/locale', () => ({
  useLocaleStoreWithOut: () => ({
    getCurrentLocale: { lang: 'zh-CN' },
    getLocaleMap: Promise.resolve([{ lang: 'zh-CN', name: 'zh-CN' }]),
    setLang: vi.fn(),
    setCurrentLocale: vi.fn()
  })
}))

import { setHtmlPageLang } from '@/plugins/vue-i18n/helper'

describe('vue-i18n helper', () => {
  it('setHtmlPageLang sets lang attribute on html element', () => {
    setHtmlPageLang('zh-CN' as any)
    const htmlEl = document.querySelector('html')
    expect(htmlEl?.getAttribute('lang')).toBe('zh-CN')
  })

  it('setHtmlPageLang changes lang to en', () => {
    setHtmlPageLang('en' as any)
    const htmlEl = document.querySelector('html')
    expect(htmlEl?.getAttribute('lang')).toBe('en')
  })
})
