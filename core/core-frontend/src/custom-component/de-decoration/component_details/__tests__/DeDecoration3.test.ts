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

import DeDecoration3 from '../DeDecoration3.vue'

const createProps = (overrides = {}) => ({
  curStyle: { width: 320, height: 240 },
  scale: 1,
  ...overrides
})

describe('DeDecoration3.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(DeDecoration3, { props: createProps() })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the root container with correct class', () => {
    const wrapper = shallowMount(DeDecoration3, { props: createProps() })
    expect(wrapper.find('.dv-decoration-3').exists()).toBe(true)
  })

  it('renders SVG element', () => {
    const wrapper = shallowMount(DeDecoration3, { props: createProps() })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('accepts animationRatio prop', () => {
    const wrapper = shallowMount(DeDecoration3, {
      props: createProps({ animationRatio: 0.8 })
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts custom colors', () => {
    const wrapper = shallowMount(DeDecoration3, {
      props: createProps({ color: ['#112233', '#445566'] })
    })
    expect(wrapper.exists()).toBe(true)
  })
})
