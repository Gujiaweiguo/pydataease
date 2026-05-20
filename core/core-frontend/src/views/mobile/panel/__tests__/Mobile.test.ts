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
    setMobileInPc: vi.fn(),
    setInMobile: vi.fn(),
    componentData: []
  })
}))
vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn(() => ({ emitter: { emit: vi.fn(), on: vi.fn() } }))
}))
vi.mock('@/utils/canvasUtils', () => ({ initCanvasDataMobile: vi.fn() }))
vi.mock('vue-router_2', () => ({
  useRoute: () => ({ query: {} }),
  useRouter: () => ({ replace: vi.fn() })
}))
vi.mock('@/api/visualization/dataVisualization', () => ({
  storeApi: vi.fn(() => Promise.resolve()),
  storeStatusApi: vi.fn(() => Promise.resolve({ data: false }))
}))
vi.mock('@/utils/imgUtils', () => ({ downloadCanvas2: vi.fn() }))
vi.mock('@/utils/utils', () => ({ deepCopy: vi.fn(v => v), getLocale: vi.fn(() => 'zh') }))
vi.mock('pinia', () => ({
  createPinia: vi.fn(() => ({})),
  storeToRefs: (store: any) => ({
    canvasStyleData: { value: store.canvasStyleData || {} },
    dvInfo: { value: store.dvInfo || {} },
    mobileInPc: { value: false }
  }),
  defineStore: vi.fn()
}))
vi.mock('@/store', () => ({ useAppStore: vi.fn(), usePermissionStore: vi.fn(), store: {} }))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    initSnapShot: vi.fn(),
    recordSnapshotCache: vi.fn()
  })
}))
vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({ resourceId: null, pid: null, opt: null, baseUrl: '', token: '' })
}))
vi.mock('@/utils/translate', () => ({
  tPriorityGroup: vi.fn(),
  reverseColor: vi.fn()
}))
vi.mock('@/utils/style', () => ({
  groupSizeStyleAdaptor: vi.fn(),
  groupStyleRevert: vi.fn(),
  calcDVDayColor: vi.fn()
}))
vi.mock('@/views/chart/components/js/util', () => ({}))
vi.mock('@/custom-component/v-text/Component.vue', () => ({ template: '<div />' }))
vi.mock('@/custom-component/component-list.ts', () => ({
  initCanvasDataMobile: vi.fn()
}))
vi.mock('@/components/data-visualization/canvas/DePreview.vue', () => ({
  default: { template: '<div />' }
}))
vi.mock('vant/es/sticky', () => ({ default: { template: '<div><slot /></div>' } }))
vi.mock('vant/es/nav-bar', () => ({ default: { template: '<div />' } }))
vi.mock('vant/es/sticky/style', () => ({}))
vi.mock('vant/es/nav-bar/style', () => ({}))
vi.mock('@/components/visualization/CanvasOptBar.vue', () => ({ default: { template: '<div />' } }))

import Mobile from '../Mobile.vue'

describe('Mobile', () => {
  it('renders component', () => {
    const wrapper = shallowMount(Mobile, {
      global: {
        stubs: {
          'van-sticky': { template: '<div><slot /></div>' },
          'van-nav-bar': { template: '<div />' },
          'de-preview': true,
          'canvas-opt-bar': true,
          icon_replace_outlined: true,
          'el-icon': { template: '<div><slot /></div>' },
          icon: { template: '<div><slot /></div>' }
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains mobile layout wrapper', () => {
    const wrapper = shallowMount(Mobile, {
      global: {
        stubs: {
          'van-sticky': { template: '<div><slot /></div>' },
          'van-nav-bar': { template: '<div />' },
          'de-preview': true,
          'canvas-opt-bar': true,
          icon_replace_outlined: true,
          'el-icon': { template: '<div><slot /></div>' },
          icon: { template: '<div><slot /></div>' }
        }
      }
    })
    expect(wrapper.find('.dv-common-layout-mobile').exists()).toBe(true)
  })
})
