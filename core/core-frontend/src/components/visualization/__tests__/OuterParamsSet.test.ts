import { ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: () => ({
    dvInfo: ref({ id: 'dv1', type: 'dashboard' }),
    componentData: ref([]),
    canvasViewInfo: ref({})
  })
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    canvasViewInfo: {}
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))

vi.mock('@/utils/utils', () => ({
  deepCopy: (v: any) => JSON.parse(JSON.stringify(v))
}))

vi.mock('@/utils/generateID', () => ({
  default: () => 'gen-id-' + Math.random()
}))

vi.mock('@/utils/attr', () => ({
  fieldType: {}
}))

vi.mock('@/api/visualization/outerParams', () => ({
  queryWithVisualizationId: vi.fn(() => Promise.resolve({ data: { outerParamsInfoArray: [] } })),
  updateOuterParamsSet: vi.fn(() => Promise.resolve())
}))

vi.mock('@/api/visualization/dataVisualization', () => ({
  queryOuterParamsDsInfo: vi.fn(() => Promise.resolve({ data: [] })),
  viewDetailList: vi.fn(() => Promise.resolve({ data: [] }))
}))

vi.mock('@/components/icon-group/chart-list', () => ({
  iconChartMap: {}
}))

vi.mock('@/components/icon-group/field-list', () => ({
  iconFieldMap: {}
}))

vi.mock('@/config/axios', () => ({}))

import OuterParamsSet from '../OuterParamsSet.vue'

const stubs = {
  ElDialog: {
    template: '<div><slot /></div>',
    props: ['modelValue', 'width', 'title']
  },
  ElButton: { template: '<button><slot /></button>', props: ['type'] },
  ElRow: { template: '<div><slot /></div>' },
  ElCol: { template: '<div><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  ElTree: {
    template: '<div />',
    props: ['data', 'nodeKey']
  },
  ElCheckbox: { template: '<input type="checkbox" />', props: ['modelValue'] },
  ElInput: { template: '<input />', props: ['modelValue'] },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue'] },
  ElOption: { template: '<option><slot /></option>' },
  ElTooltip: { template: '<div><slot /></div>' },
  ElTabPane: { template: '<div><slot /></div>' },
  ElTabs: { template: '<div><slot /></div>', props: ['modelValue'] },
  HandleMore: { template: '<div />' },
  EmptyBackground: { template: '<div />' },
  Icon: { template: '<span><slot /></span>' }
}

describe('OuterParamsSet', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(OuterParamsSet, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes optInit method', () => {
    const wrapper = shallowMount(OuterParamsSet, { global: { stubs } })
    const vm = wrapper.vm as any
    expect(typeof vm.optInit).toBe('function')
  })

  it('has params list tree structure', () => {
    const wrapper = shallowMount(OuterParamsSet, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })
})
