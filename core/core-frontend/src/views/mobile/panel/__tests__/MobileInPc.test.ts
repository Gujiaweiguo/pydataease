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
    componentData: [],
    canvasStyleData: {},
    canvasViewInfo: {}
  })
}))
vi.mock('pinia', () => ({
  createPinia: vi.fn(() => ({})),
  storeToRefs: (store: any) => ({
    componentData: { value: store.componentData },
    canvasStyleData: { value: store.canvasStyleData },
    canvasViewInfo: { value: store.canvasViewInfo }
  }),
  defineStore: vi.fn()
}))
vi.mock('@/utils/utils', () => ({ deepCopy: vi.fn(v => v), getLocale: vi.fn(() => 'zh') }))
vi.mock('@/store', () => ({ useAppStore: vi.fn(), usePermissionStore: vi.fn(), store: {} }))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn()
  })
}))
vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({ resourceId: null, pid: null, opt: null, baseUrl: '', token: '' })
}))
vi.mock('@/utils/canvasUtils', () => ({}))
vi.mock('@/views/chart/components/js/util', () => ({}))
vi.mock('@/utils/style', () => ({
  groupSizeStyleAdaptor: vi.fn(),
  groupStyleRevert: vi.fn()
}))
vi.mock('@/views/canvas/DeCanvas.vue', () => ({ default: { template: '<div />' } }))

import MobileInPc from '../MobileInPc.vue'

describe('MobileInPc', () => {
  it('renders component', () => {
    const wrapper = shallowMount(MobileInPc, {
      global: { stubs: { 'de-canvas': true } }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains mobile layout wrapper', () => {
    const wrapper = shallowMount(MobileInPc, {
      global: { stubs: { 'de-canvas': true } }
    })
    expect(wrapper.find('.dv-common-layout-mobile').exists()).toBe(true)
  })
})
