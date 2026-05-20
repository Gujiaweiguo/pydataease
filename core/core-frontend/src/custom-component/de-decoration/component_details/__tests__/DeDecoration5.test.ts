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

import DeDecoration5 from '../DeDecoration5.vue'

const createProps = (overrides = {}) => ({
  curStyle: { width: 320, height: 240 },
  scale: 1,
  ...overrides
})

describe('DeDecoration5.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(DeDecoration5, { props: createProps() })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the root container with correct class', () => {
    const wrapper = shallowMount(DeDecoration5, { props: createProps() })
    expect(wrapper.find('.dv-decoration-5').exists()).toBe(true)
  })

  it('renders SVG element', () => {
    const wrapper = shallowMount(DeDecoration5, { props: createProps() })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('accepts dur prop', () => {
    const wrapper = shallowMount(DeDecoration5, {
      props: createProps({ dur: 5 })
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts line1Width and line2Width props', () => {
    const wrapper = shallowMount(DeDecoration5, {
      props: createProps({ line1Width: 4, line2Width: 3 })
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts custom colors', () => {
    const wrapper = shallowMount(DeDecoration5, {
      props: createProps({ color: ['#ff00ff', '#ffff00'] })
    })
    expect(wrapper.exists()).toBe(true)
  })
})
