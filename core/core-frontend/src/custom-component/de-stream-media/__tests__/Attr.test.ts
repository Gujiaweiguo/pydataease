import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponent: { streamMediaLinks: { src: 'rtmp://stream.com' } },
    mobileInPc: false
  })
}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))
vi.mock('@/custom-component/common/CommonAttr.vue', () => ({
  default: {
    name: 'CommonAttr',
    template: '<div class="common-attr-stub"><slot /></div>',
    props: ['themes', 'element']
  }
}))

import Attr from '../Attr.vue'

const globalStubs = {
  CommonAttr: {
    template: '<div class="common-attr"><slot /></div>',
    props: ['themes', 'element']
  },
  'el-collapse-item': {
    template: '<div class="el-collapse-item"><slot /></div>',
    props: ['effect', 'title', 'name']
  },
  StreamMediaLinks: {
    template: '<div class="stream-media-links" />',
    props: ['linkInfo', 'themes']
  }
}

describe('de-stream-media/Attr.vue', () => {
  it('renders the wrapper div with attr-list class', () => {
    const wrapper = shallowMount(Attr, { global: { stubs: globalStubs } })
    expect(wrapper.find('.attr-list').exists()).toBe(true)
  })

  it('renders CommonAttr child component', () => {
    const wrapper = shallowMount(Attr, { global: { stubs: globalStubs } })
    expect(wrapper.html()).toContain('common-attr')
  })

  it('accepts light themes prop', () => {
    const wrapper = shallowMount(Attr, {
      props: { themes: 'light' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.attr-list').exists()).toBe(true)
  })
})
