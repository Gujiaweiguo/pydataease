import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    batchOptStatus: false,
    mobileInPc: false,
    canvasStyleData: { component: { formatterItem: {} } }
  })
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#000', '#fff'],
  DEFAULT_TOOLTIP: {
    show: true,
    backgroundColor: '#fff',
    color: '#333',
    fontSize: 12,
    tooltipFormatter: {
      type: 'auto',
      unit: 1,
      suffix: '',
      decimalCount: 2,
      thousandSeparator: true,
      unitLanguage: 'ch'
    },
    seriesTooltipFormatter: [],
    carousel: { enable: false, stayTime: 3, intervalTime: 5 },
    showGap: false,
    showFields: [],
    customContent: ''
  }
}))
vi.mock('@/views/chart/components/js/formatter', () => ({
  isEnLocal: false,
  formatterType: [{ name: 'value_formatter_auto', value: 'auto' }],
  getUnitTypeList: () => [],
  initFormatCfgUnit: () => undefined,
  onChangeFormatCfgUnitLanguage: () => undefined,
  mergeTooltipFormat: () => undefined
}))
vi.mock('@/views/chart/components/js/panel', () => ({
  default: { getChartView: () => null }
}))
vi.mock('@/utils/attr', () => ({
  fieldType: ['text', 'time', 'value', 'value', 'value', 'location', 'binary', 'url']
}))
vi.mock('@/components/icon-group/field-list', () => ({ iconFieldMap: {} }))
vi.mock('lodash-es', () => ({
  cloneDeep: (v: any) => JSON.parse(JSON.stringify(v)),
  defaultsDeep: (t: any, ...s: any[]) => Object.assign({}, ...s, t),
  defaultTo: (v: any, d: any) => v ?? d,
  partition: (arr: any[], fn: any) => {
    const t = arr.filter(fn)
    const f = arr.filter((x: any) => !fn(x))
    return [t, f]
  },
  map: (arr: any[], fn: any) => arr.map(fn),
  includes: (arr: any[], v: any) => arr.includes(v),
  isEmpty: (v: any) => !v || (Array.isArray(v) && v.length === 0)
}))
vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (s: any) => ({ batchOptStatus: { value: false }, mobileInPc: { value: false } })
}))
vi.mock('@/hooks/web/useEmitt', () => ({ useEmitt: () => undefined }))
vi.mock('@/components/icon-custom/src/Icon.vue', () => ({
  default: { template: '<span><slot /></span>' }
}))
vi.mock('@/assets/svg/icon_info_outlined.svg', () => ({ default: 'icon' }))

import TooltipSelector from '../components/TooltipSelector.vue'

const globalStubs = {
  ElForm: { template: '<form><slot /></form>', props: ['model', 'disabled', 'size'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'class'] },
  ElRow: { template: '<div><slot /></div>', props: ['gutter'] },
  ElCol: { template: '<div><slot /></div>', props: ['span'] },
  ElSelect: {
    template: '<select><slot /></select>',
    props: ['modelValue', 'effect', 'size', 'disabled']
  },
  ElOption: { template: '<option><slot /></option>', props: ['key', 'label', 'value'] },
  ElColorPicker: { template: '<div />', props: ['modelValue', 'effect'] },
  ElCheckbox: {
    template: '<input type="checkbox" />',
    props: ['modelValue', 'effect', 'size', 'label', 'disabled']
  },
  ElInput: {
    template: '<input />',
    props: [
      'modelValue',
      'effect',
      'type',
      'maxlength',
      'clearable',
      'placeholder',
      'autosize',
      'disabled',
      'size'
    ]
  },
  ElInputNumber: {
    template: '<input type="number" />',
    props: [
      'modelValue',
      'effect',
      'precision',
      'min',
      'max',
      'controls',
      'disabled',
      'size',
      'controlsPosition',
      'style'
    ]
  },
  ElSpace: { template: '<div><slot /></div>' },
  ElTooltip: { template: '<div><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  ElDivider: { template: '<hr />' },
  Icon: { template: '<span><slot /></span>', props: ['name', 'className'] }
}

const defaultChart = () => ({
  type: 'bar',
  id: 'chart1',
  render: 'antv',
  yAxis: [],
  yAxisExt: [],
  extBubble: [],
  xAxis: [],
  customAttr: {
    tooltip: {
      show: true,
      backgroundColor: '#fff',
      color: '#333',
      fontSize: 12,
      tooltipFormatter: {
        type: 'auto',
        unit: 1,
        suffix: '',
        decimalCount: 2,
        thousandSeparator: true,
        unitLanguage: 'ch'
      },
      seriesTooltipFormatter: [],
      carousel: { enable: false, stayTime: 3, intervalTime: 5 },
      showGap: false,
      showFields: [],
      customContent: ''
    }
  }
})

describe('TooltipSelector', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(TooltipSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['color', 'fontSize'] },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('computes toolTip as inverted theme', () => {
    const wrapper = shallowMount(TooltipSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: [] },
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).toolTip).toBe('light')
  })

  it('emits onTooltipChange when changeTooltipAttr is called', () => {
    const wrapper = shallowMount(TooltipSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['color'] },
      global: { stubs: globalStubs }
    })
    ;(wrapper.vm as any).changeTooltipAttr('color')
    expect(wrapper.emitted('onTooltipChange')).toBeTruthy()
  })

  it('showProperty returns correct value', () => {
    const wrapper = shallowMount(TooltipSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['color', 'showGap'] },
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).showProperty('color')).toBe(true)
    expect((wrapper.vm as any).showProperty('carousel')).toBe(false)
  })

  it('computes showTotalPercent for sankey type', () => {
    const chart = defaultChart()
    chart.type = 'sankey'
    const wrapper = shallowMount(TooltipSelector, {
      props: { chart, themes: 'dark', propertyInner: [] },
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).showTotalPercent).toBe(true)
  })
})
