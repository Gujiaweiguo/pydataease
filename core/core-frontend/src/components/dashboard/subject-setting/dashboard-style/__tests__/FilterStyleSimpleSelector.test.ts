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
    canvasStyleData: {
      component: {
        filterStyle: {
          titleLayout: 'left',
          layout: 'vertical',
          titleColor: '#000',
          labelColor: '#000',
          borderColor: '#ccc',
          text: '#000',
          bgColor: '#fff'
        }
      }
    }
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

vi.mock('lodash-es', () => ({
  cloneDeep: (v: any) => JSON.parse(JSON.stringify(v))
}))

vi.mock('element-plus-secondary', () => ({
  ElIcon: { template: '<i><slot /></i>' }
}))

vi.mock('@/assets/svg/icon_left-align_outlined.svg', () => ({ default: { template: '<svg />' } }))
vi.mock('@/assets/svg/icon_horizontal-align_outlined.svg', () => ({
  default: { template: '<svg />' }
}))
vi.mock('@/assets/svg/icon_right-align_outlined.svg', () => ({ default: { template: '<svg />' } }))
vi.mock('@/assets/svg/icon_title-top-align_outlined.svg', () => ({
  default: { template: '<svg />' }
}))
vi.mock('@/assets/svg/icon_title-left-align_outlined.svg', () => ({
  default: { template: '<svg />' }
}))

import FilterStyleSimpleSelector from '@/components/dashboard/subject-setting/dashboard-style/FilterStyleSimpleSelector.vue'

const stubs = {
  ElForm: { template: '<form><slot /></form>', props: ['labelPosition', 'size'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'class'] },
  ElRow: { template: '<div><slot /></div>', props: ['gutter'] },
  ElCol: { template: '<div><slot /></div>', props: ['span'] },
  ElColorPicker: {
    template: '<div />',
    props: ['modelValue', 'triggerWidth', 'isCustom', 'predefine']
  },
  ElDivider: { template: '<hr />', props: ['class'] },
  ElCollapseItem: { template: '<div><slot /></div>', props: ['title', 'name', 'class'] },
  ElTooltip: { template: '<div><slot /></div>', props: ['effect', 'placement'] },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>', props: ['name'] }
}

describe('FilterStyleSimpleSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(FilterStyleSimpleSelector, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains root div', () => {
    const wrapper = shallowMount(FilterStyleSimpleSelector, { global: { stubs } })
    expect(wrapper.find('div').exists()).toBe(true)
  })
})
