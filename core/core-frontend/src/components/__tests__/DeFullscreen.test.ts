import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const { emitterEmitMock, setEditModeMock, setFullscreenFlagMock } = vi.hoisted(() => ({
  emitterEmitMock: vi.fn(),
  setEditModeMock: vi.fn(),
  setFullscreenFlagMock: vi.fn()
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    setFullscreenFlag: setFullscreenFlagMock,
    setEditMode: setEditModeMock
  })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({
    emitter: {
      emit: emitterEmitMock
    }
  })
}))

import DeFullscreen from '../visualization/common/DeFullscreen.vue'

const getExposedVm = (wrapper: ReturnType<typeof mount>) =>
  wrapper.vm as unknown as { toggleFullscreen: () => void }

describe('DeFullscreen', () => {
  let fullscreenElement: Element | null
  const mountedWrappers: Array<ReturnType<typeof mount>> = []

  afterEach(() => {
    mountedWrappers.splice(0).forEach(wrapper => {
      wrapper.unmount()
    })
  })

  beforeEach(() => {
    vi.clearAllMocks()
    fullscreenElement = null

    Object.defineProperty(document, 'fullscreenElement', {
      configurable: true,
      get: () => fullscreenElement
    })

    Object.defineProperty(document, 'exitFullscreen', {
      configurable: true,
      value: vi.fn(() => {
        fullscreenElement = null
      })
    })

    Object.defineProperty(document.body, 'requestFullscreen', {
      configurable: true,
      value: vi.fn(() => {
        fullscreenElement = document.body
      })
    })
  })

  it('requests fullscreen when the document is not already fullscreen', () => {
    const wrapper = mount(DeFullscreen)
    mountedWrappers.push(wrapper)

    getExposedVm(wrapper).toggleFullscreen()

    expect(document.body.requestFullscreen).toHaveBeenCalledTimes(1)
  })

  it('exits fullscreen when the document is already fullscreen', () => {
    fullscreenElement = document.body
    const wrapper = mount(DeFullscreen)
    mountedWrappers.push(wrapper)

    getExposedVm(wrapper).toggleFullscreen()

    expect(document.exitFullscreen).toHaveBeenCalledTimes(1)
  })

  it('syncs fullscreen status and edit mode for edit pages', () => {
    const wrapper = mount(DeFullscreen, {
      props: {
        showPosition: 'edit'
      }
    })
    mountedWrappers.push(wrapper)

    fullscreenElement = document.body
    document.dispatchEvent(new Event('fullscreenchange'))
    fullscreenElement = null
    document.dispatchEvent(new Event('fullscreenchange'))

    expect(setFullscreenFlagMock).toHaveBeenNthCalledWith(1, true)
    expect(setEditModeMock).toHaveBeenNthCalledWith(1, 'preview')
    expect(setFullscreenFlagMock).toHaveBeenNthCalledWith(2, false)
    expect(setEditModeMock).toHaveBeenNthCalledWith(2, 'edit')
  })

  it('emits canvasScrollRestore on fullscreen changes in dvEdit mode', () => {
    const wrapper = mount(DeFullscreen, {
      props: {
        showPosition: 'dvEdit'
      }
    })
    mountedWrappers.push(wrapper)

    fullscreenElement = document.body
    document.dispatchEvent(new Event('fullscreenchange'))

    expect(emitterEmitMock).toHaveBeenCalledWith('canvasScrollRestore')
  })

  it('forces exit on Escape while fullscreen is active', () => {
    const wrapper = mount(DeFullscreen)
    mountedWrappers.push(wrapper)
    fullscreenElement = document.body

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))

    expect(document.exitFullscreen).toHaveBeenCalledTimes(1)
  })
})
