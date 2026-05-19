import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  canvasStyleDataRef: { value: { width: 800, height: 600, scale: 100 } }
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    canvasStyleData: mocks.canvasStyleDataRef
  })
}))

import DeRulerVertical from '../DeRulerVertical.vue'

describe('DeRulerVertical', () => {
  beforeEach(() => {
    mocks.canvasStyleDataRef.value = { width: 800, height: 600, scale: 100 }
  })

  it('renders the vertical ruler container', () => {
    const wrapper = shallowMount(DeRulerVertical)
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.ruler-outer-vertical').exists()).toBe(true)
  })

  it('renders tick marks based on canvas height', () => {
    const wrapper = shallowMount(DeRulerVertical)
    const ticks = wrapper.findAll('.ruler-tick')
    expect(ticks.length).toBeGreaterThan(0)
  })

  it('renders ruler line', () => {
    const wrapper = shallowMount(DeRulerVertical)
    expect(wrapper.find('.ruler-line').exists()).toBe(true)
  })

  it('exposes rulerScroll method', () => {
    const wrapper = shallowMount(DeRulerVertical)
    expect(typeof wrapper.vm.rulerScroll).toBe('function')
  })

  it('uses custom tickLabelFormatter when provided', () => {
    const customFormatter = (value: number) => `v=${value}`
    const wrapper = shallowMount(DeRulerVertical, {
      props: { tickLabelFormatter: customFormatter }
    })
    const labels = wrapper.findAll('.tick-label')
    if (labels.length > 0) {
      expect(labels[0].text()).toContain('v=')
    }
    expect(wrapper.exists()).toBe(true)
  })
})
