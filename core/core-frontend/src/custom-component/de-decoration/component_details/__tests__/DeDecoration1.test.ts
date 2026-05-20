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

import DeDecoration1 from '../DeDecoration1.vue'

const createProps = (overrides = {}) => ({
  curStyle: { width: 320, height: 240 },
  scale: 1,
  ...overrides
})

describe('DeDecoration1.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(DeDecoration1, { props: createProps() })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the root container with correct class', () => {
    const wrapper = shallowMount(DeDecoration1, { props: createProps() })
    expect(wrapper.find('.dv-decoration-1').exists()).toBe(true)
  })

  it('renders SVG element', () => {
    const wrapper = shallowMount(DeDecoration1, { props: createProps() })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('applies style based on curStyle and scale', () => {
    const wrapper = shallowMount(DeDecoration1, {
      props: createProps({ curStyle: { width: 500, height: 300 }, scale: 2 })
    })
    const style = wrapper.find('.dv-decoration-1').attributes('style')
    expect(style).toContain('500px')
    expect(style).toContain('scale(2)')
  })

  it('accepts custom colors', () => {
    const wrapper = shallowMount(DeDecoration1, {
      props: createProps({ color: ['#ff0000', '#00ff00'] })
    })
    expect(wrapper.exists()).toBe(true)
  })
})
