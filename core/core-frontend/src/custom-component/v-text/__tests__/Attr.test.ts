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

import VTextAttr from '../Attr.vue'

describe('v-text/Attr', () => {
  it('renders the root container', () => {
    const wrapper = shallowMount(VTextAttr, {
      props: { themes: 'dark' },
      global: { mocks: { $t: (key: string) => key } }
    })
    expect(wrapper.find('.attr-list').exists()).toBe(true)
  })

  it('accepts themes prop with default dark', () => {
    const wrapper = shallowMount(VTextAttr, {
      global: { mocks: { $t: (key: string) => key } }
    })
    expect(wrapper.props('themes')).toBe('dark')
  })

  it('accepts themes prop with light', () => {
    const wrapper = shallowMount(VTextAttr, {
      props: { themes: 'light' },
      global: { mocks: { $t: (key: string) => key } }
    })
    expect(wrapper.props('themes')).toBe('light')
  })
})
