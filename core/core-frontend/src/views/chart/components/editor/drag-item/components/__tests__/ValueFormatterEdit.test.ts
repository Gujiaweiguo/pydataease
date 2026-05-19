import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/views/chart/components/js/formatter', () => ({
  isEnLocal: false,
  formatterType: [
    { name: 'value_formatter_auto', value: 'auto' },
    { name: 'value_formatter_value', value: 'value' },
    { name: 'value_formatter_percent', value: 'percent' }
  ],
  getUnitTypeList: () => [
    { name: '无', value: 1 },
    { name: '千', value: 1000 },
    { name: '万', value: 10000 }
  ],
  onChangeFormatCfgUnitLanguage: () => undefined,
  valueFormatter: (val: number) => String(val),
  initFormatCfgUnit: () => undefined
}))

import ValueFormatterEdit from '../ValueFormatterEdit.vue'

const globalStubs = {
  ElForm: { template: '<form><slot /></form>', props: ['model'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label'] },
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue'] },
  ElRadio: { template: '<label><slot /></label>', props: ['value'] },
  ElInputNumber: {
    template: '<input type="number" />',
    props: ['modelValue', 'min', 'max', 'controlsPosition']
  },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue', 'placeholder'] },
  ElOption: { template: '<option><slot /></option>', props: ['key', 'label', 'value'] },
  ElInput: {
    template: '<input />',
    props: ['modelValue', 'clearable', 'maxlength', 'placeholder']
  },
  ElCheckbox: { template: '<input type="checkbox" />', props: ['modelValue', 'label'] },
  ElRow: { template: '<div><slot /></div>', props: ['gutter'] },
  ElCol: { template: '<div><slot /></div>', props: ['span'] }
}

const defaultProps = () => ({
  formatterItem: {
    formatterCfg: {
      type: 'auto',
      unitLanguage: 'ch',
      unit: 1,
      suffix: '',
      decimalCount: 2,
      thousandSeparator: true
    }
  },
  chart: { type: 'bar' }
})

describe('ValueFormatterEdit', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(ValueFormatterEdit, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('initializes typeList from formatter module', () => {
    const wrapper = shallowMount(ValueFormatterEdit, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.typeList.length).toBe(3)
  })

  it('computes exampleResult from initial value', () => {
    const wrapper = shallowMount(ValueFormatterEdit, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.exampleResult).toBeDefined()
    expect(typeof vm.state.exampleResult).toBe('string')
  })

  it('initializes formatterCfg if not present', () => {
    const props = defaultProps()
    ;(props.formatterItem as any).formatterCfg = undefined
    const wrapper = shallowMount(ValueFormatterEdit, {
      props,
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
