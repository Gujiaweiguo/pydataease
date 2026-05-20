import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi, beforeEach } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn(() => ({ emitter: { emit: vi.fn(), on: vi.fn() } }))
}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    componentData: [],
    setComponentData: vi.fn(),
    setMobileInPc: vi.fn(),
    setCanvasStyle: vi.fn(),
    updateCurDvInfo: vi.fn(),
    setCanvasViewInfo: vi.fn()
  })
}))
vi.mock('@/utils/eventBus', () => ({ default: { emit: vi.fn(), on: vi.fn() } }))
vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div><slot /></div>' }
}))
vi.mock('@/utils/canvasUtils', () => ({
  findComponentById: vi.fn(),
  mobileViewStyleSwitch: vi.fn()
}))
vi.mock('@/utils/utils', () => ({ deepCopy: vi.fn(v => v), getLocale: vi.fn(() => 'zh') }))
vi.mock('pinia', () => ({
  createPinia: vi.fn(() => ({})),
  storeToRefs: vi.fn(),
  defineStore: vi.fn()
}))
vi.mock('@/store', () => ({ useAppStore: vi.fn(), usePermissionStore: vi.fn(), store: {} }))
vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({ resourceId: null, pid: null, opt: null, baseUrl: '', token: '' })
}))
vi.mock('@/store/modules/appearance', () => ({
  useAppearanceStoreWithOut: () => ({})
}))
vi.mock('@/views/chart/components/js/util', () => ({}))
vi.mock('@/views/chart/components/js/formatter', () => ({}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: [],
  DEFAULT_TITLE_STYLE_LIGHT: {},
  DEFAULT_COLOR_CASE_LIGHT: {},
  COMMON_COMPONENT_BACKGROUND_LIGHT: {},
  DEFAULT_TITLE_STYLE_DARK: {},
  DEFAULT_COLOR_CASE_DARK: {},
  COMMON_COMPONENT_BACKGROUND_DARK: {}
}))
vi.mock('@/views/chart/components/editor/util/dataVisualization', () => ({
  PANEL_CHART_INFO_LIGHT: { chartTitle: {}, chartColor: {}, chartCommonStyle: {} },
  PANEL_CHART_INFO_DARK: { chartTitle: {}, chartColor: {}, chartCommonStyle: {} }
}))
vi.mock('@/custom-component/component-list.ts', () => ({}))
vi.mock('@/views/mobile/panel/MobileInPc.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/views/canvas/DeCanvas.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))

import MobilePanelIndex from '../index.vue'

describe('MobilePanelIndex', () => {
  beforeEach(() => {
    // Prevent the component's postMessage from triggering its own handler
    vi.spyOn(window.parent, 'postMessage').mockImplementation(() => {
      /* noop */
    })
  })

  it('renders component', () => {
    const wrapper = shallowMount(MobilePanelIndex, {
      global: { stubs: { 'de-preview-mobile': true, 'xpack-component': true } }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains panel-mobile div wrapper', () => {
    const wrapper = shallowMount(MobilePanelIndex, {
      global: { stubs: { 'de-preview-mobile': true, 'xpack-component': true } }
    })
    expect(wrapper.find('.panel-mobile').exists()).toBe(true)
  })
})
