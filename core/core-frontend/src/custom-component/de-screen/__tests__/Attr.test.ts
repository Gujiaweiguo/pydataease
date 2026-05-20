import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponent: { id: 'test-id', propValue: '' },
    editMode: 'preview'
  })
}))

vi.mock('pinia', () => ({
  storeToRefs: (store: any) => ({
    curComponent: { value: store.curComponent },
    editMode: { value: store.editMode }
  }),
  defineStore: vi.fn()
}))

vi.mock('@/custom-component/common/CommonAttr.vue', () => ({
  default: { template: '<div class="common-attr"><slot /></div>' }
}))

import Attr from '../Attr.vue'

const mountComponent = () =>
  shallowMount(Attr, {
    props: { themes: 'dark' },
    global: {
      mocks: { $t: (key: string) => key }
    }
  })

describe('de-screen/Attr', () => {
  it('renders the root container', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.attr-list').exists()).toBe(true)
  })

  it('accepts themes prop with default dark', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('themes')).toBe('dark')
  })

  it('accepts themes prop with light', () => {
    const wrapper = shallowMount(Attr, {
      props: { themes: 'light' },
      global: { mocks: { $t: (key: string) => key } }
    })
    expect(wrapper.props('themes')).toBe('light')
  })
})
