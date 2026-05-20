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
    setCurComponent: vi.fn(),
    setHiddenListStatus: vi.fn(),
    canvasDataInit: vi.fn(),
    setMobileInPc: vi.fn(),
    createInit: vi.fn(),
    setComponentData: vi.fn(),
    setCanvasStyle: vi.fn(),
    setCanvasViewInfo: vi.fn(),
    setAppDataInfo: vi.fn(),
    getAppDataInfo: vi.fn(),
    updateDvInfoCall: vi.fn(),
    componentData: [],
    canvasStyleData: { value: { component: { chartTitle: { color: '#000' } } } },
    canvasViewInfo: {},
    curComponent: null,
    dvInfo: { value: {} },
    editMode: 'edit',
    fullscreenFlag: false,
    batchOptStatus: false,
    hiddenListStatus: false,
    lastHiddenComponent: null
  })
}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    initSnapShot: vi.fn(),
    recordSnapshotCache: vi.fn(),
    snapshotPublish: vi.fn(),
    resetStyleChangeTimes: vi.fn()
  })
}))
vi.mock('@/store/modules/data-visualization/contextmenu', () => ({
  contextmenuStoreWithOut: () => ({ hideContextMenu: vi.fn() })
}))
vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({
    resourceId: null,
    pid: null,
    opt: null,
    createType: null,
    templateParams: null
  })
}))
vi.mock('@/store/modules/request', () => ({
  useRequestStoreWithOut: () => ({ loadingMap: {} })
}))
vi.mock('@/store/modules/permission', () => ({
  usePermissionStoreWithOut: () => ({ currentPath: '' })
}))
vi.mock('@/store/modules/interactive', () => ({
  interactiveStoreWithOut: () => ({ setInteractive: vi.fn() })
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
vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({ wsCache: { get: vi.fn(), delete: vi.fn(), set: vi.fn() } })
}))
vi.mock('@/hooks/web/useMoveLine', () => ({
  useMoveLine: () => ({ width: { value: 280 }, node: { value: null } })
}))
vi.mock('@/utils/canvasUtils', () => ({
  initCanvasData: vi.fn(),
  initCanvasDataPrepare: vi.fn(),
  decompressionPre: vi.fn(),
  onInitReady: vi.fn(),
  findComponentById: vi.fn(),
  canvasSave: vi.fn(),
  backCanvasData: vi.fn(),
  getMapElementIds: vi.fn(() => [])
}))
vi.mock('@/utils/CrossPermission', () => ({
  check: vi.fn(() => true),
  compareStorage: vi.fn(() => false)
}))
vi.mock('@/utils/utils', () => ({ deepCopy: vi.fn(v => v), getLocale: vi.fn(() => 'zh') }))
vi.mock('@/utils/imgUtils', () => ({
  downloadCanvas2: vi.fn(),
  download2AppTemplate: vi.fn(),
  imgUrlTrans: vi.fn(v => v)
}))
vi.mock('@/utils/eventBus', () => ({ default: { emit: vi.fn(), on: vi.fn() } }))
vi.mock('@/utils/attr', () => ({ positionData: [] }))
vi.mock('@/utils/style', () => ({
  groupSizeStyleAdaptor: vi.fn(),
  groupStyleRevert: vi.fn()
}))
vi.mock('pinia', async importOriginal => {
  const actual = await importOriginal<typeof import('pinia')>()
  return {
    ...actual,
    storeToRefs: (store: any) => store
  }
})
vi.mock('@/store', () => ({ useAppStore: vi.fn(), usePermissionStore: vi.fn(), store: {} }))
vi.mock('@/store/modules/map', () => ({
  useMapStore: vi.fn(() => ({}))
}))
vi.mock('@/store/modules/appearance', () => ({
  useAppearanceStoreWithOut: () => ({})
}))
vi.mock('@/store/modules/link', () => ({
  useLinkStore: vi.fn(() => ({}))
}))
vi.mock('@/store/modules/data-visualization/compose', () => ({
  composeStoreWithOut: () => ({})
}))
vi.mock('@/utils/DeShortcutKey', () => ({}))
vi.mock('@/views/chart/components/js/util', () => ({}))
vi.mock('@/views/chart/components/js/formatter', () => ({}))
vi.mock('@/utils/style', () => ({
  groupSizeStyleAdaptor: vi.fn(),
  groupStyleRevert: vi.fn()
}))
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
vi.mock('@/components/visualization/CanvasOptBar.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/components/dashboard/DbToolbar.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/components/dashboard/DbCanvasAttr.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/views/chart/components/editor/index.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/views/chart/components/editor/editor-style/ChartStyleBatchSet.vue', () => ({
  default: { template: '<div />' }
}))
vi.mock('@/views/chart/components/js/panel/common/common_antv', () => ({}))
vi.mock('@/views/chart/components/js/panel/common/common_table', () => ({}))
vi.mock('@/views/chart/components/js/util', () => ({}))
vi.mock('@/views/chart/components/js/formatter', () => ({}))
vi.mock('@/views/chart/components/js/panel/types/impl/g2plot', () => ({}))
vi.mock('@/views/chart/components/js/panel/types/impl/s2', () => ({}))
vi.mock('@/views/chart/components/js/panel/types/impl/l7', () => ({}))
vi.mock('@antv/g2', () => ({}))
vi.mock('@antv/g2plot', () => ({}))
vi.mock('@antv/s2', () => ({ SpreadSheet: {} }))
vi.mock('@/views/chart/components/js/panel/index', () => ({}))
vi.mock('@/views/chart/components/js/panel/common', () => ({}))
vi.mock('@/custom-component/de-tabs/Component.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/custom-component/de-tabs/TabBackground.vue', () => ({
  default: { template: '<div />' }
}))
vi.mock('@/custom-component/v-query/index.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/custom-component/Group.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/custom-component/DeStreaming.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/custom-component/Picture.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/custom-component/CanvasIcon.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/custom-component/DeRuler.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/custom-component/de-screen/Component.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/views/canvas/DeCanvas.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/components/visualization/DvSidebar.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/components/visualization/CanvasCacheDialog.vue', () => ({
  default: { template: '<div />' }
}))
vi.mock('@/components/dashboard/DashboardHiddenComponent.vue', () => ({
  default: { template: '<div />' }
}))
vi.mock('@/views/sqlbot/assistant.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/views/common/ComponentStyleEditor.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/views/common/DeResourceArrow.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/components/empty-background/src/EmptyBackground.vue', () => ({
  default: { template: '<div />' }
}))
vi.mock('@/components/de-app/AppExportForm.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/views/data-visualization/PreviewHead.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/custom-component/ImgViewDialog.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/pages/panel/DashboardPreview.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/custom-component/v-query/VanPopupSelect.vue', () => ({
  default: { template: '<div />' }
}))
vi.mock('@/custom-component/v-query/Time.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/components/visualization/ComponentEditBar.vue', () => ({
  default: { template: '<div />' }
}))
vi.mock('@/components/data-visualization/canvas/ContextMenuDetails.vue', () => ({
  default: { template: '<div />' }
}))
vi.mock('@/components/visualization/ComponentSelector.vue', () => ({
  default: { template: '<div />' }
}))
vi.mock('@/custom-component/v-text/Component.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/components/data-visualization/canvas/DePreview.vue', () => ({
  default: { template: '<div />' }
}))
vi.mock('@/utils/eventBus', () => ({ default: { emit: vi.fn(), on: vi.fn() } }))
vi.mock('@/utils/attr', () => ({ positionData: [] }))
vi.mock('@/utils/style', () => ({
  groupSizeStyleAdaptor: vi.fn(),
  groupStyleRevert: vi.fn()
}))
vi.mock('@/api/dataset', () => ({ getDatasetTree: vi.fn(() => Promise.resolve([])) }))
vi.mock('@/api/visualization/dataVisualization', () => ({
  storeApi: vi.fn(() => Promise.resolve()),
  storeStatusApi: vi.fn(() => Promise.resolve({ data: false })),
  recoverToPublished: vi.fn(() => Promise.resolve()),
  exportLogApp: vi.fn(),
  exportLogImg: vi.fn(),
  exportLogPDF: vi.fn(),
  exportLogTemplate: vi.fn()
}))
vi.mock('@/api/watermark', () => ({ watermarkFind: vi.fn(() => Promise.resolve({ data: {} })) }))
vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div><slot /></div>' }
}))
vi.mock('@/router', () => ({
  default: { currentRoute: { value: { query: {} } } }
}))
vi.mock('pinia', () => ({
  storeToRefs: (store: any) => store
}))
vi.mock('lodash-es', () => ({
  cloneDeep: vi.fn(v => v),
  debounce: vi.fn(fn => fn)
}))
vi.mock('js-base64', () => ({ Base64: { decode: vi.fn(v => v) } }))

import DashboardIndex from '../index.vue'

describe('DashboardIndex', () => {
  it('renders component', () => {
    const wrapper = shallowMount(DashboardIndex, {
      global: {
        stubs: {
          'db-toolbar': true,
          'el-container': { template: '<div><slot /></div>' },
          'el-aside': { template: '<div><slot /></div>' },
          'de-canvas': true,
          'dv-sidebar': { template: '<div><slot /></div>' },
          'view-editor': true,
          'db-canvas-attr': true,
          'chart-style-batch-set': true,
          'mobile-config-panel': true,
          'xpack-component': true,
          'canvas-cache-dialog': true,
          'dashboard-hidden-component': true,
          'sql-assistant': true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
