import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: {
      get: vi.fn(() => null),
      set: vi.fn(),
      delete: vi.fn()
    }
  })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn(() => undefined)
}))

vi.mock('@/store/modules/appearance', () => ({
  useAppearanceStoreWithOut: () => ({})
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    dvInfo: { id: null, name: '' },
    setCurComponent: vi.fn(),
    setEditMode: vi.fn(),
    resetDvInfo: vi.fn(),
    updateDvInfoCall: vi.fn()
  })
}))

vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({
    getIsDataEaseBi: false,
    getIsIframe: false
  })
}))

vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({
    dvId: null,
    baseUrl: '',
    clearState: vi.fn()
  })
}))

vi.mock('@/store/modules/share', () => ({
  useShareStoreWithOut: () => ({
    setData: vi.fn()
  })
}))

vi.mock('@/api/visualization/dataVisualization', () => ({
  copyResource: vi.fn(),
  deleteLogic: vi.fn(),
  ResourceOrFolder: {},
  queryShareBaseApi: vi.fn(() => Promise.resolve({ data: {} })),
  updateBase: vi.fn()
}))

vi.mock('@/utils/treeDraggbleChart', () => ({
  treeDraggbleChart: () => ({
    handleDrop: vi.fn(),
    allowDrop: vi.fn(() => true),
    handleDragStart: vi.fn()
  })
}))

vi.mock('@/utils/treeSortUtils', () => ({
  default: vi.fn(() => []),
  treeParentWeight: vi.fn(() => ({}))
}))

vi.mock('@/utils/canvasUtils', () => ({
  findParentIdByChildIdRecursive: vi.fn(),
  onInitReady: vi.fn()
}))

vi.mock('@/utils/utils', () => ({
  isFreeFolder: vi.fn(() => false)
}))

vi.mock('@/config/axios/service', () => ({
  cancelRequestBatch: vi.fn()
}))

vi.mock('@/router', () => ({
  default: {
    currentRoute: { value: { query: {} } }
  }
}))

vi.mock('@/store/modules/interactive', () => ({
  interactiveStoreWithOut: () => ({
    setInteractive: vi.fn(() => Promise.resolve()),
    getPanel: { treeNodes: [], rootManage: false, anyManage: false },
    getScreen: { treeNodes: [], rootManage: false, anyManage: false }
  })
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div />' }
}))

vi.mock('@/components/icon-custom', () => ({
  Icon: { template: '<i><slot /></i>' }
}))

vi.mock('@/components/handle-more', () => ({
  HandleMore: { template: '<div />' }
}))

vi.mock('vue-clipboard3', () => ({
  default: vi.fn(() => ({ copy: vi.fn() }))
}))

vi.mock('pinia', async importOriginal => {
  const actual = await importOriginal() as Record<string, unknown>
  return {
    ...actual,
    storeToRefs: vi.fn(() => ({
      dvInfo: { value: { id: null, name: '' } }
    }))
  }
})

import DeResourceTree from '../DeResourceTree.vue'

const globalStubs = {
  ElIcon: { template: '<i><slot /></i>' },
  ElTooltip: { template: '<div><slot /></div>' },
  ElTree: {
    template: '<div class="el-tree-stub" />',
    methods: {
      setCurrentKey: vi.fn(),
      filter: vi.fn()
    }
  },
  ElInput: { template: '<input />', props: ['modelValue'] },
  ElScrollbar: { template: '<div><slot /></div>' },
  ElDropdown: { template: '<div><slot /><slot name="dropdown" /></div>' },
  ElDropdownMenu: { template: '<div><slot /></div>' },
  ElDropdownItem: { template: '<div><slot /></div>' },
  DeResourceGroupOpt: { template: '<div />' },
  DeResourceCreateOptV2: { template: '<div />' },
  DvHandleMore: { template: '<div />', props: ['menuList', 'node', 'anyManage', 'resourceType'] }
}

describe('DeResourceTree', () => {
  const mountComponent = () =>
    shallowMount(DeResourceTree, {
      props: { curCanvasType: 'dashboard' },
      global: { stubs: globalStubs }
    })

  it('renders', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('has resource-tree class', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.resource-tree').exists()).toBe(true)
  })

  it('displays tree header with resource label', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.tree-header').exists()).toBe(true)
  })

  it('exposes rootManage, hasData, createNewObject, mounted', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    expect('rootManage' in vm).toBe(true)
    expect('hasData' in vm).toBe(true)
    expect(typeof vm.createNewObject).toBe('function')
    expect('mounted' in vm).toBe(true)
  })
})
