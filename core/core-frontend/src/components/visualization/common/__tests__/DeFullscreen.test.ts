import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    setFullscreenFlag: vi.fn(),
    setEditMode: vi.fn()
  })
}))
vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn(() => ({ emitter: { emit: vi.fn(), on: vi.fn() } }))
}))

import DeFullscreen from '../DeFullscreen.vue'

describe('DeFullscreen', () => {
  it('renders component', () => {
    const wrapper = shallowMount(DeFullscreen, {
      props: { themes: 'light', componentType: 'button', showPosition: 'preview' }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders a span element', () => {
    const wrapper = shallowMount(DeFullscreen, {
      props: { themes: 'light', componentType: 'button', showPosition: 'preview' }
    })
    expect(wrapper.find('span').exists()).toBe(true)
  })

  it('exposes toggleFullscreen method', () => {
    const wrapper = shallowMount(DeFullscreen, {
      props: { themes: 'light', componentType: 'button', showPosition: 'preview' }
    })
    expect(typeof wrapper.vm.toggleFullscreen).toBe('function')
  })
})
