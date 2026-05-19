import { ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: () => ({
    dvInfo: ref({ id: 'dv1', type: 'dashboard', name: 'Test' }),
    canvasViewInfo: ref({}),
    componentData: ref([])
  })
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    setNowPanelJumpInfo: vi.fn()
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))

vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({ getIsDataEaseBi: false, getIsIframe: false })
}))

vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({ clearState: vi.fn() })
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({ wsCache: { get: vi.fn(), set: vi.fn() } })
}))

vi.mock('@/api/visualization/linkJump', () => ({
  queryVisualizationJumpInfo: vi.fn(() => Promise.resolve({ data: {} })),
  queryWithViewId: vi.fn(() => Promise.resolve({ data: { linkJumpInfoArray: [] } })),
  updateJumpSet: vi.fn(() => Promise.resolve())
}))

vi.mock('@/api/visualization/dataVisualization', () => ({
  findDvType: vi.fn(() => Promise.resolve({ data: 'dashboard' })),
  queryTreeApi: vi.fn(() => Promise.resolve([]))
}))

vi.mock('@/api/dataset', () => ({
  getDatasetDetails: vi.fn(() => Promise.resolve({})),
  listFieldByDatasetGroup: vi.fn(() => Promise.resolve({ data: [] }))
}))

vi.mock('@/components/icon-group/field-list', () => ({
  iconFieldMap: {}
}))

vi.mock('@/components/icon-group/chart-list', () => ({
  iconChartMap: {}
}))

vi.mock('@/utils/attr', () => ({
  fieldType: {}
}))

vi.mock('@/utils/canvasUtils', () => ({
  filterEmptyFolderTree: (v: any) => v
}))

vi.mock('@/utils/treeSortUtils', () => ({
  default: (v: any) => v
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div />' }
}))

vi.mock('@/views/visualized/data/dataset/form/util', () => ({
  guid: () => 'test-guid-' + Math.random()
}))

vi.mock('@/config/axios', () => ({}))

import LinkJumpSet from '../LinkJumpSet.vue'

const stubs = {
  ElDialog: {
    template: '<div><slot /></div>',
    props: ['modelValue', 'width', 'title']
  },
  ElButton: { template: '<button><slot /></button>', props: ['type', 'size'] },
  ElRow: { template: '<div class="el-row"><slot /></div>' },
  ElCol: { template: '<div class="el-col"><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  ElSwitch: { template: '<input type="checkbox" />', props: ['modelValue', 'size'] },
  ElTree: { template: '<div class="el-tree"><slot /></div>', props: ['data', 'nodeKey'] },
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue'] },
  ElRadio: { template: '<label><slot /></label>', props: ['value'] },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue'] },
  ElOption: { template: '<option><slot /></option>' },
  ElCheckbox: { template: '<input type="checkbox" />', props: ['modelValue'] },
  ElTooltip: { template: '<div><slot /></div>' },
  ElInput: { template: '<input />', props: ['modelValue'] },
  ElScrollbar: { template: '<div><slot /></div>' },
  ElFormItem: { template: '<div><slot /></div>' },
  Icon: { template: '<span><slot /></span>' },
  XpackComponent: { template: '<div />' },
  EmptyBackground: { template: '<div />' },
  JumpSetOuterContentEditor: { template: '<div />' }
}

describe('LinkJumpSet', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(LinkJumpSet, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes dialogInit method', () => {
    const wrapper = shallowMount(LinkJumpSet, { global: { stubs } })
    const vm = wrapper.vm as any
    expect(typeof vm.dialogInit).toBe('function')
  })
})
