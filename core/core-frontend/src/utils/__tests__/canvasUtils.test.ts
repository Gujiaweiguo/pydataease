import { beforeEach, describe, expect, it, vi } from 'vitest'

const { componentDataRef, canvasViewInfoRef, emitMock, getViewConfigMock, wsCacheGetMock } =
  vi.hoisted(() => ({
    componentDataRef: { value: [] as Array<Record<string, unknown>> },
    canvasViewInfoRef: { value: {} as Record<string, unknown> },
    emitMock: vi.fn(),
    getViewConfigMock: vi.fn(() => ({ title: 'View Title', render: 'render-view' })),
    wsCacheGetMock: vi.fn(() => 'test-version')
  }))

vi.mock('@/custom-component/component-list', () => ({
  default: [
    {
      component: 'Text',
      style: { borderWidth: 1 },
      propValue: {},
      commonBackground: { theme: 'base' }
    }
  ],
  ACTION_SELECTION: { name: 'action' },
  BASE_CAROUSEL: { autoplay: false },
  BASE_EVENTS: { jump: { type: '' } },
  COMMON_COMPONENT_BACKGROUND_DARK: { theme: 'dark' },
  COMMON_COMPONENT_BACKGROUND_LIGHT: { theme: 'light' },
  COMMON_TAB_TITLE_BACKGROUND: { color: 'tab' },
  MULTI_DIMENSIONAL: { enabled: false }
}))

vi.mock('@/utils/eventBus', () => ({
  default: { emit: emitMock }
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curOriginThemes: 'light',
    __refs: {
      inMobile: { value: false },
      dvInfo: { value: { type: 'dashboard' } },
      canvasStyleData: { value: { dashboard: {}, component: {} } },
      componentData: componentDataRef,
      canvasViewInfo: canvasViewInfoRef,
      appData: { value: {} }
    }
  })
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: { __refs: Record<string, unknown> }) => store.__refs
}))

vi.mock('@/api/visualization/dataVisualization', () => ({
  appCanvasNameCheck: vi.fn(),
  checkCanvasChange: vi.fn(),
  decompression: vi.fn(),
  dvNameCheck: vi.fn(),
  findById: vi.fn(),
  findCopyResource: vi.fn(),
  saveCanvas: vi.fn(),
  updateCanvas: vi.fn()
}))

vi.mock('@/api/visualization/linkage', () => ({
  getPanelAllLinkageInfo: vi.fn()
}))

vi.mock('@/api/visualization/linkJump', () => ({
  queryVisualizationJumpInfo: vi.fn()
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  getViewConfig: getViewConfigMock,
  SENIOR_STYLE_SETTING_LIGHT: { pagerSize: 12 }
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({})
}))

vi.mock('@/utils/utils', () => ({
  deepCopy: <T>(value: T) => structuredClone(value),
  nameTrim: (value: string) => value.trim()
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: { warning: vi.fn(), success: vi.fn() },
  ElMessageBox: { confirm: vi.fn() }
}))

vi.mock('@/views/visualized/data/dataset/form/util', () => ({
  guid: vi.fn(() => 'guid-1')
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

vi.mock('@/store/modules/appearance', () => ({
  useAppearanceStoreWithOut: () => ({})
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({ wsCache: { get: wsCacheGetMock } })
}))

vi.mock('@/utils/ModelUtil', () => ({
  isDesktop: vi.fn(() => false)
}))

vi.mock('@/Types', () => ({
  ShorthandMode: { Uniform: 'Uniform' }
}))

vi.mock('@/views/chart/components/js/formatter', () => ({
  formatterItem: { format: 'default' }
}))

import {
  chartTransObject2Str,
  chartTransStr2Object,
  checkAddHttp,
  filterEmptyFolderTree,
  findParentIdByChildIdRecursive,
  getMapElementIds,
  markTreeFolder,
  setIdValueTrans
} from '../canvasUtils'

type FolderNode = {
  children?: FolderNode[]
  disabled?: boolean
  id: string
  leaf: boolean
}

describe('canvasUtils', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    componentDataRef.value = []
    canvasViewInfoRef.value = {}
  })

  it('clones chart data only when the copy flag is enabled', () => {
    const source = { nested: { value: 1 } }

    const copied = chartTransStr2Object(source, 'Y')
    const original = chartTransStr2Object(source, undefined)

    expect(copied).toEqual(source)
    expect(copied).not.toBe(source)
    expect(original).toBe(source)
  })

  it('preserves or clones outgoing chart objects using the same copy semantics', () => {
    const source = { nested: { value: 2 } }

    expect(chartTransObject2Str(source, undefined)).toBe(source)
    expect(chartTransObject2Str(source, 'Y')).toEqual(source)
    expect(chartTransObject2Str(source, 'Y')).not.toBe(source)
  })

  it('normalizes urls by adding http only when needed', () => {
    expect(checkAddHttp('example.com')).toBe('http://example.com')
    expect(checkAddHttp('HTTPS://dataease.cn')).toBe('HTTPS://dataease.cn')
    expect(checkAddHttp('')).toBe('')
  })

  it('replaces bracketed display names with matching ids', () => {
    const content = 'sum([Sales]) / count([Orders])'
    const columns = [
      { name: 'Sales', id: 'field_sales' },
      { name: 'Orders', id: 'field_orders' }
    ]

    expect(setIdValueTrans('name', 'id', content, columns)).toBe(
      'sum(field_sales) / count(field_orders)'
    )
    expect(setIdValueTrans('name', 'id', '', columns)).toBe('')
  })

  it('marks folders as disabled recursively while keeping leaves enabled', () => {
    const tree: FolderNode[] = [
      {
        id: 'folder',
        leaf: false,
        children: [{ id: 'leaf', leaf: true }]
      }
    ]

    markTreeFolder(tree)

    expect(tree[0].disabled).toBe(true)
    expect(tree[0].children?.[0].disabled).toBe(false)
  })

  it('filters out empty folders but preserves non-empty folders and leaves', () => {
    const nodes: FolderNode[] = [
      { id: 'empty-folder', leaf: false, children: [] },
      {
        id: 'mixed-folder',
        leaf: false,
        children: [
          { id: 'nested-empty', leaf: false, children: [] },
          { id: 'nested-leaf', leaf: true }
        ]
      },
      { id: 'leaf-root', leaf: true }
    ]

    const result = filterEmptyFolderTree(nodes)

    expect(result.map(node => node.id)).toEqual(['mixed-folder', 'leaf-root'])
    expect(result[0].children?.map(node => node.id)).toEqual(['nested-leaf'])
  })

  it('finds the nearest parent id for nested child nodes', () => {
    const tree = [
      {
        id: 'root-1',
        children: [
          {
            id: 'branch-1',
            children: [{ id: 'leaf-1' }]
          }
        ]
      }
    ]

    expect(findParentIdByChildIdRecursive(tree, 'leaf-1')).toBe('branch-1')
    expect(findParentIdByChildIdRecursive(tree, 'missing')).toBeNull()
  })

  it('collects map element ids from root and tab-contained components', () => {
    const canvasDataPreview = [
      { id: 'map-root', innerType: 'map', component: 'UserView' },
      {
        id: 'tab-1',
        component: 'DeTabs',
        propValue: [
          {
            componentData: [
              { id: 'tab-map', innerType: 'heat-map' },
              { id: 'tab-text', innerType: 'text' }
            ]
          }
        ]
      }
    ]

    expect(getMapElementIds(canvasDataPreview)).toEqual(['map-root', 'tab-map'])
  })
})
