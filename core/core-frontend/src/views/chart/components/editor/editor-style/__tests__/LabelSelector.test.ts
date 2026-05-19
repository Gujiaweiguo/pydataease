import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    batchOptStatus: false,
    canvasStyleData: { dashboard: { themeColor: 'dark' }, component: { formatterItem: {} } }
  })
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#000', '#fff'],
  DEFAULT_LABEL: {
    show: true,
    color: '#000',
    fontSize: 12,
    formatter: '',
    labelFormatter: {
      type: 'auto',
      unit: 1,
      suffix: '',
      decimalCount: 2,
      thousandSeparator: true,
      unitLanguage: 'ch'
    },
    quotaLabelFormatter: {
      type: 'auto',
      unit: 1,
      suffix: '',
      decimalCount: 2,
      thousandSeparator: true,
      unitLanguage: 'ch'
    },
    seriesLabelFormatter: [],
    totalFormatter: {
      type: 'auto',
      unit: 1,
      suffix: '',
      decimalCount: 2,
      thousandSeparator: true,
      unitLanguage: 'ch'
    },
    conversionTag: { label: '' },
    proportionSeriesFormatter: {},
    showFields: [],
    customContent: '',
    showDimension: true,
    showQuota: true,
    showProportion: false
  }
}))
vi.mock('@/views/chart/components/js/formatter', () => ({
  isEnLocal: false,
  formatterType: [
    { name: 'value_formatter_auto', value: 'auto' },
    { name: 'value_formatter_value', value: 'value' }
  ],
  getUnitTypeList: () => [],
  initFormatCfgUnit: () => undefined,
  onChangeFormatCfgUnitLanguage: () => undefined
}))
vi.mock('@/views/chart/components/editor/util/StringUtils', () => ({
  includesAny: (...args: any[]) => false
}))
vi.mock('@/utils/attr', () => ({
  fieldType: ['text', 'time', 'value', 'value', 'value', 'location', 'binary', 'url']
}))
vi.mock('@/components/icon-group/field-list', () => ({ iconFieldMap: {} }))
vi.mock('lodash-es', () => ({
  cloneDeep: (v: any) => JSON.parse(JSON.stringify(v)),
  defaultsDeep: (t: any, ...s: any[]) => Object.assign({}, ...s, t),
  intersection: (...arrs: any[]) => arrs.reduce((a, b) => a.filter((i: any) => b.includes(i))),
  union: (...arrs: any[]) => [...new Set(arrs.flat())],
  defaultTo: (v: any, d: any) => v ?? d,
  map: (arr: any[], fn: any) => arr.map(fn),
  isEmpty: (v: any) => !v || (Array.isArray(v) && v.length === 0)
}))
vi.mock('pinia', () => ({ storeToRefs: (s: any) => ({ batchOptStatus: { value: false } }) }))
vi.mock('@/components/icon-custom/src/Icon.vue', () => ({
  default: { template: '<span><slot /></span>' }
}))
vi.mock('@/assets/svg/icon_info_outlined.svg', () => ({ default: 'icon' }))

import LabelSelector from '../components/LabelSelector.vue'

const globalStubs = {
  ElForm: { template: '<form><slot /></form>', props: ['model', 'disabled', 'size'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'class'] },
  ElRow: { template: '<div><slot /></div>', props: ['gutter'] },
  ElCol: { template: '<div><slot /></div>', props: ['span'] },
  ElSelect: {
    template: '<select><slot /></select>',
    props: [
      'modelValue',
      'effect',
      'size',
      'disabled',
      'filterable',
      'multiple',
      'collapseTags',
      'collapseTagsTooltip'
    ]
  },
  ElOption: { template: '<option><slot /></option>', props: ['key', 'label', 'value', 'disabled'] },
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
      'controlsPosition'
    ]
  },
  ElSpace: { template: '<div><slot /></div>' },
  ElTooltip: { template: '<div><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  ElDivider: { template: '<hr />', props: ['class'] },
  Icon: { template: '<span><slot /></span>', props: ['name', 'className'] }
}

const defaultChart = () => ({
  type: 'bar',
  yAxis: [],
  yAxisExt: [],
  customAttr: {
    label: {
      show: true,
      color: '#000',
      fontSize: 12,
      showFields: [],
      customContent: '',
      showDimension: true,
      showQuota: true,
      showProportion: false,
      labelFormatter: {
        type: 'auto',
        unit: 1,
        suffix: '',
        decimalCount: 2,
        thousandSeparator: true,
        unitLanguage: 'ch'
      },
      quotaLabelFormatter: { type: 'auto' },
      seriesLabelFormatter: [],
      totalFormatter: { type: 'auto' },
      conversionTag: { label: '' },
      proportionSeriesFormatter: {}
    },
    basicStyle: { layout: 'vertical' }
  }
})

describe('LabelSelector', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(LabelSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['color', 'fontSize'] },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('computes toolTip as inverted theme', () => {
    const wrapper = shallowMount(LabelSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: [] },
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).toolTip).toBe('light')
  })

  it('computes chartType from chart', () => {
    const wrapper = shallowMount(LabelSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: [] },
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).chartType).toBe('bar')
  })

  it('emits onLabelChange when changeLabelAttr is called', () => {
    const wrapper = shallowMount(LabelSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['color'] },
      global: { stubs: globalStubs }
    })
    ;(wrapper.vm as any).changeLabelAttr('color')
    expect(wrapper.emitted('onLabelChange')).toBeTruthy()
  })

  it('showProperty returns correct value', () => {
    const wrapper = shallowMount(LabelSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['color', 'fontSize'] },
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).showProperty('color')).toBe(true)
    expect((wrapper.vm as any).showProperty('rPosition')).toBe(false)
  })
})
