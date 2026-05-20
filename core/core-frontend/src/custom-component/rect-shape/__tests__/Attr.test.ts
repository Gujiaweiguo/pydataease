import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponent: { id: 'test-id', propValue: '' }
  })
}))

vi.mock('pinia', () => ({
  storeToRefs: (store: any) => ({
    curComponent: { value: store.curComponent }
  }),
  defineStore: vi.fn()
}))

vi.mock('@/custom-component/common/CommonAttr.vue', () => ({
  default: { template: '<div class="common-attr"><slot /></div>' }
}))

import RectShapeAttr from '../Attr.vue'

describe('rect-shape/Attr', () => {
  it('renders the root container', () => {
    const wrapper = shallowMount(RectShapeAttr)
    expect(wrapper.find('.attr-list').exists()).toBe(true)
  })
})
