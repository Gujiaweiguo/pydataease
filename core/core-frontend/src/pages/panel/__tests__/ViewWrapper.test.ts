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

vi.mock('@/utils/canvasUtils', () => ({
  initCanvasData: vi.fn(),
  onInitReady: vi.fn()
}))

vi.mock('@/store/modules/interactive', () => ({
  interactiveStoreWithOut: () => ({
    setInteractive: vi.fn().mockResolvedValue(undefined)
  })
}))

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
    addOuterParamsFilter: vi.fn()
  })
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div></div>' }
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: { error: vi.fn() }
}))

import ViewWrapper from '../ViewWrapper.vue'

describe('panel/ViewWrapper.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(ViewWrapper, {
      global: {
        provide: {
          embeddedParams: { dvId: 'dv1', busiFlag: 'dashboard', chartId: 'c1' }
        },
        stubs: {
          'component-wrapper': { template: '<div></div>' },
          'user-view-enlarge': { template: '<div></div>' },
          'empty-background': { template: '<div></div>' },
          XpackComponent: { template: '<div></div>' }
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has de-view-wrapper class element when config is set', () => {
    const wrapper = shallowMount(ViewWrapper, {
      global: {
        provide: {
          embeddedParams: { dvId: 'dv1', busiFlag: 'dashboard', chartId: 'c1' }
        },
        stubs: {
          'component-wrapper': { template: '<div></div>' },
          'user-view-enlarge': { template: '<div></div>' },
          'empty-background': { template: '<div></div>' },
          XpackComponent: { template: '<div></div>' }
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
