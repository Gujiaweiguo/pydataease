import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const {
  chartGetChartViewMock,
  checkFilterRemoveMock,
  checkIsSameDsMock,
  emitMock,
  messageWarningMock,
  viewFieldTimeTransMock
} = vi.hoisted(() => ({
  chartGetChartViewMock: vi.fn(),
  checkFilterRemoveMock: vi.fn(),
  checkIsSameDsMock: vi.fn(),
  emitMock: vi.fn(),
  messageWarningMock: vi.fn(),
  viewFieldTimeTransMock: vi.fn()
}))

vi.mock('@/utils/utils', () => ({
  deepCopy: <T>(value: T) => JSON.parse(JSON.stringify(value))
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  BASE_VIEW_CONFIG: {
    customStyle: {
      text: {}
    },
    customAttr: {}
  },
  DEFAULT_INDICATOR_NAME_STYLE: { fontSize: 18 },
  DEFAULT_INDICATOR_STYLE: { color: '#000000' },
  SENIOR_STYLE_SETTING_LIGHT: { enabled: true }
}))

vi.mock('@/views/chart/components/editor/util/dataVisualization', () => ({
  DEFAULT_CANVAS_STYLE_DATA_DARK: { theme: 'dark', scale: 100, component: {} },
  DEFAULT_CANVAS_STYLE_DATA_LIGHT: { theme: 'light', scale: 80, component: {} },
  DEFAULT_CANVAS_STYLE_DATA_SCREEN_DARK: { theme: 'screen-dark', scale: 90, component: {} }
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({
    emitter: {
      emit: emitMock
    }
  })
}))

vi.mock('@/views/chart/components/js/panel', () => ({
  default: {
    getChartView: chartGetChartViewMock
  }
}))

vi.mock('@/custom-component/component-list', () => ({
  COMMON_COMPONENT_BACKGROUND_DARK: {},
  COMMON_COMPONENT_BACKGROUND_LIGHT: {},
  defaultStyleValue: {},
  findBaseDeFaultAttr: vi.fn()
}))

vi.mock('@/utils/viewUtils', () => ({
  checkIsSameDs: checkIsSameDsMock,
  viewFieldTimeTrans: viewFieldTimeTransMock
}))

vi.mock('@/store/modules/appearance', () => ({
  useAppearanceStoreWithOut: () => ({
    fontList: []
  })
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: {
    warning: messageWarningMock
  }
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => `translated:${key}`
  })
}))

vi.mock('@/utils/componentUtils', () => ({
  filterEnumParams: vi.fn(),
  filterEnumParamsReduce: vi.fn(),
  filterParamsOptions: vi.fn()
}))

vi.mock('@/views/chart/components/js/formatter', () => ({
  formatterItem: { format: 'default' }
}))

vi.mock('@/custom-component/v-query/QueryUtils', () => ({
  checkFilterRemove: checkFilterRemoveMock
}))

import { dvMainStore } from '../dvMain'

