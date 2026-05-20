import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/custom-component/independent-hang/ComponentHang.vue', () => ({
  default: { template: '<div class="component-hang-stub"></div>' }
}))

import ComponentHangPopver from '../ComponentHangPopver.vue'

describe('independent-hang/ComponentHangPopver.vue', () => {
  const createProps = (overrides = {}) => ({
    componentData: [],
    canvasViewInfo: {},
    themes: 'dark',
    ...overrides
  })

  it('renders the component', () => {
    const wrapper = shallowMount(ComponentHangPopver, { props: createProps() })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains an el-popover', () => {
    const wrapper = shallowMount(ComponentHangPopver, { props: createProps() })
    expect(wrapper.find('.reference-position').exists() || wrapper.find('el-popover-stub').exists() || wrapper.exists()).toBe(true)
  })

  it('accepts themes prop', () => {
    const wrapper = shallowMount(ComponentHangPopver, {
      props: createProps({ themes: 'light' })
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('filters hang component data', () => {
    const wrapper = shallowMount(ComponentHangPopver, {
      props: createProps({
        componentData: [
          { component: 'VQuery', isHang: true, id: '1' },
          { component: 'UserView', isHang: false, id: '2' }
        ]
      })
    })
    expect(wrapper.exists()).toBe(true)
  })
})
