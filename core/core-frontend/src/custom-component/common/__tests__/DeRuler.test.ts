import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  canvasStyleDataRef: { value: { width: 800, height: 600, scale: 100 } },
  curComponentRef: { value: null as any },
  componentDataRef: { value: [] as any[] }
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
    canvasStyleData: mocks.canvasStyleDataRef,
    curComponent: mocks.curComponentRef,
    componentData: mocks.componentDataRef
  })
}))

import DeRuler from '../DeRuler.vue'

const globalStubs = {
  ArrowLeft: { template: '<span />' },
  ArrowRight: { template: '<span />' }
}

describe('DeRuler', () => {
  beforeEach(() => {
    mocks.canvasStyleDataRef.value = { width: 800, height: 600, scale: 100 }
    mocks.curComponentRef.value = null
    mocks.componentDataRef.value = []
  })

  it('renders with default horizontal direction', () => {
    const wrapper = shallowMount(DeRuler, { global: { stubs: globalStubs } })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.ruler-outer').exists()).toBe(true)
  })

  it('does not show cur-shadow when no curComponent', () => {
    const wrapper = shallowMount(DeRuler, { global: { stubs: globalStubs } })
    expect(wrapper.find('.cur-shadow').exists()).toBe(false)
  })

  it('shows cur-shadow when curComponent exists and not hidden category', () => {
    mocks.curComponentRef.value = {
      style: { left: 10, top: 20, width: 100, height: 50 },
      canvasId: 'canvas-main',
      category: 'base'
    }
    const wrapper = shallowMount(DeRuler, { global: { stubs: globalStubs } })
    expect(wrapper.find('.cur-shadow').exists()).toBe(true)
  })

  it('renders tick marks based on ruler size', () => {
    const wrapper = shallowMount(DeRuler, { global: { stubs: globalStubs } })
    const ticks = wrapper.findAll('.ruler-tick')
    expect(ticks.length).toBeGreaterThan(0)
  })

  it('applies vertical class when direction is vertical', () => {
    const wrapper = shallowMount(DeRuler, {
      props: { direction: 'vertical' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.ruler-vertical').exists()).toBe(true)
  })

  it('exposes rulerScroll method', () => {
    const wrapper = shallowMount(DeRuler, { global: { stubs: globalStubs } })
    expect(typeof wrapper.vm.rulerScroll).toBe('function')
  })
})
