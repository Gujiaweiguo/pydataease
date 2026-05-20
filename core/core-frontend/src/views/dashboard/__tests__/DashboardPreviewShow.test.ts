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
    canvasDataInit: vi.fn(),
    initCurMultiplexingComponents: vi.fn(),
    componentData: [],
    canvasStyleData: {},
    canvasViewInfo: {},
    dvInfo: { value: { name: '', type: 'dashboard' } },
    canvasViewDataInfo: { value: {} },
    fullscreenFlag: false
  })
}))
vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({ getIsDataEaseBi: false, setArrowSide: vi.fn() })
}))
vi.mock('@/store/modules/user', () => ({
  useUserStoreWithOut: () => ({ getName: 'test' })
}))
vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn(() => ({ emitter: { emit: vi.fn(), on: vi.fn() } }))
}))
vi.mock('@/hooks/web/useMoveLine', () => ({
  useMoveLine: () => ({ width: { value: 280 }, node: { value: null } })
}))
vi.mock('@/utils/canvasUtils', () => ({
  initCanvasData: vi.fn(),
  initCanvasDataPrepare: vi.fn(),
  onInitReady: vi.fn(),
  getMapElementIds: vi.fn(() => [])
}))
vi.mock('@/utils/imgUtils', () => ({
  downloadCanvas2: vi.fn(),
  download2AppTemplate: vi.fn()
}))
vi.mock('@/api/visualization/dataVisualization', () => ({
  storeApi: vi.fn(),
  storeStatusApi: vi.fn(),
  exportLogApp: vi.fn(),
  exportLogImg: vi.fn(),
  exportLogPDF: vi.fn(),
  exportLogTemplate: vi.fn(),
  queryTreeApi: vi.fn()
}))
vi.mock('@/utils/utils', () => ({ deepCopy: vi.fn(v => v), getLocale: vi.fn(() => 'zh') }))
vi.mock('pinia', () => ({
  createPinia: vi.fn(() => ({})),
  storeToRefs: (store: any) => store,
  defineStore: vi.fn()
}))
vi.mock('@/store', () => ({ useAppStore: vi.fn(), usePermissionStore: vi.fn(), store: {} }))
vi.mock('vue-clipboard3', () => ({
  default: () => ({ copy: vi.fn() })
}))
vi.mock('@/views/share/share/ShareHandler.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/views/share/share/ShareTicket.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/views/share/share/option', () => ({
  ShareInfo: {},
  SHARE_BASE: '',
  shortcuts: []
}))
vi.mock('vant/es/nav-bar/style', () => ({}))
vi.mock('vant/es/sticky/style', () => ({}))
vi.mock('@/utils/style', () => ({
  groupSizeStyleAdaptor: vi.fn(),
  groupStyleRevert: vi.fn()
}))
vi.mock('@/views/chart/components/js/util', () => ({}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn()
  })
}))
vi.mock('@/utils/DeShortcutKey', () => ({}))
vi.mock('@/custom-component/v-text/Component.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/custom-component/component-list.ts', () => ({}))
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
vi.mock('@/views/common/DeResourceTree.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/views/common/DeResourceArrow.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/components/visualization/CanvasOptBar.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/components/data-visualization/canvas/DePreview.vue', () => ({
  default: { template: '<div />' }
}))
vi.mock('@/components/empty-background/src/EmptyBackground.vue', () => ({
  default: { template: '<div />' }
}))
vi.mock('@/components/de-app/AppExportForm.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/views/data-visualization/PreviewHead.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/store/modules/interactive', () => ({
  interactiveStoreWithOut: () => ({ setInteractive: vi.fn() })
}))

import DashboardPreviewShow from '../DashboardPreviewShow.vue'

describe('DashboardPreviewShow', () => {
  it('renders component', () => {
    const wrapper = shallowMount(DashboardPreviewShow, {
      props: { showPosition: 'preview', noClose: true, resourceTable: 'core' },
      global: {
        stubs: {
          'arrow-side': true,
          'el-aside': { template: '<div><slot /></div>' },
          'el-container': { template: '<div><slot /></div>' },
          'de-resource-tree': true,
          'preview-head': true,
          'de-preview': true,
          'canvas-opt-bar': true,
          'empty-background': true,
          'app-export-form': true,
          'el-button': true,
          'el-icon': { template: '<div><slot /></div>' },
          Icon: { template: '<div><slot /></div>' },
          icon_add_outlined: true,
          'arrow-left': true,
          'arrow-right': true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains dv-preview wrapper', () => {
    const wrapper = shallowMount(DashboardPreviewShow, {
      props: { showPosition: 'preview', noClose: true, resourceTable: 'core' },
      global: {
        stubs: {
          'arrow-side': true,
          'el-aside': { template: '<div><slot /></div>' },
          'el-container': { template: '<div><slot /></div>' },
          'de-resource-tree': true,
          'preview-head': true,
          'de-preview': true,
          'canvas-opt-bar': true,
          'empty-background': true,
          'app-export-form': true,
          'el-button': true,
          'el-icon': { template: '<div><slot /></div>' },
          Icon: { template: '<div><slot /></div>' },
          icon_add_outlined: true,
          'arrow-left': true,
          'arrow-right': true
        }
      }
    })
    expect(wrapper.find('.dv-preview').exists()).toBe(true)
  })
})
