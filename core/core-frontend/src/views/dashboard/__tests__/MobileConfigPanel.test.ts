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
    setCurComponent: vi.fn(),
    setCurComponentMobileConfig: vi.fn(),
    componentData: { value: [] },
    canvasStyleData: { value: {} },
    canvasViewInfo: { value: {} },
    dvInfo: { value: { name: 'test', id: '1' } },
    initCurMultiplexingComponents: vi.fn()
  })
}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn(),
    recordSnapshotCacheToMobile: vi.fn(),
    resetStyleChangeTimes: vi.fn()
  })
}))
vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({ resourceId: null, pid: null, opt: null, baseUrl: '', token: '' })
}))
vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn(() => ({ emitter: { emit: vi.fn(), on: vi.fn() } }))
}))
vi.mock('@/utils/canvasUtils', () => ({
  canvasSave: vi.fn(),
  findComponentById: vi.fn(),
  backCanvasData: vi.fn()
}))
vi.mock('@/utils/utils', () => ({ deepCopy: vi.fn(v => v), getLocale: vi.fn(() => 'zh') }))
vi.mock('@/utils/imgUtils', () => ({ imgUrlTrans: vi.fn(v => v) }))
vi.mock('pinia', () => ({
  createPinia: vi.fn(() => ({})),
  storeToRefs: (store: any) => store,
  defineStore: vi.fn()
}))
vi.mock('@/store', () => ({ useAppStore: vi.fn(), usePermissionStore: vi.fn(), store: {} }))
vi.mock('lodash-es', () => ({
  cloneDeep: vi.fn(v => v),
  debounce: vi.fn(fn => fn)
}))
vi.mock('@/views/chart/components/js/util', () => ({}))
vi.mock('@/utils/style', () => ({
  groupSizeStyleAdaptor: vi.fn(),
  groupStyleRevert: vi.fn()
}))
vi.mock('@/store/modules/data-visualization/compose', () => ({
  composeStoreWithOut: () => ({})
}))
vi.mock('@/utils/DeShortcutKey', () => ({}))
vi.mock('@/store/modules/link', () => ({
  useLinkStore: vi.fn(() => ({}))
}))
vi.mock('@/store/modules/map', () => ({
  useMapStore: vi.fn(() => ({}))
}))
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
vi.mock('@/views/canvas/DeCanvas.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/views/common/DeResourceTree.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/components/visualization/CanvasOptBar.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/components/dashboard/DbToolbar.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/views/common/ComponentStyleEditor.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/custom-component/ImgViewDialog.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/components/data-visualization/canvas/ComponentWrapper.vue', () => ({
  default: { template: '<div />' }
}))
vi.mock('vant/es/nav-bar/style', () => ({}))
vi.mock('vant/es/sticky/style', () => ({}))

import MobileConfigPanel from '../MobileConfigPanel.vue'

describe('MobileConfigPanel', () => {
  it('renders component', () => {
    const wrapper = shallowMount(MobileConfigPanel, {
      global: {
        stubs: {
          'el-icon': { template: '<div><slot /></div>' },
          'el-switch': true,
          'el-tooltip': { template: '<div><slot /></div>' },
          'el-button': true,
          'el-tabs': { template: '<div><slot /></div>' },
          'el-tab-pane': { template: '<div><slot /></div>' },
          'mobile-background-selector': true,
          'component-style-editor': true,
          'component-wrapper': true,
          Icon: { template: '<div><slot /></div>' },
          icon_left_outlined: true,
          icon_pc_outlined: true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains mobile-config-panel wrapper', () => {
    const wrapper = shallowMount(MobileConfigPanel, {
      global: {
        stubs: {
          'el-icon': { template: '<div><slot /></div>' },
          'el-switch': true,
          'el-tooltip': { template: '<div><slot /></div>' },
          'el-button': true,
          'el-tabs': { template: '<div><slot /></div>' },
          'el-tab-pane': { template: '<div><slot /></div>' },
          'mobile-background-selector': true,
          'component-style-editor': true,
          'component-wrapper': true,
          Icon: { template: '<div><slot /></div>' },
          icon_left_outlined: true,
          icon_pc_outlined: true
        }
      }
    })
    expect(wrapper.find('.mobile-config-panel').exists()).toBe(true)
  })
})
