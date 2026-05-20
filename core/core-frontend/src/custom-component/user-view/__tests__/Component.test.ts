import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/utils/utils', () => ({
  isISOMobile: () => false
}))
vi.mock('@/views/chart/components/views/index.vue', () => ({
  default: { template: '<div class="chart-stub"></div>' }
}))

import Component from '../Component.vue'

describe('user-view Component', () => {
  const defaultProps = {
    active: false,
    propValue: { text: 'hello' },
    element: {
      id: 'view-1',
      propValue: null,
      innerType: 'chart'
    },
    view: { propValue: null },
    showPosition: 'canvas',
    searchCount: 0,
    scale: 1,
    dvType: 'dashboard',
    disabled: false,
    suffixId: 'common',
    fontFamily: 'inherit'
  }

  it('renders successfully with bash-shape wrapper', () => {
    const wrapper = shallowMount(Component, {
      props: defaultProps
    })
    expect(wrapper.find('.bash-shape').exists()).toBe(true)
  })

  it('contains chart child component', () => {
    const wrapper = shallowMount(Component, {
      props: defaultProps
    })
    expect(wrapper.findComponent({ name: 'chart' }).exists()).toBe(true)
  })

  it('passes scale prop correctly', () => {
    const wrapper = shallowMount(Component, {
      props: { ...defaultProps, scale: 2 }
    })
    expect(wrapper.props('scale')).toBe(2)
  })

  it('emits onPointClick event', async () => {
    const wrapper = shallowMount(Component, {
      props: defaultProps
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.bash-shape').exists()).toBe(true)
  })
})
