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

import DeBoard2 from '../DeBoard2.vue'

const createProps = (overrides = {}) => ({
  curStyle: { width: 320, height: 240 },
  scale: 1,
  ...overrides
})

describe('DeBoard2.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(DeBoard2, { props: createProps() })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the root container with correct class', () => {
    const wrapper = shallowMount(DeBoard2, { props: createProps() })
    expect(wrapper.find('.dv-border-box-2').exists()).toBe(true)
  })

  it('renders SVG elements', () => {
    const wrapper = shallowMount(DeBoard2, { props: createProps() })
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('renders the border-box-content slot container', () => {
    const wrapper = shallowMount(DeBoard2, { props: createProps() })
    expect(wrapper.find('.border-box-content').exists()).toBe(true)
  })

  it('applies style based on curStyle and scale', () => {
    const wrapper = shallowMount(DeBoard2, {
      props: createProps({ curStyle: { width: 600, height: 400 }, scale: 1.5 })
    })
    const style = wrapper.find('.dv-border-box-2').attributes('style')
    expect(style).toContain('600px')
    expect(style).toContain('scale(1.5)')
  })

  it('accepts custom colors', () => {
    const wrapper = shallowMount(DeBoard2, {
      props: createProps({ color: ['#112233', '#445566'] })
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts backgroundColor prop', () => {
    const wrapper = shallowMount(DeBoard2, {
      props: createProps({ backgroundColor: '#ffffff' })
    })
    expect(wrapper.exists()).toBe(true)
  })
})
