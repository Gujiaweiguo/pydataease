import { beforeEach, describe, expect, it, vi } from 'vitest'

const { i18nState, translateMock } = vi.hoisted(() => ({
  i18nState: {
    current: undefined as
      | undefined
      | {
          global: {
            t: ReturnType<typeof vi.fn>
            locale: string
            availableLocales: string[]
          }
        }
  },
  translateMock: vi.fn((key: string, ...args: unknown[]) => JSON.stringify({ key, args }))
}))

vi.mock('@/plugins/vue-i18n', () => ({
  get i18n() {
    return i18nState.current
  }
}))

import { t as plainT, useI18n } from '../useI18n'

describe('useI18n', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    i18nState.current = undefined
  })

  it('falls back to returning the raw key when i18n is unavailable', () => {
    const { t } = useI18n()

    expect(t('dashboard.title')).toBe('dashboard.title')
  })

  it('prefixes the namespace before translating', () => {
    i18nState.current = {
      global: {
        t: translateMock,
        locale: 'en',
        availableLocales: ['en']
      }
    }

    const { t } = useI18n('dashboard')
    const result = t('title')

    expect(translateMock).toHaveBeenCalledWith('dashboard.title')
    expect(result).toBe(JSON.stringify({ key: 'dashboard.title', args: [] }))
  })

  it('does not double-prefix keys that already include the namespace', () => {
    i18nState.current = {
      global: {
        t: translateMock,
        locale: 'en',
        availableLocales: ['en']
      }
    }

    const { t } = useI18n('dashboard')

    t('dashboard.title')

    expect(translateMock).toHaveBeenCalledWith('dashboard.title')
  })

  it('returns the raw key when no namespace exists and the key is not nested', () => {
    i18nState.current = {
      global: {
        t: translateMock,
        locale: 'en',
        availableLocales: ['en']
      }
    }

    const { t } = useI18n()

    expect(t('title')).toBe('title')
    expect(translateMock).not.toHaveBeenCalled()
  })

  it('returns an empty string for falsy keys', () => {
    i18nState.current = {
      global: {
        t: translateMock,
        locale: 'en',
        availableLocales: ['en']
      }
    }

    const { t } = useI18n('dashboard')

    expect(t('')).toBe('')
    expect(translateMock).not.toHaveBeenCalled()
  })

  it('passes translation arguments through to the global translator', () => {
    i18nState.current = {
      global: {
        t: translateMock,
        locale: 'en',
        availableLocales: ['en']
      }
    }

    const { t } = useI18n('dashboard')
    const params = { count: 3 }

    t('items', params)

    expect(translateMock).toHaveBeenCalledWith('dashboard.items', params)
  })

  it('keeps the standalone helper behavior unchanged', () => {
    expect(plainT('plain.key')).toBe('plain.key')
  })
})
