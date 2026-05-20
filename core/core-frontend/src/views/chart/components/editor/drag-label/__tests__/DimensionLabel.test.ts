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

import DimensionLabel from '@/views/chart/components/editor/drag-label/DimensionLabel.vue'

describe('DimensionLabel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders for table type', () => {
    const wrapper = shallowMount(DimensionLabel, {
      props: { view: { type: 'table-info' } },
      global: { stubs: {} }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('chart.drag_block_table_data_column')
  })

  it('renders for bar type', () => {
    const wrapper = shallowMount(DimensionLabel, {
      props: { view: { type: 'bar' } },
      global: { stubs: {} }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('chart.drag_block_type_axis')
  })

  it('renders for pie type', () => {
    const wrapper = shallowMount(DimensionLabel, {
      props: { view: { type: 'pie' } },
      global: { stubs: {} }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('chart.drag_block_pie_label')
  })

  it('renders for map type', () => {
    const wrapper = shallowMount(DimensionLabel, {
      props: { view: { type: 'map' } },
      global: { stubs: {} }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('chart.area')
  })

  it('renders for funnel type', () => {
    const wrapper = shallowMount(DimensionLabel, {
      props: { view: { type: 'funnel' } },
      global: { stubs: {} }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('chart.drag_block_funnel_split')
  })

  it('renders for radar type', () => {
    const wrapper = shallowMount(DimensionLabel, {
      props: { view: { type: 'radar' } },
      global: { stubs: {} }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('chart.drag_block_radar_label')
  })

  it('renders dimension text', () => {
    const wrapper = shallowMount(DimensionLabel, {
      props: { view: { type: 'bar' } },
      global: { stubs: {} }
    })
    expect(wrapper.text()).toContain('chart.dimension')
  })
})
