import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#000', '#fff'],
  DEFAULT_YAXIS_STYLE: {
    show: true,
    nameShow: true,
    name: '',
    color: '#333',
    fontSize: 12,
    position: 'left',
    axisValue: { auto: true, min: 0, max: 100, splitCount: 5 },
    axisLine: { show: true, lineStyle: { color: '#333', style: 'solid', width: 1 } },
    splitLine: { show: false, lineStyle: { color: '#ccc', style: 'solid', width: 1 } },
    axisLabel: { show: true, color: '#333', fontSize: 12, rotate: 0, lengthLimit: 20 },
    axisLabelFormatter: {
      type: 'auto',
      unit: 1,
      suffix: '',
      decimalCount: 2,
      thousandSeparator: true,
      unitLanguage: 'ch'
    }
  }
}))
vi.mock('@/views/chart/components/js/formatter', () => ({
  isEnLocal: false,
  formatterType: [{ name: 'value_formatter_auto', value: 'auto' }],
  getUnitTypeList: () => [],
  initFormatCfgUnit: () => undefined,
  onChangeFormatCfgUnitLanguage: () => undefined
}))
vi.mock('element-plus-secondary', () => ({
  ElFormItem: { template: '<div><slot /></div>' },
  ElMessage: { error: () => undefined }
}))
vi.mock('@/assets/svg/icon_info_outlined.svg', () => ({ default: 'icon' }))

import YAxisSelector from '../components/YAxisSelector.vue'

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
  ElColorPicker: { template: '<div />', props: ['modelValue', 'effect', 'disabled'] },
  ElCheckbox: {
    template: '<input type="checkbox" />',
    props: ['modelValue', 'effect', 'size', 'label']
  },
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue', 'size'] },
  ElRadio: { template: '<label><slot /></label>', props: ['effect', 'value'] },
  ElInput: {
    template: '<input />',
    props: ['modelValue', 'effect', 'size', 'maxlength', 'disabled', 'clearable', 'placeholder']
  },
  ElInputNumber: {
    template: '<input type="number" />',
    props: [
      'modelValue',
      'effect',
      'precision',
      'min',
      'max',
      'size',
      'controls',
      'disabled',
      'controlsPosition'
    ]
  },
  ElTooltip: { template: '<div><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  ElDivider: { template: '<hr />', props: ['class'] },
  Icon: { template: '<span><slot /></span>', props: ['name'] }
}

const defaultChart = () => ({
  type: 'bar',
  customStyle: {
    yAxis: {
      show: true,
      nameShow: true,
      name: '',
      color: '#333',
      fontSize: 12,
      position: 'left',
      axisValue: { auto: true, min: 0, max: 100, splitCount: 5 },
      axisLine: { show: true, lineStyle: { color: '#333', style: 'solid', width: 1 } },
      splitLine: { show: false, lineStyle: { color: '#ccc', style: 'solid', width: 1 } },
      axisLabel: { show: true, color: '#333', fontSize: 12, rotate: 0 },
      axisLabelFormatter: {
        type: 'auto',
        unit: 1,
        suffix: '',
        decimalCount: 2,
        thousandSeparator: true,
        unitLanguage: 'ch'
      }
    }
  },
  customAttr: { basicStyle: { layout: 'vertical' } }
})

describe('YAxisSelector', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(YAxisSelector, {
      props: {
        chart: defaultChart(),
        themes: 'dark',
        propertyInner: ['name', 'color', 'fontSize']
      },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('initializes axisForm from chart customStyle', () => {
    const wrapper = shallowMount(YAxisSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['name'] },
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.axisForm.show).toBe(true)
    expect(vm.state.axisForm.position).toBe('left')
  })

  it('emits onChangeYAxisForm when changeAxisStyle is called', () => {
    const wrapper = shallowMount(YAxisSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['name'] },
      global: { stubs: globalStubs }
    })
    ;(wrapper.vm as any).changeAxisStyle('name')
    expect(wrapper.emitted('onChangeYAxisForm')).toBeTruthy()
  })

  it('showProperty returns correct value', () => {
    const wrapper = shallowMount(YAxisSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['position'] },
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).showProperty('position')).toBe(true)
    expect((wrapper.vm as any).showProperty('axisValue')).toBe(false)
  })

  it('computes toolTip correctly', () => {
    const wrapper = shallowMount(YAxisSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: [] },
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).toolTip).toBe('light')
  })
})
