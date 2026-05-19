import { ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({ service: {} as any, PATH_URL: './', cancelMap: new Map() }))
vi.mock('@/api/visualization/dataVisualization', () => ({
  queryTreeApi: () => Promise.resolve([])
}))
vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: () => ({
    dvInfo: ref({
      id: 'dv1',
      type: 'dashboard',
      name: 'Test Dashboard',
      dataState: 'ready',
      status: 1,
      pid: '0'
    }),
    componentData: ref([]),
    canvasViewInfo: ref({}),
    editMode: ref('edit'),
    curComponent: ref(null),
    linkageSettingStatus: ref(false),
    curLinkageView: ref(null),
    targetLinkageInfo: ref({}),
    curBatchOptComponents: ref([]),
    batchOptStatus: ref(false),
    appData: ref(null)
  })
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    setEditMode: vi.fn(),
    setCurComponent: vi.fn(),
    setComponentData: vi.fn(),
    clearLinkageSettingInfo: vi.fn(),
    setHiddenListStatus: vi.fn(),
    setBatchOptStatus: vi.fn(),
    setAppDataInfo: vi.fn(),
    updateDvInfoCall: vi.fn(),
    matrixSizeAdaptor: vi.fn()
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn(),
    snapshotData: [],
    snapshotIndex: 0,
    styleChangeTimes: { value: 0 },
    undo: vi.fn(),
    redo: vi.fn(),
    resetStyleChangeTimes: vi.fn(),
    initSnapShot: vi.fn(),
    resetSnapshot: vi.fn()
  })
}))

vi.mock('@/store/modules/data-visualization/copy', () => ({
  copyStoreWithOut: () => ({
    copyMultiplexingComponents: vi.fn()
  })
}))

vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({ getIsDataEaseBi: false, getIsIframe: false })
}))

vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({ baseUrl: '', clearState: vi.fn() })
}))

vi.mock('@/store/modules/user', () => ({
  useUserStoreWithOut: () => ({ getOid: undefined })
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({ wsCache: { get: vi.fn(() => false), set: vi.fn(), delete: vi.fn() } })
}))

vi.mock('@/utils/eventBus', () => ({
  default: { on: vi.fn(), off: vi.fn(), emit: vi.fn() }
}))

vi.mock('@/utils/canvasUtils', () => ({
  canvasSave: vi.fn((cb: any) => cb()),
  canvasSaveWithParams: vi.fn((_p: any, cb: any) => cb()),
  checkCanvasChangePre: vi.fn((cb: any) => cb()),
  findAllViewsId: vi.fn(),
  initCanvasData: vi.fn()
}))

vi.mock('@/config/axios', () => ({}))
vi.mock('@/api/visualization/linkage', () => ({
  getPanelAllLinkageInfo: vi.fn(() => Promise.resolve({ data: {} })),
  saveLinkage: vi.fn(() => Promise.resolve())
}))

vi.mock('@/config/axios', () => ({}))
vi.mock('@/api/visualization/linkJump', () => ({
  queryVisualizationJumpInfo: vi.fn(() => Promise.resolve({ data: {} }))
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div />' }
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/utils/utils', () => ({
  deepCopy: (v: any) => JSON.parse(JSON.stringify(v)),
  getLocale: () => 'zh-CN'
}))

vi.mock('vue-clipboard3', () => ({
  default: () => ({ copy: vi.fn() })
}))

import DbToolbar from '../DbToolbar.vue'

const stubs = {
  ElButton: { template: '<button><slot /></button>', props: ['type', 'icon', 'disabled', 'text'] },
  ElIcon: { template: '<i><slot /></i>' },
  ElTooltip: { template: '<div><slot /></div>', props: ['content', 'effect', 'placement'] },
  ElDropdown: {
    template: '<div><slot /><slot name="dropdown" /></div>',
    props: ['trigger', 'disabled']
  },
  ElDropdownMenu: { template: '<div><slot /></div>' },
  ElDropdownItem: { template: '<div><slot /></div>' },
  ElCol: { template: '<div><slot /></div>' },
  Icon: { template: '<span><slot /></span>' },
  ComponentGroup: { template: '<div><slot /></div>' },
  ComponentButton: { template: '<button />' },
  ComponentButtonLabel: { template: '<button />' },
  MultiplexingCanvas: { template: '<div />' },
  DeResourceGroupOpt: { template: '<div />' },
  OuterParamsSet: { template: '<div />' },
  DeFullscreen: { template: '<div />' },
  DeAppApply: { template: '<div />' },
  XpackComponent: { template: '<div />' },
  icon_left_outlined: { template: '<svg />' },
  icon_undo_outlined: { template: '<svg />' },
  icon_redo_outlined: { template: '<svg />' }
}

describe('DbToolbar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(DbToolbar, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the toolbar container', () => {
    const wrapper = shallowMount(DbToolbar, { global: { stubs } })
    expect(wrapper.find('.toolbar-main').exists()).toBe(true)
  })

  it('accepts createType prop', () => {
    const wrapper = shallowMount(DbToolbar, {
      props: { createType: 'new' },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
