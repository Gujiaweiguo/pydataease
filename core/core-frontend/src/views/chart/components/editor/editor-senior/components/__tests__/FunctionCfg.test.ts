import { nextTick } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios', () => ({}))
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (key: string) => key }) }))
vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div />' },
  loadPlugin: () => undefined
}))
vi.mock('@/config/axios/hmac', () => ({}))

import FunctionCfg from '../FunctionCfg.vue'

const globalStubs = {
  ElForm: { template: '<form class="form-stub"><slot /></form>' },
  ElFormItem: {
    props: ['label'],
    template: '<div class="form-item-stub" :data-label="label"><slot /></div>'
  },
  ElCheckbox: { props: ['modelValue'], template: '<label class="checkbox-stub"><slot /></label>' },
  ElTooltip: { template: '<div class="tooltip-stub"><slot /><slot name="content" /></div>' },
  ElIcon: { template: '<i class="icon-stub"><slot /></i>' },
  ElSlider: { props: ['modelValue'], template: '<div class="slider-stub" />' },
  ElColorPicker: { props: ['modelValue'], template: '<div class="color-picker-stub" />' },
  ElRadioGroup: { props: ['modelValue'], template: '<div class="radio-group-stub"><slot /></div>' },
  ElRadio: {
    props: ['label'],
    template: '<label class="radio-stub" :data-label="label"><slot /></label>'
  },
  ElInput: { props: ['modelValue'], template: '<input class="input-stub" />' },
  ElSelect: { props: ['modelValue'], template: '<select class="select-stub"><slot /></select>' },
  ElOption: {
    props: ['label', 'value'],
    template: '<option class="option-stub" :value="value">{{ label }}</option>'
  },
  Icon: { template: '<span class="vant-icon-stub"><slot /></span>' }
}

const createChart = (type = 'table-normal') => ({
  type,
  senior: {
    functionCfg: {
      sliderShow: true,
      sliderRange: [5, 30],
      sliderBg: '#111111',
      sliderFillBg: '#222222',
      sliderTextColor: '#333333',
      emptyDataStrategy: 'setZero',
      emptyDataFieldCtrl: ['sales']
    }
  },
  yAxis: [
    { groupType: 'q', name: 'Sales', dataeaseName: 'sales' },
    { groupType: 'd', name: 'Region', dataeaseName: 'region' }
  ],
  xAxis: [{ groupType: 'q', name: 'Orders', dataeaseName: 'orders' }]
})

const mountComponent = (chart = createChart(), propertyInner = ['slider', 'emptyDataStrategy']) =>
  shallowMount(FunctionCfg, {
    props: {
      chart,
      themes: 'dark',
      propertyInner
    },
    global: {
      stubs: globalStubs
    }
  })

describe('FunctionCfg', () => {
  it('initializes field options for table metrics when empty field control is shown', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    expect(vm.showEmptyDataFieldCtrl).toBe(true)
    expect(vm.fieldOptions).toEqual([{ label: 'Sales', value: 'sales' }])
  })

  it('treats rich-text charts as custom-value capable and renders the custom input', async () => {
    const wrapper = mountComponent(createChart('rich-text'), ['emptyDataStrategy'])
    const vm = wrapper.vm as any

    vm.state.functionForm.emptyDataStrategy = 'custom'
    await nextTick()

    expect(vm.isRichText).toBe(true)
    expect(wrapper.find('.input-stub').exists()).toBe(true)
  })

  it('hides ignore-data option for indicator charts', () => {
    const wrapper = mountComponent(createChart('indicator'), ['emptyDataStrategy'])

    expect((wrapper.vm as any).showIgnoreOption).toBe(false)
  })

  it('emits the latest function config when changeFunctionCfg is called', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.state.functionForm.sliderShow = false
    vm.changeFunctionCfg()

    expect(wrapper.emitted('onFunctionCfgChange')).toEqual([[vm.state.functionForm]])
  })
})