describe('dvMainStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('starts with the expected initial state', () => {
    const store = dvMainStore()

    expect(store.$state).toMatchObject({
      editMode: 'preview',
      fullscreenFlag: false,
      canvasState: { curPointArea: 'base' },
      pcMatrixCount: { x: 72, y: 36 },
      curOriginThemes: 'light',
      canvasStyleData: { theme: 'dark', scale: 100, backgroundColor: null }
    })
  })

  it('stores and clears the last hidden component', () => {
    const store = dvMainStore()
    const component = { id: 'hidden-1' }

    store.setLastHiddenComponent(component)
    expect(store.lastHiddenComponent).toEqual([component])

    store.setLastHiddenComponent()
    expect(store.lastHiddenComponent).toEqual([])
  })

  it('fills missing canvas style defaults', () => {
    const store = dvMainStore()

    store.setCanvasStyle({
      scale: 66,
      component: {
        customFlag: true
      }
    } as any)

    expect(store.canvasStyleData).toMatchObject({
      scale: 66,
      component: {
        customFlag: true,
        seniorStyleSetting: { enabled: true },
        formatterItem: { format: 'default' }
      }
    })
  })

  it('clears the selected component state and emits mobile change events when deselecting', () => {
    const store = dvMainStore()
    const oldComponent = {
      id: 'old-component',
      canvasId: 'group-1-child',
      editing: true,
      resizing: true,
      dragging: true,
      canvasActive: true
    }
    store.mobileInPc = true
    store.curComponent = oldComponent as any
    store.componentData = [
      { id: 'group-1', canvasActive: true },
      { id: 'other-1', canvasActive: true }
    ] as any

    store.setCurComponent({ component: null, index: null })

    expect(oldComponent).toMatchObject({
      editing: false,
      resizing: false,
      dragging: false,
      canvasActive: false
    })
    expect(store.componentData).toEqual([
      expect.objectContaining({ id: 'group-1', canvasActive: false }),
      expect.objectContaining({ id: 'other-1', canvasActive: true })
    ])
    expect(emitMock).toHaveBeenCalledWith('curComponentChange', {
      type: 'curComponentChange',
      value: null
    })
  })

  it('updates the active area when selecting a categorized component', () => {
    const store = dvMainStore()
    const nextComponent = {
      id: 'next-component',
      component: 'Text',
      canvasId: 'canvas-main',
      category: 'hidden',
      style: {}
    }

    store.componentData = [{ id: 'other-1', canvasActive: true }] as any

    store.setCurComponent({ component: nextComponent as any, index: 2 })

    expect(store.curComponent).toMatchObject({ id: 'next-component', category: 'hidden' })
    expect(store.curComponentIndex).toBe(2)
    expect(store.canvasState.curPointArea).toBe('hidden')
    expect(nextComponent).toMatchObject({
      editing: false
    })
  })

  it('filters empty component entries recursively', () => {
    const store = dvMainStore()

    store.setComponentData([
      null,
      {
        id: 'group-1',
        component: 'Group',
        propValue: [null, { id: 'group-child', component: 'Text' }]
      },
      {
        id: 'tabs-1',
        component: 'DeTabs',
        propValue: [{ name: 'tab-a', componentData: [null, { id: 'tab-child', component: 'Text' }] }]
      }
    ] as any)

    expect(store.componentData).toHaveLength(2)
    expect(store.componentData[0].propValue).toEqual([{ id: 'group-child', component: 'Text' }])
    expect(store.componentData[1].propValue[0].componentData).toEqual([
      { id: 'tab-child', component: 'Text' }
    ])
  })

  it('rounds dashboard component dimensions and prevents negative top values', () => {
    const store = dvMainStore()

    store.dvInfo.type = 'dashboard'
    store.curComponent = {
      component: 'Text',
      style: {
        top: 0,
        left: 0,
        width: 10,
        height: 10,
        rotate: 0
      }
    } as any

    store.setShapeStyle({ top: -1.4, left: 10.6, width: 20.4, height: 30.6, rotate: 44.7 })

    expect(store.curComponent.style).toMatchObject({
      top: 0,
      left: 11,
      width: 20,
      height: 31,
      rotate: 45
    })
  })

  it('toggles the hidden list and clears batch state for dashboards', () => {
    const store = dvMainStore()

    store.dvInfo.type = 'dashboard'
    store.hiddenListStatus = false
    store.batchOptStatus = true
    store.curBatchOptComponents = ['view-1']
    store.mixProperties = ['prop-a'] as any
    store.mixPropertiesInner = { key: 'value' }
    store.batchOptComponentType = 'UserView'
    store.batchOptComponentInfo = { id: 'view-1' } as any
    store.batchOptComponents = { 'view-1': { value: 'chart' } } as any
    store.changeProperties = { customStyle: { a: 1 }, customAttr: { b: 2 } }

    store.setHiddenListStatus()

    expect(store.hiddenListStatus).toBe(true)
    expect(store.batchOptStatus).toBe(false)
    expect(store.curBatchOptComponents).toEqual([])
    expect(store.mixProperties).toEqual([])
    expect(store.mixPropertiesInner).toEqual({})
    expect(store.batchOptComponentType).toBeNull()
    expect(store.batchOptComponentInfo).toBeNull()
    expect(store.batchOptComponents).toEqual({})
    expect(store.changeProperties).toEqual({ customStyle: {}, customAttr: {} })
  })

  it('initializes dashboard metadata and theme defaults', () => {
    const store = dvMainStore()

    store.createInit('dashboard', 'dv-1', 'folder-1', { text: 'wm' }, undefined)

    expect(store.dvInfo).toMatchObject({
      dataState: 'prepare',
      id: 'dv-1',
      pid: 'folder-1',
      type: 'dashboard',
      name: 'translated:visualization.new_dashboard',
      watermarkInfo: { text: 'wm' },
      status: 0,
      contentId: '0',
      weight: 9
    })
    expect(store.canvasStyleData).toEqual({ theme: 'light', scale: 80, component: {} })
    expect(store.componentData).toEqual([])
    expect(store.canvasViewInfo).toEqual({})
  })

  it('preserves existing calParams values when view data details refresh', () => {
    const store = dvMainStore()

    store.canvasViewInfo = {
      'view-1': {
        calParams: [{ id: 'city', value: 'Shanghai' }]
      }
    } as any

    store.setViewDataDetails('view-1', {
      data: { rows: [1, 2, 3] },
      calParams: [
        { id: 'city', value: 'Beijing' },
        { id: 'status', value: 'active' }
      ]
    })

    expect(store.getViewDataDetails('view-1')).toEqual({ rows: [1, 2, 3] })
    expect(store.canvasViewInfo['view-1'].calParams).toEqual([
      { id: 'city', value: 'Shanghai' },
      { id: 'status', value: 'active' }
    ])
  })
})
