import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/utils/eventBus', () => ({
  default: { emit: vi.fn() }
}))

vi.mock('@/custom-component/common/ComponentConfig', () => ({
  CANVAS_MATERIAL: [
    {
      category: 'CanvasBoard',
      title: 'Canvas Board',
      span: 8,
      details: [{ title: 'Rect', value: 'rect', type: 'common', icon: 'rect-icon' }]
    }
  ]
}))

vi.mock('@/components/icon-custom/src/Icon.vue', () => ({
  default: { template: '<span><slot /></span>' }
}))

vi.mock('@/custom-component/de-decoration/Component.vue', () => ({
  default: { template: '<div class="de-decoration-stub">decoration</div>' }
}))

import CommonGroup from '../CommonGroup.vue'

const globalStubs = {
  ElRow: { template: '<div><slot /></div>' },
  ElCol: { template: '<div><slot /></div>' },
  ElScrollbar: {
    template: '<div><slot /></div>',
    methods: { setScrollTop: vi.fn() }
  }
}

describe('CommonGroup', () => {
  it('renders with default props', () => {
    const wrapper = shallowMount(CommonGroup, { global: { stubs: globalStubs } })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.group').exists()).toBe(true)
  })

  it('renders group list with category items', () => {
    const wrapper = shallowMount(CommonGroup, { global: { stubs: globalStubs } })
    const items = wrapper.findAll('.li-custom')
    expect(items.length).toBeGreaterThan(0)
  })

  it('has default curCategory as CanvasBoard', () => {
    const wrapper = shallowMount(CommonGroup, { global: { stubs: globalStubs } })
    const activeItems = wrapper.findAll('.li-custom-active')
    expect(activeItems.length).toBeGreaterThan(0)
  })

  it('renders group-left and group-right sections', () => {
    const wrapper = shallowMount(CommonGroup, { global: { stubs: globalStubs } })
    expect(wrapper.find('.group-left').exists()).toBe(true)
    expect(wrapper.find('.group-right').exists()).toBe(true)
  })
})
