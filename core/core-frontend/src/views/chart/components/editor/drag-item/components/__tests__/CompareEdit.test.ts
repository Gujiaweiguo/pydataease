import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))

import CompareEdit from '../CompareEdit.vue'

const globalStubs = {
  ElForm: { template: '<form><slot /></form>', props: ['model'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label'] },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue', 'placeholder'] },
  ElOption: { template: '<option><slot /></option>', props: ['key', 'label', 'value'] },
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue'] },
  ElRadio: { template: '<label><slot /></label>', props: ['value'] }
}

const defaultProps = () => ({
  compareItem: {
    compareCalc: {
      field: '',
      type: 'none',
      resultData: 'percent',
      custom: { timeType: 'y_M_d' }
    }
  },
  chart: {
    type: 'bar',
    xAxis: [{ id: 'f1', deType: 1, name: 'date', dateStyle: 'y_M_d' }],
    xAxisExt: [],
    yAxis: []
  },
  dimensionData: [],
  quotaData: []
})

describe('CompareEdit', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(CompareEdit, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('initializes fieldList from chart xAxis with date fields', () => {
    const wrapper = shallowMount(CompareEdit, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.fieldList.length).toBeGreaterThan(0)
    expect(vm.state.fieldList[0].id).toBe('f1')
  })

  it('auto-selects first field when no field is set', () => {
    const props = defaultProps()
    props.compareItem.compareCalc.field = ''
    const wrapper = shallowMount(CompareEdit, {
      props,
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.fieldList.length).toBeGreaterThan(0)
    expect(props.compareItem.compareCalc.field).toBe('f1')
  })

  it('isIndicator is true when chart type is indicator', () => {
    const props = defaultProps()
    props.chart.type = 'indicator'
    const wrapper = shallowMount(CompareEdit, {
      props,
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.isIndicator).toBe(true)
  })

  it('isIndicator is false for non-indicator chart types', () => {
    const props = defaultProps()
    props.chart.type = 'bar'
    const wrapper = shallowMount(CompareEdit, {
      props,
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.isIndicator).toBe(false)
  })

  it('computes hintStr based on compareCalc settings', () => {
    const props = defaultProps()
    props.compareItem.compareCalc.field = 'f1'
    props.compareItem.compareCalc.type = 'day_mom'
    props.compareItem.compareCalc.resultData = 'percent'
    const wrapper = shallowMount(CompareEdit, {
      props,
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.hintStr).toBe('chart.compare_calc_day_percent')
  })
})
