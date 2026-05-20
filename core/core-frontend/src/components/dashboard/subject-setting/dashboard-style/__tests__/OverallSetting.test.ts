import { ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  recordSnapshotCache: vi.fn(),
  canvasStyleDataValue: {
    fontFamily: 'Arial',
    refreshViewEnable: false,
    refreshTime: 1,
    refreshUnit: 'minute',
    refreshBrowserEnable: false,
    refreshBrowserTime: 1,
    refreshBrowserUnit: 'minute',
    refreshViewLoading: false,
    dashboardAdaptor: 'keepHeightAndWidth',
    suspensionButtonAvailable: false,
    dashboard: {
      themeColor: 'light',
      gap: 'yes',
      gapMode: 'small',
      gapSize: 3,
      resultMode: 'all',
      resultCount: 1000,
      showGrid: false
    },
    component: {
      chartCommonStyle: {},
      chartTitle: {},
      chartColor: {},
      filterStyle: {},
      tabStyle: {},
      seniorStyleSetting: {}
    }
  },
  dvInfoValue: { type: 'dashboard' }
}))

vi.mock('pinia', async () => {
  const actual = await vi.importActual('pinia')
  return {
    ...actual,
    storeToRefs: () => ({
      canvasStyleData: ref(mocks.canvasStyleDataValue),
      dvInfo: ref(mocks.dvInfoValue)
    })
  }
})

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({})
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: mocks.recordSnapshotCache })
}))

vi.mock('@/store/modules/appearance', () => ({
  useAppearanceStoreWithOut: () => ({ fontList: [], setCurrentFont: vi.fn() })
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  CHART_FONT_FAMILY_ORIGIN: [{ name: 'Arial', value: 'Arial' }],
  DEFAULT_COLOR_CASE_LIGHT: {},
  DEFAULT_COLOR_CASE_DARK: {},
  DEFAULT_TITLE_STYLE_LIGHT: {},
  DEFAULT_TITLE_STYLE_DARK: {},
  DEFAULT_TAB_COLOR_CASE_LIGHT: {},
  DEFAULT_TAB_COLOR_CASE_DARK: {},
  FILTER_COMMON_STYLE_LIGHT: {},
  FILTER_COMMON_STYLE_DARK: {},
  SENIOR_STYLE_SETTING_LIGHT: {},
  SENIOR_STYLE_SETTING_DARK: {}
}))

vi.mock('@/utils/canvasStyle', () => ({
  adaptCurThemeCommonStyleAll: vi.fn(),
  adaptTitleFontFamilyAll: vi.fn(),
  LIGHT_THEME_DASHBOARD_BACKGROUND: '#fff',
  DARK_THEME_DASHBOARD_BACKGROUND: '#000'
}))

vi.mock('@/utils/utils', () => ({
  deepCopy: (v: any) => JSON.parse(JSON.stringify(v))
}))

vi.mock('@/custom-component/component-list', () => ({
  COMMON_COMPONENT_BACKGROUND_LIGHT: {},
  COMMON_COMPONENT_BACKGROUND_DARK: {}
}))

vi.mock('@/utils/ModelUtil', () => ({
  isDesktop: () => false
}))

vi.mock('@/utils/eventBus', () => ({
  default: { on: vi.fn(), off: vi.fn(), emit: vi.fn() }
}))

vi.mock('@/config/axios', () => ({}))

import OverallSetting from '@/components/dashboard/subject-setting/dashboard-style/OverallSetting.vue'

const stubs = {
  ElForm: { template: '<form><slot /></form>', props: ['size', 'labelPosition'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'class'] },
  ElSpace: { template: '<div><slot /></div>', props: ['size'] },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue', 'effect'] },
  ElOption: { template: '<option><slot /></option>', props: ['label', 'value'] },
  ElCheckbox: { template: '<input type="checkbox" />', props: ['modelValue', 'effect', 'size'] },
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue', 'effect'] },
  ElRadio: { template: '<label><slot /></label>', props: ['label', 'effect', 'value'] },
  ElInputNumber: {
    template: '<input type="number" />',
    props: ['modelValue', 'effect', 'controlsPosition', 'min', 'max', 'disabled']
  },
  ElInput: {
    template: '<input />',
    props: ['modelValue', 'effect', 'type', 'disabled', 'min', 'max']
  },
  ElTooltip: { template: '<div><slot /></div>', props: ['effect', 'placement'] },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>' },
  ColorButton: { template: '<button><slot /></button>', props: ['colorType', 'label'] },
  icon_info_outlined: { template: '<svg />' }
}

describe('OverallSetting (dashboard-style)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(OverallSetting, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts themes prop', () => {
    const wrapper = shallowMount(OverallSetting, {
      props: { themes: 'dark' },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has form items for dashboard type', () => {
    const wrapper = shallowMount(OverallSetting, { global: { stubs } })
    expect(wrapper.findAll('div').length).toBeGreaterThan(0)
  })
})
