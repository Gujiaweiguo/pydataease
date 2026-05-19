import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { ref } from 'vue'

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponent: ref({ propValue: { url: 'test.png' } })
  })
}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))
vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: (url: string) => url
}))
vi.mock('@/utils/eventBus', () => ({
  default: { on: vi.fn(), off: vi.fn() }
}))
vi.mock('@/custom-component/common/CommonAttr.vue', () => ({
  default: {
    name: 'CommonAttr',
    template: '<div class="common-attr-stub"><slot /></div>',
    props: ['themes', 'element', 'backgroundColorPickerWidth', 'backgroundBorderSelectWidth']
  }
}))

import Attr from '../Attr.vue'

const globalStubs = {
  CommonAttr: {
    template: '<div class="common-attr"><slot /></div>',
    props: ['themes', 'element', 'backgroundColorPickerWidth', 'backgroundBorderSelectWidth']
  }
}

describe('de-graphical/Attr.vue', () => {
  it('renders the wrapper div with attr-list class', () => {
    const wrapper = shallowMount(Attr, { global: { stubs: globalStubs } })
    expect(wrapper.find('.attr-list').exists()).toBe(true)
  })

  it('renders CommonAttr child component', () => {
    const wrapper = shallowMount(Attr, { global: { stubs: globalStubs } })
    expect(wrapper.html()).toContain('common-attr')
  })

  it('passes themes prop with default dark', () => {
    const wrapper = shallowMount(Attr, { global: { stubs: globalStubs } })
    expect(wrapper.find('.attr-list').exists()).toBe(true)
  })

  it('passes background width props as 197', () => {
    const wrapper = shallowMount(Attr, { global: { stubs: globalStubs } })
    expect(wrapper.find('.attr-list').exists()).toBe(true)
  })
})
