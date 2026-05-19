import { defineComponent } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/utils/eventBus', () => ({
  default: { emit: vi.fn() }
}))
vi.mock('@/utils/canvasUtils', () => ({
  commonHandleDragStart: vi.fn(),
  commonHandleDragEnd: vi.fn()
}))
vi.mock('@/components/icon-group/chart-list', () => ({
  iconChartMap: {}
}))
vi.mock('@/components/icon-group/chart-dark-list', () => ({
  iconChartDarkMap: {}
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  CHART_TYPE_CONFIGS: [
    {
      category: 'quota',
      title: 'Quota',
      display: 'show',
      details: [
        { title: 'Bar', value: 'bar', icon: 'bar-icon' }
      ]
    }
  ]
}))
vi.mock('@/components/icon-custom/src/Icon.vue', () => ({
  default: { template: '<span><slot /></span>' }
}))
vi.mock('@/components/plugin', () => ({
  XpackComponent: defineComponent({ name: 'XpackComponent', template: '<div />' })
}))

import UserViewGroup from '../UserViewGroup.vue'

const globalStubs = {
  ElRow: { template: '<div><slot /></div>' },
  ElCol: { template: '<div><slot /></div>' },
  ElScrollbar: {
    template: '<div><slot /></div>',
    methods: { setScrollTop: vi.fn() }
  }
}

describe('UserViewGroup', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders with default props', () => {
    const wrapper = shallowMount(UserViewGroup, { global: { stubs: globalStubs } })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.group').exists()).toBe(true)
  })

  it('renders category list items', () => {
    const wrapper = shallowMount(UserViewGroup, { global: { stubs: globalStubs } })
    const items = wrapper.findAll('.li-custom')
    expect(items.length).toBeGreaterThan(0)
  })

  it('has group-left and group-right sections', () => {
    const wrapper = shallowMount(UserViewGroup, { global: { stubs: globalStubs } })
    expect(wrapper.find('.group-left').exists()).toBe(true)
    expect(wrapper.find('.group-right').exists()).toBe(true)
  })

  it('applies theme class on the group element', () => {
    const wrapper = shallowMount(UserViewGroup, {
      props: { themes: 'light' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.light').exists()).toBe(true)
  })
})
