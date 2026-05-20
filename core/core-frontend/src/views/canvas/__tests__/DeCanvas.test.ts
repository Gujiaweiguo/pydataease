import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/store', () => ({ store: {} }))
vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  storeToRefs: vi.fn(() => ({})),
  createPinia: vi.fn()
}))

vi.mock('@/custom-component/component-list', () => ({
  findNewComponentFromList: vi.fn(() => ({ id: 'comp-1' }))
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    addComponent: vi.fn(),
    setClickComponentStatus: vi.fn(),
    setInEditorStatus: vi.fn(),
    setCurComponent: vi.fn(),
    setDataPrepareState: vi.fn(),
    setBashMatrixInfo: vi.fn(),
    setCanvasStyleScale: vi.fn(),
    mainScrollTop: 0,
    pcMatrixCount: { x: 24, y: 32 },
    curOriginThemes: 'light',
    mobileInPc: false
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn(),
    recordSnapshotCacheWithPositionChange: vi.fn()
  })
}))

vi.mock('../../utils/eventBus', () => ({
  default: {
    on: vi.fn(),
    off: vi.fn(),
    emit: vi.fn()
  }
}))

vi.mock('element-resize-detector', () => ({
  default: () => ({
    listenTo: vi.fn(),
    uninstall: vi.fn()
  })
}))

vi.mock('@/utils/style', () => ({
  getCanvasStyle: vi.fn(() => ({})),
  syncShapeItemStyle: vi.fn()
}))

vi.mock('@/utils/canvasStyle', () => ({
  adaptCurThemeCommonStyle: vi.fn()
}))

vi.mock('@/components/data-visualization/canvas/CanvasCore.vue', () => ({
  default: { template: '<div class="canvas-core-stub" />' }
}))

vi.mock('@/utils/canvasUtils', () => ({
  isMainCanvas: vi.fn(() => true),
  isDashboard: vi.fn(() => true)
}))

vi.mock('@/views/visualized/data/dataset/form/util.js', () => ({
  guid: vi.fn(() => 'test-guid')
}))

describe('DeCanvas', () => {
  it('renders without errors', async () => {
    const DeCanvas = (await import('../DeCanvas.vue')).default
    const wrapper = shallowMount(DeCanvas, {
      props: {
        canvasStyleData: { width: 1920, height: 1080 },
        componentData: [],
        canvasViewInfo: {},
        canvasId: 'canvas-main'
      },
      global: {
        stubs: {
          'canvas-opt-bar': { template: '<div class="opt-bar-stub" />' },
          'canvas-core': { template: '<div class="canvas-core-stub" />' }
        }
      }
    })
    expect(wrapper.find('.content').exists()).toBe(true)
  })

  it('accepts required props', async () => {
    const DeCanvas = (await import('../DeCanvas.vue')).default
    const wrapper = shallowMount(DeCanvas, {
      props: {
        canvasStyleData: { width: 1920, height: 1080 },
        componentData: [{ id: '1' }],
        canvasViewInfo: { view1: {} },
        canvasId: 'test-canvas'
      },
      global: {
        stubs: {
          'canvas-opt-bar': { template: '<div />' },
          'canvas-core': { template: '<div />' }
        }
      }
    })
    expect(wrapper.props('canvasId')).toBe('test-canvas')
    expect(wrapper.props('componentData')).toEqual([{ id: '1' }])
  })
})
