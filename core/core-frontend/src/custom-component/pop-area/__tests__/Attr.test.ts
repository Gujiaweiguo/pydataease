import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponent: null
  })
}))
vi.mock('pinia', () => ({
  storeToRefs: (store: any) => ({ curComponent: { value: store.curComponent } })
}))
vi.mock('@/custom-component/common/CommonAttr.vue', () => ({
  default: { template: '<div class="common-attr-stub"><slot /></div>' }
}))

import Attr from '../Attr.vue'

describe('pop-area/Attr.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(Attr)
    expect(wrapper.exists()).toBe(true)
  })

  it('renders attr-list container', () => {
    const wrapper = shallowMount(Attr)
    expect(wrapper.find('.attr-list').exists()).toBe(true)
  })

  it('contains CommonAttr component', () => {
    const wrapper = shallowMount(Attr)
    expect(
      wrapper.findComponent({ name: 'CommonAttr' }).exists() ||
        wrapper.find('.common-attr-stub').exists()
    ).toBe(true)
  })
})
