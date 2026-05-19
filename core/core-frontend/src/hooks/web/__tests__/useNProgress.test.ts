import { beforeEach, describe, expect, it, vi } from 'vitest'

const { configureMock, doneMock, nextTickMock, startMock, useCssVarMock } = vi.hoisted(() => ({
  configureMock: vi.fn(),
  doneMock: vi.fn(),
  nextTickMock: vi.fn(() => Promise.resolve()),
  startMock: vi.fn(),
  useCssVarMock: vi.fn(() => ({ value: '#1f6feb' }))
}))

vi.mock('vue', async () => {
  const actual = await vi.importActual<typeof import('vue')>('vue')
  return {
    ...actual,
    nextTick: nextTickMock,
    unref: (value: { value?: string } | string) =>
      typeof value === 'object' ? value?.value : value
  }
})

vi.mock('@vueuse/core', () => ({
  useCssVar: useCssVarMock
}))

vi.mock('nprogress', () => ({
  default: {
    configure: configureMock,
    start: startMock,
    done: doneMock
  }
}))

import { useNProgress } from '../useNProgress'

describe('useNProgress', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    document.body.innerHTML = ''
  })

  it('configures NProgress without a spinner', () => {
    useNProgress()

    expect(configureMock).toHaveBeenCalledWith({ showSpinner: false })
  })

  it('starts the progress bar', () => {
    const progress = useNProgress()

    progress.start()

    expect(startMock).toHaveBeenCalledTimes(1)
  })

  it('finishes the progress bar', () => {
    const progress = useNProgress()

    progress.done()

    expect(doneMock).toHaveBeenCalledTimes(1)
  })

  it('applies the primary color to the progress bar after nextTick', async () => {
    document.body.innerHTML = '<div id="nprogress"><div class="bar"></div></div>'

    useNProgress()
    await Promise.resolve()

    const bar = document.querySelector('#nprogress .bar') as HTMLElement
    expect(nextTickMock).toHaveBeenCalledTimes(1)
    expect(bar.style.background).toBe('#1f6feb')
  })

  it('skips color assignment when the progress bar element is missing', async () => {
    expect(() => useNProgress()).not.toThrow()

    await Promise.resolve()

    expect(nextTickMock).toHaveBeenCalledTimes(1)
  })
})
