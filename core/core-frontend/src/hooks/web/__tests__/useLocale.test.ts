import { beforeEach, describe, expect, it, vi } from 'vitest'

const { fixtureBaseUrl, i18nState, localeStore, setHtmlPageLangMock } = vi.hoisted(() => ({
  fixtureBaseUrl: import.meta.url.replace(/__tests__\/[^/]*$/, '__tests__/fixtures'),
  i18nState: {
    current: undefined as any
  },
  localeStore: {
    setCurrentLocale: vi.fn().mockResolvedValue(undefined),
    getCurrentLocale: { lang: 'en' },
    getLocaleMap: Promise.resolve([{ lang: 'fr-CA', name: 'acme' }])
  },
  setHtmlPageLangMock: vi.fn()
}))

vi.mock('@/plugins/vue-i18n', () => ({
  get i18n() {
    return i18nState.current
  }
}))

vi.mock('@/store/modules/locale', () => ({
  useLocaleStoreWithOut: () => localeStore
}))

vi.mock('@/plugins/vue-i18n/helper', () => ({
  setHtmlPageLang: setHtmlPageLangMock
}))

vi.mock('@/config/axios/service', () => ({
  PATH_URL: fixtureBaseUrl
}))

import enLocale from '@/locales/en'
import twLocale from '@/locales/tw'
import zhCnLocale from '@/locales/zh-CN'
import { useLocale } from '../useLocale'

describe('useLocale', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localeStore.getCurrentLocale = { lang: 'en' }
    localeStore.getLocaleMap = Promise.resolve([{ lang: 'fr-CA', name: 'acme' }])
  })

  it('switches legacy mode to zh-CN and loads the built-in locale module', async () => {
    const setLocaleMessage = vi.fn()
    i18nState.current = {
      mode: 'legacy',
      global: {
        locale: 'en',
        setLocaleMessage
      }
    }

    await useLocale().changeLocale('zh-CN' as LocaleType)

    expect(setLocaleMessage).toHaveBeenCalledWith('zh-CN', zhCnLocale)
    expect(i18nState.current.global.locale).toBe('zh-CN')
    expect(localeStore.setCurrentLocale).toHaveBeenCalledWith({ lang: 'zh-CN' })
    expect(setHtmlPageLangMock).toHaveBeenCalledWith('zh-CN')
  })

  it('switches composition mode by mutating locale.value', async () => {
    const setLocaleMessage = vi.fn()
    i18nState.current = {
      mode: 'composition',
      global: {
        locale: { value: 'en' },
        setLocaleMessage
      }
    }

    await useLocale().changeLocale('tw' as LocaleType)

    expect(setLocaleMessage).toHaveBeenCalledWith('tw', twLocale)
    expect(i18nState.current.global.locale.value).toBe('tw')
    expect(localeStore.setCurrentLocale).toHaveBeenCalledWith({ lang: 'tw' })
    expect(setHtmlPageLangMock).toHaveBeenCalledWith('tw')
  })

  it('loads the English built-in locale module when switching to en', async () => {
    const setLocaleMessage = vi.fn()
    i18nState.current = {
      mode: 'legacy',
      global: {
        locale: 'zh-CN',
        setLocaleMessage
      }
    }

    await useLocale().changeLocale('en' as LocaleType)

    expect(setLocaleMessage).toHaveBeenCalledWith('en', enLocale)
    expect(localeStore.setCurrentLocale).toHaveBeenCalledWith({ lang: 'en' })
  })

  it('loads remote locale modules for custom languages based on the current locale map', async () => {
    const setLocaleMessage = vi.fn()
    i18nState.current = {
      mode: 'legacy',
      global: {
        locale: 'en',
        setLocaleMessage
      }
    }
    localeStore.getCurrentLocale = { lang: 'fr-CA' }
    localeStore.getLocaleMap = Promise.resolve([{ lang: 'fr-CA', name: 'acme' }])

    await useLocale().changeLocale('fr-CA' as LocaleType)

    expect(setLocaleMessage).toHaveBeenCalledWith(
      'fr-CA',
      expect.objectContaining({
        greeting: 'bonjour',
        layout: { title: 'Acme locale' }
      })
    )
    expect(localeStore.setCurrentLocale).toHaveBeenCalledWith({ lang: 'fr-CA' })
    expect(setHtmlPageLangMock).toHaveBeenCalledWith('fr-CA')
  })
})
