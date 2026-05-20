import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/custom-component/de-decoration/component_details/config', () => ({
  customMergeColor: (defaults: string[], colors: string[]) =>
    defaults.map((d, i) => (colors && colors[i] != null ? colors[i] : d))
}))

import DeBoard8 from '../DeBoard8.vue'

const createProps = (overrides = {}) => ({
  curStyle: { width: 320, height: 240 },
  scale: 1,
  ...overrides
})

describe('DeBoard8.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(DeBoard8, { props: createProps() })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the root container with correct class', () => {
    const wrapper = shallowMount(DeBoard8, { props: createProps() })
    expect(wrapper.find('.dv-border-box-8').exists()).toBe(true)
  })

  it('renders SVG elements', () => {
    const wrapper = shallowMount(DeBoard8, { props: createProps() })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('renders the border-box-content slot container', () => {
    const wrapper = shallowMount(DeBoard8, { props: createProps() })
    expect(wrapper.find('.border-box-content').exists()).toBe(true)
  })

  it('accepts duration prop', () => {
    const wrapper = shallowMount(DeBoard8, {
      props: createProps({ duration: 5 })
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts custom colors', () => {
    const wrapper = shallowMount(DeBoard8, {
      props: createProps({ color: ['#999999', '#aaaaaa'] })
    })
    expect(wrapper.exists()).toBe(true)
  })
})
