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

import DeDecoration4 from '../DeDecoration4.vue'

const createProps = (overrides = {}) => ({
  curStyle: { width: 320, height: 240 },
  scale: 1,
  ...overrides
})

describe('DeDecoration4.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(DeDecoration4, { props: createProps() })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the root container with correct class', () => {
    const wrapper = shallowMount(DeDecoration4, { props: createProps() })
    expect(wrapper.find('.dv-decoration-4').exists()).toBe(true)
  })

  it('renders SVG element', () => {
    const wrapper = shallowMount(DeDecoration4, { props: createProps() })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('accepts reverse prop', () => {
    const wrapper = shallowMount(DeDecoration4, {
      props: createProps({ reverse: true })
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts dur prop', () => {
    const wrapper = shallowMount(DeDecoration4, {
      props: createProps({ dur: 3 })
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts strokeWidth prop', () => {
    const wrapper = shallowMount(DeDecoration4, {
      props: createProps({ strokeWidth: 5 })
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts custom colors', () => {
    const wrapper = shallowMount(DeDecoration4, {
      props: createProps({ color: ['#778899', '#aabbcc'] })
    })
    expect(wrapper.exists()).toBe(true)
  })
})
