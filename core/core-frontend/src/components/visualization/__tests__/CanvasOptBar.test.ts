import { ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  clearPanelLinkageInfo: vi.fn(),
  emitSpy: vi.fn(),
  mobileInPc: false,
  dvInfoType: 'dashboard',
  fullscreenFlag: false
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: () => ({
    fullscreenFlag: ref(mocks.fullscreenFlag)
  })
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    clearPanelLinkageInfo: mocks.clearPanelLinkageInfo,
    mobileInPc: mocks.mobileInPc,
    dvInfo: { type: mocks.dvInfoType }
  })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: mocks.emitSpy } })
}))

vi.mock('@/utils/canvasUtils', () => ({
  isMainCanvas: (id: string) => id === 'canvas-main'
}))

vi.mock('@/utils/utils', () => ({
  isMobile: () => false
}))

vi.mock('@/config/axios', () => ({}))

import CanvasOptBar from '../CanvasOptBar.vue'

const globalStubs = {
  ElButton: { template: '<button><slot /></button>', props: ['type'] },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>' },
  'dv-bar-unLinkage': { template: '<svg />' }
}

const globalMocks = {
  stubs: globalStubs,
  mocks: { $t: (k: string) => k }
}

describe('CanvasOptBar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.mobileInPc = false
    mocks.fullscreenFlag = false
    mocks.dvInfoType = 'dashboard'
  })

  it('does not render when no linkage filters exist', () => {
    const wrapper = shallowMount(CanvasOptBar, {
      props: {
        canvasStyleData: {},
        componentData: [
          { component: 'UserView', linkageFilters: [] }
        ]
      },
      global: globalMocks
    })
    expect(wrapper.find('div').exists()).toBe(false)
  })

  it('renders when linkage filters exist on a UserView component', () => {
    const wrapper = shallowMount(CanvasOptBar, {
      props: {
        canvasStyleData: {},
        componentData: [
          { component: 'UserView', linkageFilters: [{ fieldId: 'f1' }] }
        ]
      },
      global: globalMocks
    })
    expect(wrapper.find('div').exists()).toBe(true)
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('calls clearPanelLinkageInfo and emits event on clearAllLinkage click', async () => {
    const wrapper = shallowMount(CanvasOptBar, {
      props: {
        canvasStyleData: {},
        componentData: [
          { component: 'UserView', linkageFilters: [{ fieldId: 'f1' }] }
        ]
      },
      global: globalMocks
    })
    await wrapper.find('button').trigger('click')
    expect(mocks.clearPanelLinkageInfo).toHaveBeenCalled()
    expect(mocks.emitSpy).toHaveBeenCalledWith('clearPanelLinkage', { viewId: 'all' })
  })

  it('applies bar-main-preview-fixed class when dvPreviewMode is true', () => {
    mocks.dvInfoType = 'dataV'
    const wrapper = shallowMount(CanvasOptBar, {
      props: {
        canvasStyleData: {},
        componentData: [
          { component: 'UserView', linkageFilters: [{ fieldId: 'f1' }] }
        ],
        isFixed: true
      },
      global: globalMocks
    })
    expect(wrapper.find('.bar-main-preview-fixed').exists()).toBe(true)
  })

  it('does not render for non-main canvas', () => {
    const wrapper = shallowMount(CanvasOptBar, {
      props: {
        canvasStyleData: {},
        componentData: [
          { component: 'UserView', linkageFilters: [{ fieldId: 'f1' }] }
        ],
        canvasId: 'canvas-0-1'
      },
      global: globalMocks
    })
    expect(wrapper.find('div').exists()).toBe(false)
  })
})
