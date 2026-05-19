import { beforeEach, describe, expect, it, vi } from 'vitest'

const { serviceMock } = vi.hoisted(() => ({
  serviceMock: vi.fn()
}))

vi.mock('element-plus-secondary', () => ({
  ElLoading: {
    service: serviceMock
  }
}))

import { useLoading } from '../useLoading'

describe('useLoading', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    serviceMock.mockImplementation(() => ({ close: vi.fn() }))
  })

  it('returns open and close handlers', () => {
    const loading = useLoading()

    expect(typeof loading.open).toBe('function')
    expect(typeof loading.close).toBe('function')
  })

  it('opens a fullscreen loading instance with default options', () => {
    const loading = useLoading()

    loading.open()

    expect(serviceMock).toHaveBeenCalledWith({
      fullscreen: true,
      customClass: '',
      text: ''
    })
  })

  it('forwards custom class and text to ElLoading.service', () => {
    const loading = useLoading('dashboard-loading', 'Loading dashboard')

    loading.open()

    expect(serviceMock).toHaveBeenCalledWith({
      fullscreen: true,
      customClass: 'dashboard-loading',
      text: 'Loading dashboard'
    })
  })

  it('closes the active loading instance', () => {
    const closeMock = vi.fn()
    serviceMock.mockReturnValueOnce({ close: closeMock })
    const loading = useLoading()

    loading.open()
    loading.close()

    expect(closeMock).toHaveBeenCalledTimes(1)
  })

  it('closes the most recently opened loading instance', () => {
    const firstCloseMock = vi.fn()
    const secondCloseMock = vi.fn()
    serviceMock
      .mockReturnValueOnce({ close: firstCloseMock })
      .mockReturnValueOnce({ close: secondCloseMock })
    const loading = useLoading()

    loading.open()
    loading.open()
    loading.close()

    expect(firstCloseMock).not.toHaveBeenCalled()
    expect(secondCloseMock).toHaveBeenCalledTimes(1)
  })
})
