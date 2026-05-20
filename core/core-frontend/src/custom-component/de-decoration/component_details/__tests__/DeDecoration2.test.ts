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

import DeDecoration2 from '../DeDecoration2.vue'

const createProps = (overrides = {}) => ({
  curStyle: { width: 320, height: 240 },
  scale: 1,
  ...overrides
})

describe('DeDecoration2.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(DeDecoration2, { props: createProps() })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the root container with correct class', () => {
    const wrapper = shallowMount(DeDecoration2, { props: createProps() })
    expect(wrapper.find('.dv-decoration-2').exists()).toBe(true)
  })

  it('renders SVG element', () => {
    const wrapper = shallowMount(DeDecoration2, { props: createProps() })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('applies style based on curStyle and scale', () => {
    const wrapper = shallowMount(DeDecoration2, {
      props: createProps({ curStyle: { width: 600, height: 400 }, scale: 1.5 })
    })
    const style = wrapper.find('.dv-decoration-2').attributes('style')
    expect(style).toContain('600px')
    expect(style).toContain('scale(1.5)')
  })

  it('accepts reverse prop', () => {
    const wrapper = shallowMount(DeDecoration2, {
      props: createProps({ reverse: true })
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts dur prop', () => {
    const wrapper = shallowMount(DeDecoration2, {
      props: createProps({ dur: 10 })
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts custom colors', () => {
    const wrapper = shallowMount(DeDecoration2, {
      props: createProps({ color: ['#aabbcc', '#ddeeff'] })
    })
    expect(wrapper.exists()).toBe(true)
  })
})
