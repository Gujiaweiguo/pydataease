import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/config/axios/service', () => ({}))

vi.mock('@/config/axios/refresh', () => ({}))

vi.mock('@/config/axios/hmac', () => ({}))

vi.mock('vue-clipboard3', () => ({
  default: vi.fn(() => ({ copy: vi.fn() }))
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn()
  })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    dvInfo: { value: { id: null, name: '', type: 'dataV' } },
    canvasViewDataInfo: { value: {} },
    canvasDataInit: vi.fn(),
    updateCurDvInfo: vi.fn()
  })
}))

vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({
    getIsDataEaseBi: false,
    setArrowSide: vi.fn()
  })
}))

vi.mock('@/store/modules/user', () => ({
  useUserStoreWithOut: () => ({
    getName: 'admin'
  })
}))

vi.mock('vant', () => ({
  Icon: { template: '<i />' },
  showToast: vi.fn()
}))

vi.mock('@/components/de-app/AppExportForm.vue', () => ({
  default: { template: '<div class="app-export-form-stub" />' }
}))

vi.mock('@/components/empty-background/src/EmptyBackground.vue', () => ({
  default: { template: '<div class="empty-bg-stub" />', props: ['description', 'imgType'] }
}))

vi.mock('@/views/data-visualization/MultiplexPreviewShow.vue', () => ({
  default: { template: '<div class="multiplex-stub" />' }
}))

vi.mock('@/views/data-visualization/DvPreview.vue', () => ({
  default: { template: '<div class="dv-preview-stub" />' }
}))

vi.mock('@/views/data-visualization/PreviewHead.vue', () => ({
  default: { template: '<div class="preview-head-stub" />' }
}))

vi.mock('@/views/common/DeResourceTree.vue', () => ({
  default: { template: '<div class="resource-tree-stub" />' }
}))

vi.mock('@/views/common/DeResourceArrow.vue', () => ({
  default: { template: '<div class="arrow-side-stub" />', props: ['isInside'] }
}))

vi.mock('@/hooks/web/useMoveLine', () => ({
  useMoveLine: () => ({ width: 279, node: { value: null } })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn(() => ({
    emitter: { emit: vi.fn() }
  }))
}))

vi.mock('@/utils/canvasUtils', () => ({
  getMapElementIds: vi.fn(() => []),
  initCanvasData: vi.fn(),
  initCanvasDataPrepare: vi.fn(),
  onInitReady: vi.fn()
}))

vi.mock('@/utils/imgUtils', () => ({
  download2AppTemplate: vi.fn(),
  downloadCanvas2: vi.fn()
}))

vi.mock('@/utils/utils', () => ({
  deepCopy: vi.fn((v: any) => v),
  getLocale: vi.fn(() => 'zh'),
  filterFreeFolder: vi.fn(),
  exportPermission: vi.fn(() => [true, false]),
  isFreeFolder: vi.fn(() => false)
}))

vi.mock('@/api/visualization/dataVisualization', () => ({
  exportLogApp: vi.fn(),
  exportLogImg: vi.fn(),
  exportLogPDF: vi.fn(),
  exportLogTemplate: vi.fn(),
  queryTreeApi: vi.fn(() => Promise.resolve([]))
}))

vi.mock('@/api/dataset', () => ({
  getDatasetTree: vi.fn(() => Promise.resolve([]))
}))

vi.mock('pinia', async importOriginal => {
  const actual = (await importOriginal()) as Record<string, unknown>
  return {
    ...actual,
    storeToRefs: vi.fn(() => ({
      dvInfo: { value: { id: null, name: '', type: 'dataV' } },
      canvasViewDataInfo: { value: {} }
    }))
  }
})

import PreviewShow from '../PreviewShow.vue'

const globalStubs = {
  ElAside: { template: '<aside class="el-aside-stub"><slot /></aside>' },
  ElContainer: { template: '<div class="el-container-stub"><slot /></div>' },
  ElButton: { template: '<button><slot /><slot name="icon" /></button>' },
  ElIcon: { template: '<i><slot /></i>' },
  DeResourceTree: { template: '<div class="resource-tree-stub" />' },
  ArrowSide: { template: '<div class="arrow-side-stub" />', props: ['isInside'] },
  PreviewHead: { template: '<div class="preview-head-stub" />' },
  EmptyBackground: { template: '<div class="empty-bg-stub" />', props: ['description', 'imgType'] },
  DvPreview: { template: '<div class="dv-preview-stub" />' },
  MultiplexPreviewShow: { template: '<div class="multiplex-stub" />' },
  AppExportForm: { template: '<div class="app-export-form-stub" />' }
}

describe('PreviewShow', () => {
  const mountComponent = (showPosition = 'preview') =>
    shallowMount(PreviewShow, {
      props: { showPosition },
      global: { stubs: globalStubs }
    })

  it('renders', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('has dv-preview wrapper class', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.dv-preview').exists()).toBe(true)
  })

  it('exposes getPreviewStateInfo method', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    expect(typeof vm.getPreviewStateInfo).toBe('function')
  })

  it('contains resource tree stub', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.resource-tree-stub').exists()).toBe(true)
  })
})
