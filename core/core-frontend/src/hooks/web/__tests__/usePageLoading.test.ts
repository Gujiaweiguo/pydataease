import { beforeEach, describe, expect, it, vi } from 'vitest'

const { appStoreMock } = vi.hoisted(() => ({
  appStoreMock: {
    setPageLoading: vi.fn()
  }
}))

vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => appStoreMock
}))

import { usePageLoading } from '../usePageLoading'

describe('usePageLoading', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns loadStart and loadDone handlers', () => {
    const pageLoading = usePageLoading()

    expect(typeof pageLoading.loadStart).toBe('function')
    expect(typeof pageLoading.loadDone).toBe('function')
  })

  it('starts the page loading state', () => {
    usePageLoading().loadStart()

    expect(appStoreMock.setPageLoading).toHaveBeenCalledWith(true)
  })

  it('stops the page loading state', () => {
    usePageLoading().loadDone()

    expect(appStoreMock.setPageLoading).toHaveBeenCalledWith(false)
  })

  it('toggles page loading in the expected order', () => {
    const pageLoading = usePageLoading()

    pageLoading.loadStart()
    pageLoading.loadDone()

    expect(appStoreMock.setPageLoading.mock.calls).toEqual([[true], [false]])
  })
})
