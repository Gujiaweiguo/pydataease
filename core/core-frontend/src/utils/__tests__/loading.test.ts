import { beforeEach, describe, expect, it, vi } from 'vitest'

const { requestStoreMock } = vi.hoisted(() => ({
  requestStoreMock: {
    loadingMap: {} as Record<string, number>,
    addLoading: vi.fn(),
    reduceLoading: vi.fn()
  }
}))

vi.mock('@/store/modules/request', () => ({
  useRequestStoreWithOut: () => requestStoreMock
}))

import { tryHideLoading, tryShowLoading } from '../loading'

describe('loading utils', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    requestStoreMock.loadingMap = {}
  })

  it('adds a loading marker when identification is provided', () => {
    tryShowLoading('panel-a')

    expect(requestStoreMock.addLoading).toHaveBeenCalledWith('panel-a')
  })

  it('ignores falsy ids when showing loading', () => {
    tryShowLoading('')

    expect(requestStoreMock.addLoading).not.toHaveBeenCalled()
  })

  it('reduces loading count when the tracked request is active', () => {
    requestStoreMock.loadingMap.panelA = 2

    tryHideLoading('panelA')

    expect(requestStoreMock.reduceLoading).toHaveBeenCalledWith('panelA')
  })

  it('does not reduce loading when the count is zero or missing', () => {
    requestStoreMock.loadingMap.zeroPanel = 0

    tryHideLoading('zeroPanel')
    tryHideLoading('missingPanel')

    expect(requestStoreMock.reduceLoading).not.toHaveBeenCalled()
  })

  it('ignores falsy ids when hiding loading', () => {
    tryHideLoading(undefined)

    expect(requestStoreMock.reduceLoading).not.toHaveBeenCalled()
  })
})
