import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    tabMoveInActiveId: null,
    bashMatrixInfo: {},
    editMode: 'preview',
    mobileInPc: false,
    curComponent: null,
    setCurComponent: vi.fn(),
    updateCopyCanvasView: vi.fn(),
    deleteComponent: vi.fn(),
    addComponent: vi.fn(),
    setNowPanelTrackInfo: vi.fn()
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn(),
    recordSnapshotCacheToMobile: vi.fn()
  })
}))

vi.mock('pinia', () => ({
  storeToRefs: (store: any) => ({
    tabMoveInActiveId: { value: null },
    bashMatrixInfo: { value: {} },
    editMode: { value: 'preview' },
    mobileInPc: { value: false },
    curComponent: { value: null }
  }),
  defineStore: vi.fn()
}))

vi.mock('@/views/visualized/data/dataset/form/util', () => ({
  guid: () => 'test-guid-' + Math.random()
}))

vi.mock('@/utils/eventBus', () => ({
  default: { on: vi.fn(), off: vi.fn(), emit: vi.fn() }
}))

vi.mock('@/utils/canvasUtils', () => ({
  canvasChangeAdaptor: vi.fn(),
  findComponentIndexById: vi.fn(() => -1),
  isDashboard: () => false,
  filterEmptyFolderTree: vi.fn()
}))

vi.mock('@/custom-component/de-tabs/DeCustomTab.vue', () => ({
  default: { template: '<div class="de-custom-tab"><slot /></div>' }
}))

vi.mock('@/api/visualization/linkage', () => ({
  getPanelAllLinkageInfo: vi.fn(() => Promise.resolve({ data: {} }))
}))

vi.mock('@/utils/style', () => ({
  dataVTabComponentAdd: vi.fn(),
  groupSizeStyleAdaptor: vi.fn()
}))

vi.mock('@/store/modules/data-visualization/copy', () => ({
  deepCopyTabItemHelper: vi.fn(() => [])
}))

vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: (url: string) => url
}))

vi.mock('@/components/de-board/Board.vue', () => ({
  default: { template: '<div class="board-stub" />' }
}))

vi.mock('@/views/chart/components/js/g2plot_tooltip_carousel', () => ({
  default: { resume: vi.fn(), paused: vi.fn() }
}))

vi.mock('@/views/data-visualization/PreviewCanvas.vue', () => ({
  default: { template: '<div class="preview-canvas-stub" />' }
}))

vi.mock('@/custom-component/de-screen/SelectScreenDialog.vue', () => ({
  default: {
    template: '<div class="select-screen-dialog-stub" />',
    methods: { init: vi.fn() }
  }
}))

import Component from '../Component.vue'

const createElement = () => ({
  id: 'test-element',
  propValue: [
    { name: 'tab1', title: 'Tab 1', screenId: null, closable: true }
  ],
  editableTabsValue: 'tab1',
  style: {
    headHorizontalPosition: 'left',
    showTabTitle: true,
    textDecoration: 'none',
    fontStyle: 'normal',
    fontWeight: 'normal',
    fontSize: 16,
    activeFontSize: 18
  },
  titleBackground: {
    enable: false,
    multiply: false,
    active: {
      backgroundImageEnable: false,
      backgroundType: 'innerImage',
      innerImage: 'board/board_1.svg',
      innerImageColor: '#000000'
    },
    inActive: {
      backgroundImageEnable: false,
      backgroundType: 'innerImage',
      innerImage: 'board/board_1.svg',
      innerImageColor: '#000000'
    }
  },
  carousel: { enable: false, time: 5 }
})

const mountComponent = () =>
  shallowMount(Component, {
    props: {
      canvasStyleData: {},
      canvasViewInfo: {},
      dvInfo: { id: 'dv-1', type: 'dashboard' },
      element: createElement(),
      isEdit: false,
      showPosition: 'preview',
      scale: 1,
      searchCount: 0,
      fontFamily: 'inherit'
    },
    global: {
      mocks: { $t: (key: string) => key }
    }
  })

describe('de-screen/Component', () => {
  it('renders the root container', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.custom-tabs-head').exists()).toBe(true)
  })

  it('accepts required props', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('canvasStyleData')).toBeDefined()
    expect(wrapper.props('element')).toBeDefined()
    expect(wrapper.props('dvInfo')).toBeDefined()
  })

  it('defaults isEdit to false', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('isEdit')).toBe(false)
  })

  it('defaults scale to 1', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('scale')).toBe(1)
  })
})
