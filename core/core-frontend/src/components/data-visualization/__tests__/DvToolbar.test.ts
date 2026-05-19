import { ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/api/visualization/dataVisualization', () => ({ queryTreeApi: () => Promise.resolve([]) }))
vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: () => ({
    dvInfo: ref({ id: 'dv1', type: 'dataV', name: 'Test Screen', dataState: 'ready', status: 1 }),
    componentData: ref([]),
    canvasViewInfo: ref({}),
    canvasStyleData: ref({ scale: 100, width: 1920 }),
    editMode: ref('edit'),
    appData: ref(null),
    styleChangeTimes: ref(0),
    snapshotIndex: ref(0)
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
    setAppDataInfo: vi.fn(),
    updateDvInfoCall: vi.fn(),
    canvasStateChange: vi.fn()
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn(),
    snapshotData: [],
    snapshotIndex: { value: 0 },
    styleChangeTimes: { value: 0 },
    undo: vi.fn(),
    redo: vi.fn(),
    resetStyleChangeTimes: vi.fn(),
    initSnapShot: vi.fn(),
    resetSnapshot: vi.fn()
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

vi.mock('@/utils/changeComponentsSizeWithScale', () => ({
  changeSizeWithScale: vi.fn()
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

import DvToolbar from '../DvToolbar.vue'

const stubs = {
  ElButton: { template: '<button><slot /></button>', props: ['type', 'icon', 'disabled'] },
  ElIcon: { template: '<i><slot /></i>' },
  ElTooltip: { template: '<div><slot /></div>', props: ['content', 'effect', 'placement', 'offset'] },
  ElDropdown: { template: '<div><slot /><slot name="dropdown" /></div>', props: ['trigger', 'disabled'] },
  ElDropdownMenu: { template: '<div><slot /></div>' },
  ElDropdownItem: { template: '<div><slot /></div>' },
  Icon: { template: '<span><slot /></span>' },
  ComponentGroup: { template: '<div><slot /></div>' },
  ComponentButton: { template: '<button />' },
  ComponentButtonLabel: { template: '<button />' },
  MultiplexingCanvas: { template: '<div />' },
  DeResourceGroupOpt: { template: '<div />' },
  DeAppApply: { template: '<div />' },
  OuterParamsSet: { template: '<div />' },
  DeFullscreen: { template: '<div />' },
  XpackComponent: { template: '<div />' },
  'icon_left_outlined': { template: '<svg />' },
  'icon_undo_outlined': { template: '<svg />' },
  'icon_redo_outlined': { template: '<svg />' }
}

describe('DvToolbar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(DvToolbar, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the toolbar container', () => {
    const wrapper = shallowMount(DvToolbar, { global: { stubs } })
    expect(wrapper.find('.toolbar-main').exists()).toBe(true)
  })

  it('accepts createType prop', () => {
    const wrapper = shallowMount(DvToolbar, {
      props: { createType: 'new' },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
