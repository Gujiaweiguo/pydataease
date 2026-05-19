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
    curComponent: { videoLinks: {}, id: 'test-id' },
    curActiveTabInner: {}
  })
}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))
vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: vi.fn() } })
}))
vi.mock('../../store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponent: { videoLinks: {}, id: 'test-id' },
    curActiveTabInner: {}
  })
}))
vi.mock('../../store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))
vi.mock('../../hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))
vi.mock('../../utils/utils', () => ({
  checkAddHttp: (url: string) => url,
  deepCopy: (obj: any) => JSON.parse(JSON.stringify(obj))
}))

import VideoLinks from '../VideoLinks.vue'

const globalStubs = {
  'el-row': { template: '<div class="el-row"><slot /></div>' },
  'el-form': { template: '<form><slot /></form>', props: ['size'] },
  'el-form-item': { template: '<div class="form-item"><slot /></div>', props: ['effect', 'label'] },
  'el-input': { template: '<input class="el-input" />', props: ['modelValue', 'effect'] },
  'el-switch': { template: '<div class="el-switch" />', props: ['modelValue', 'effect', 'size'] },
  'el-radio-group': {
    template: '<div class="radio-group"><slot /></div>',
    props: ['modelValue', 'effect']
  },
  'el-radio': { template: '<label><slot /></label>', props: ['effect', 'label'] }
}

const defaultProps = () => ({
  themes: 'dark',
  linkInfo: {
    videoType: 'web',
    web: { src: 'https://video.com', autoplay: false, loop: false }
  }
})

describe('de-video/VideoLinks.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(VideoLinks, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains a form element', () => {
    const wrapper = shallowMount(VideoLinks, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('contains an el-switch for autoplay', () => {
    const wrapper = shallowMount(VideoLinks, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.el-switch').exists()).toBe(true)
  })

  it('contains an el-input for video link', () => {
    const wrapper = shallowMount(VideoLinks, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.el-input').exists()).toBe(true)
  })
})
