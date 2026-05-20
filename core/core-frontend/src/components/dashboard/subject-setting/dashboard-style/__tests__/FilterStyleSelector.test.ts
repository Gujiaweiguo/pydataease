import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store', () => ({ store: {} }))

vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  storeToRefs: vi.fn(() => ({})),
  createPinia: vi.fn()
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    canvasStyleData: { component: { filterStyle: {} } }
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#5470c6']
}))

vi.mock('@/utils/canvasStyle', () => ({
  adaptCurThemeFilterStyleAll: vi.fn()
}))

vi.mock('@/utils/eventBus', () => ({
  default: { on: vi.fn(), off: vi.fn(), emit: vi.fn() }
}))

import FilterStyleSelector from '@/components/dashboard/subject-setting/dashboard-style/FilterStyleSelector.vue'

const stubs = {
  ElCol: { template: '<div><slot /></div>' },
  ElForm: { template: '<form><slot /></form>', props: ['model', 'labelWidth', 'size'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'class'] },
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue', 'size'] },
  ElRadioButton: { template: '<label><slot /></label>', props: ['label', 'disabled'] },
  ElColorPicker: { template: '<div />', props: ['modelValue', 'size', 'class', 'predefine'] },
  ElDivider: { template: '<hr />' },
  ElRow: { template: '<div><slot /></div>', props: ['style'] }
}

describe('FilterStyleSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(FilterStyleSelector, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains root div', () => {
    const wrapper = shallowMount(FilterStyleSelector, { global: { stubs } })
    expect(wrapper.find('div').exists()).toBe(true)
  })
})
