import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store', () => ({ store: {} }))

vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  storeToRefs: vi.fn(() => ({})),
  createPinia: vi.fn()
}))

vi.mock('@/views/chart/components/editor/util/StringUtils', () => ({
  includesAny: (str: string, ...args: string[]) => args.some(a => str.includes(a)),
  equalsAny: (str: string, ...args: string[]) => args.some(a => str === a)
}))

import QuotaLabel from '@/views/chart/components/editor/drag-label/QuotaLabel.vue'

describe('QuotaLabel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders for table type', () => {
    const wrapper = shallowMount(QuotaLabel, {
      props: { view: { type: 'table-info' } },
      global: { stubs: {} }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('chart.drag_block_table_data_column')
  })

  it('renders for bar type', () => {
    const wrapper = shallowMount(QuotaLabel, {
      props: { view: { type: 'bar' } },
      global: { stubs: {} }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('chart.drag_block_value_axis')
  })

  it('renders for pie type', () => {
    const wrapper = shallowMount(QuotaLabel, {
      props: { view: { type: 'pie' } },
      global: { stubs: {} }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('chart.drag_block_pie_angle')
  })

  it('renders for funnel type', () => {
    const wrapper = shallowMount(QuotaLabel, {
      props: { view: { type: 'funnel' } },
      global: { stubs: {} }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('chart.drag_block_funnel_width')
  })

  it('renders for gauge type', () => {
    const wrapper = shallowMount(QuotaLabel, {
      props: { view: { type: 'gauge' } },
      global: { stubs: {} }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('chart.drag_block_gauge_angel')
  })

  it('renders for map type', () => {
    const wrapper = shallowMount(QuotaLabel, {
      props: { view: { type: 'map' } },
      global: { stubs: {} }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('chart.chart_data')
  })

  it('renders quota text', () => {
    const wrapper = shallowMount(QuotaLabel, {
      props: { view: { type: 'bar' } },
      global: { stubs: {} }
    })
    expect(wrapper.text()).toContain('chart.quota')
  })
})
