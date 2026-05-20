import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/utils/components', () => ({
  default: () => ({ template: '<div class="mock-component"></div>' })
}))

import ComponentHang from '../ComponentHang.vue'

describe('independent-hang/ComponentHang.vue', () => {
  const createProps = (overrides = {}) => ({
    hangComponentData: [],
    canvasViewInfo: {},
    scale: 100,
    ...overrides
  })

  it('renders the component', () => {
    const wrapper = shallowMount(ComponentHang, { props: createProps() })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the hang-main container', () => {
    const wrapper = shallowMount(ComponentHang, { props: createProps() })
    expect(wrapper.find('.hang-main').exists()).toBe(true)
  })

  it('accepts scale prop', () => {
    const wrapper = shallowMount(ComponentHang, {
      props: createProps({ scale: 200 })
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts hangComponentData with items', () => {
    const wrapper = shallowMount(ComponentHang, {
      props: createProps({
        hangComponentData: [{ component: 'VQuery', id: '1' }]
      })
    })
    expect(wrapper.exists()).toBe(true)
  })
})
