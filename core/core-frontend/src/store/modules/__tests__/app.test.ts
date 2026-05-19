import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const { wsCacheSet, modelApi } = vi.hoisted(() => ({
  wsCacheSet: vi.fn(),
  modelApi: vi.fn()
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: {
      set: wsCacheSet
    }
  })
}))

vi.mock('@/api/login', () => ({
  modelApi
}))

import { useAppStore } from '../app'

describe('useAppStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    wsCacheSet.mockReset()
    modelApi.mockReset()
    document.title = ''
  })

  it('has the expected initial state', () => {
    const store = useAppStore()

    expect(store.$state).toMatchObject({
      size: true,
      pageLoading: false,
      title: '',
      dekey: 'DataEaseKey',
      desktop: false,
      isDataEaseBi: false,
      isIframe: false,
      arrowSide: false
    })
  })

  it('exposes getters for default state values', () => {
    const store = useAppStore()

    expect(store.getSize).toBe(true)
    expect(store.getArrowSide).toBe(false)
    expect(store.getPageLoading).toBe(false)
    expect(store.getTitle).toBe('')
    expect(store.getIsDataEaseBi).toBe(false)
    expect(store.getIsIframe).toBe(false)
    expect(store.getDekey).toBe('DataEaseKey')
    expect(store.getDesktop).toBe(false)
  })

  it('updates boolean flags through dedicated actions', () => {
    const store = useAppStore()

    store.setSize(false)
    store.setArrowSide(true)
    store.setIsDataEaseBi(true)
    store.setIsIframe(true)
    store.setPageLoading(true)

    expect(store.$state).toMatchObject({
      size: false,
      arrowSide: true,
      isDataEaseBi: true,
      isIframe: true,
      pageLoading: true
    })
  })

  it('updates the title and synchronizes document.title', () => {
    const store = useAppStore()

    store.setTitle('Dashboard Center')

    expect(store.title).toBe('Dashboard Center')
    expect(document.title).toBe('Dashboard Center')
  })

  it('updates the dekey value', () => {
    const store = useAppStore()

    store.setDekey('custom-key')

    expect(store.dekey).toBe('custom-key')
    expect(store.getDekey).toBe('custom-key')
  })

  it('stores desktop mode through setDesktop and persists it in cache', () => {
    const store = useAppStore()

    store.setDesktop(true)

    expect(store.desktop).toBe(true)
    expect(wsCacheSet).toHaveBeenCalledWith('app.desktop', true)
  })

  it('loads app model from the API and caches the result', async () => {
    const store = useAppStore()
    modelApi.mockResolvedValue({ data: true })

    await store.setAppModel()

    expect(modelApi).toHaveBeenCalledTimes(1)
    expect(store.desktop).toBe(true)
    expect(wsCacheSet).toHaveBeenCalledWith('app.desktop', true)
  })
})
