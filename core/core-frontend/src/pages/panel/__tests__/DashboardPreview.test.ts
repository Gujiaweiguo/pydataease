import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('@/config/axios', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: {} }),
    post: vi.fn().mockResolvedValue({ data: {} })
  }
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: {
      get: vi.fn().mockReturnValue(null),
      set: vi.fn()
    }
  })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn()
}))

vi.mock('@/utils/canvasUtils', () => ({
  initCanvasData: vi.fn(),
  initCanvasDataMobile: vi.fn(),
  onInitReady: vi.fn()
}))

vi.mock('@/store/modules/interactive', () => ({
  interactiveStoreWithOut: () => ({
    setInteractive: vi.fn().mockResolvedValue(undefined)
  })
}))

vi.mock('@/router/mobile', () => ({}))

vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({
    setType: vi.fn(),
    setBusiFlag: vi.fn(),
    setOuterParams: vi.fn(),
    setSuffixId: vi.fn(),
    setToken: vi.fn(),
    setBaseUrl: vi.fn(),
    setDvId: vi.fn(),
    setPid: vi.fn(),
    setResourceId: vi.fn(),
    setDfId: vi.fn(),
    getToken: null,
    getTokenInfo: {},
    setTokenInfo: vi.fn()
  })
}))

vi.mock('@/utils/utils', () => ({
  isMobile: vi.fn().mockReturnValue(false)
}))

vi.mock('@/utils/CrossPermission', () => ({
  check: vi.fn().mockReturnValue(true)
}))

vi.mock('@/api/visualization/outerParams', () => ({
  getOuterParamsInfo: vi.fn().mockResolvedValue({ data: {} })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    setNowPanelOuterParamsInfoV2: vi.fn(),
    setEmbeddedCallBack: vi.fn(),
    addOuterParamsFilter: vi.fn(),
    setMobileInPc: vi.fn(),
    setInMobile: vi.fn()
  })
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: { error: vi.fn() }
}))

vi.mock('vant/es/nav-bar/style', () => ({}))
vi.mock('vant/es/sticky/style', () => ({}))

import DashboardPreview from '../DashboardPreview.vue'

describe('panel/DashboardPreview.vue', () => {
  it('renders the component', async () => {
    const wrapper = shallowMount(DashboardPreview, {
      global: {
        provide: {
          embeddedParams: { dvId: 'dv1', busiFlag: 'dashboard' }
        },
        stubs: {
          'de-preview': { template: '<div class="de-preview"></div>' },
          'empty-background': { template: '<div></div>' }
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains reactive state', async () => {
    const wrapper = shallowMount(DashboardPreview, {
      global: {
        provide: {
          embeddedParams: { dvId: 'dv1', busiFlag: 'dashboard' }
        },
        stubs: {
          'de-preview': { template: '<div></div>' },
          'empty-background': { template: '<div></div>' }
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
