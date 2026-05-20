import { ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  recordSnapshotCache: vi.fn(),
  canvasStyleDataValue: {
    component: {
      chartColor: {
        basicStyle: { gradient: false, alpha: 100, colors: ['#5470c6'] },
        label: { color: '#000', fontSize: 12 },
        tooltip: { color: '#000', fontSize: 12, backgroundColor: '#fff' },
        tableHeader: {
          tableHeaderBgColor: '#fff',
          tableHeaderFontColor: '#000',
          tableHeaderColBgColor: '',
          tableHeaderCornerBgColor: ''
        },
        tableCell: { tableItemBgColor: '#fff', tableItemSubBgColor: '#fff', tableFontColor: '#000' }
      },
      seniorStyleSetting: { pagerColor: '', pagerSize: 12 }
    }
  },
  canvasViewInfoValue: {}
}))

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
  storeToRefs: () => ({
    canvasStyleData: ref(mocks.canvasStyleDataValue),
    canvasViewInfo: ref(mocks.canvasViewInfoValue)
  }),
  createPinia: vi.fn()
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    canvasStyleData: mocks.canvasStyleDataValue,
    canvasViewInfo: mocks.canvasViewInfoValue
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: mocks.recordSnapshotCache })
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#5470c6'],
  DEFAULT_BASIC_STYLE: { colors: ['#5470c6'] },
  DEFAULT_COLOR_CASE: { basicStyle: { colors: ['#5470c6'] } }
}))

vi.mock('@/utils/eventBus', () => ({
  default: { on: vi.fn(), off: vi.fn(), emit: vi.fn() }
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: vi.fn() } })
}))

vi.mock('element-resize-detector', () => ({
  default: () => ({ listenTo: vi.fn() })
}))

vi.mock(
  '@/views/chart/components/editor/editor-style/components/CustomColorStyleSelect.vue',
  () => ({
    default: { template: '<div><slot /></div>' }
  })
)

import ComponentColorSelector from '@/components/dashboard/subject-setting/dashboard-style/ComponentColorSelector.vue'

const stubs = {
  ElForm: { template: '<form><slot /></form>', props: ['model', 'size'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'class'] },
  ElCheckbox: { template: '<input type="checkbox" />', props: ['modelValue', 'size', 'effect'] },
  ElSlider: { template: '<div />', props: ['modelValue', 'effect'] },
  ElInput: {
    template: '<input />',
    props: ['modelValue', 'type', 'effect', 'min', 'max', 'controls']
  },
  ElRow: { template: '<div><slot /></div>', props: ['gutter'] },
  ElCol: { template: '<div><slot /></div>', props: ['span'] },
  ElDivider: { template: '<hr />', props: ['class'] },
  ElCollapseItem: { template: '<div><slot /></div>', props: ['title', 'name', 'effect', 'class'] },
  ElColorPicker: {
    template: '<div />',
    props: [
      'modelValue',
      'size',
      'predefine',
      'triggerWidth',
      'isCustom',
      'effect',
      'showAlpha',
      'colorFormat'
    ]
  },
  ElSelect: {
    template: '<select><slot /></select>',
    props: ['modelValue', 'size', 'effect', 'style']
  },
  ElOption: { template: '<option><slot /></option>', props: ['label', 'value', 'key'] },
  CustomColorStyleSelect: { template: '<div><slot /></div>' }
}

describe('ComponentColorSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(ComponentColorSelector, {
      props: { themes: 'light' },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts themes prop', () => {
    const wrapper = shallowMount(ComponentColorSelector, {
      props: { themes: 'dark' },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders form container', () => {
    const wrapper = shallowMount(ComponentColorSelector, {
      props: { themes: 'light' },
      global: { stubs }
    })
    expect(wrapper.find('div').exists()).toBe(true)
  })
})
