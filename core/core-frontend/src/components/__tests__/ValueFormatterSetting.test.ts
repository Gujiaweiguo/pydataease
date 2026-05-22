import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const formatterMock = vi.hoisted(() => ({
  formatterType: [
    { name: 'auto', value: 'auto' },
    { name: 'number', value: 'number' },
    { name: 'percent', value: 'percent' }
  ],
  getUnitTypeList: vi.fn((lang: string) => [{ name: `${lang}-unit`, value: `${lang}-unit` }]),
  onChangeFormatCfgUnitLanguage: vi.fn(),
  valueFormatter: vi.fn(
    (value: number, cfg: Record<string, unknown>) =>
      `${value}:${cfg.type}:${cfg.unitLanguage}:${cfg.unit}:${cfg.suffix}:${cfg.thousandSeparator}`
  ),
  initFormatCfgUnit: vi.fn(),
  isEnLocal: false
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => `t:${key}` })
}))

vi.mock('@/views/chart/components/js/formatter', () => formatterMock)

import ValueFormatterSetting from '@/components/dashboard/subject-setting/dashboard-style/ValueFormatterSetting.vue'

const ElFormStub = defineComponent({
  name: 'ElForm',
  props: ['model', 'effect', 'labelPosition'],
  template: '<form class="el-form-stub"><slot /></form>'
})

const ElFormItemStub = defineComponent({
  name: 'ElFormItem',
  props: ['label', 'effect'],
  template: '<div class="el-form-item-stub" :data-label="label"><slot /></div>'
})

const ElRadioGroupStub = defineComponent({
  name: 'ElRadioGroup',
  props: ['modelValue', 'effect'],
  emits: ['change'],
  template: '<div class="radio-group-stub"><slot /></div>'
})

const ElRadioStub = defineComponent({
  name: 'ElRadio',
  props: ['label', 'effect'],
  template: '<label class="radio-stub" :data-label="label"><slot /></label>'
})

const ElInputNumberStub = defineComponent({
  name: 'ElInputNumber',
  props: ['modelValue', 'effect', 'min', 'max'],
  emits: ['change'],
  template: '<div class="input-number-stub" :data-value="String(modelValue)"></div>'
})

const ElSelectStub = defineComponent({
  name: 'ElSelect',
  props: ['modelValue', 'effect', 'placeholder'],
  emits: ['change'],
  template: '<div class="select-stub"><slot /></div>'
})

const ElOptionStub = defineComponent({
  name: 'ElOption',
  props: ['label', 'value', 'effect'],
  template: '<div class="option-stub" :data-value="value">{{ label }}</div>'
})

const ElInputStub = defineComponent({
  name: 'ElInput',
  props: ['modelValue', 'effect', 'placeholder'],
  emits: ['change'],
  template: '<div class="input-stub"><slot /></div>'
})

const ElCheckboxStub = defineComponent({
  name: 'ElCheckbox',
  props: ['modelValue', 'effect', 'label'],
  emits: ['change'],
  template: '<label class="checkbox-stub"><slot />{{ label }}</label>'
})

const mountComponent = (formatterCfg: BaseFormatter) =>
  mount(ValueFormatterSetting, {
    props: {
      formatterCfg,
      themes: 'dark'
    },
    global: {
      stubs: {
        ElForm: ElFormStub,
        ElFormItem: ElFormItemStub,
        ElRadioGroup: ElRadioGroupStub,
        ElRadio: ElRadioStub,
        ElInputNumber: ElInputNumberStub,
        ElSelect: ElSelectStub,
        ElOption: ElOptionStub,
        ElInput: ElInputStub,
        ElCheckbox: ElCheckboxStub,
        ElRow: { template: '<div class="row-stub"><slot /></div>' },
        ElCol: { template: '<div class="col-stub"><slot /></div>' }
      }
    }
  })

describe('ValueFormatterSetting', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders formatter options and the formatted example text', () => {
    const wrapper = mountComponent({
      type: 'number',
      decimalCount: 2,
      unitLanguage: 'ch',
      unit: 1,
      suffix: '元',
      thousandSeparator: true,
      showTotalPercent: false
    })

    expect(wrapper.findAll('.radio-stub')).toHaveLength(3)
    expect(wrapper.text()).toContain('t:chart.auto')
    expect(wrapper.text()).toContain('20000000:number:ch:1:元:true')
  })

  it('toggles formatter-specific fields based on formatter type', () => {
    const autoWrapper = mountComponent({
      type: 'auto',
      decimalCount: 2,
      unitLanguage: 'ch',
      unit: 1,
      suffix: '',
      thousandSeparator: false,
      showTotalPercent: false
    })
    const percentWrapper = mountComponent({
      type: 'percent',
      decimalCount: 1,
      unitLanguage: 'en',
      unit: 1,
      suffix: '%',
      thousandSeparator: false,
      showTotalPercent: false
    })

    expect(autoWrapper.findComponent(ElInputNumberStub).exists()).toBe(false)
    expect(percentWrapper.findAllComponents(ElSelectStub)).toHaveLength(0)
  })

  it('emits formatter changes when the decimal input changes', async () => {
    const formatterCfg: BaseFormatter = {
      type: 'number',
      decimalCount: 2,
      unitLanguage: 'ch',
      unit: 1,
      suffix: '',
      thousandSeparator: false,
      showTotalPercent: false
    }
    const wrapper = mountComponent(formatterCfg)

    await wrapper.getComponent(ElInputNumberStub).vm.$emit('change', 4)

    expect(wrapper.emitted('onFormatterItemChange')).toEqual([[formatterCfg]])
  })

  it('updates unit language through the formatter helper', async () => {
    const formatterCfg: BaseFormatter = {
      type: 'number',
      decimalCount: 2,
      unitLanguage: 'ch',
      unit: 1,
      suffix: '',
      thousandSeparator: false,
      showTotalPercent: false
    }
    const wrapper = mountComponent(formatterCfg)

    await wrapper.findAllComponents(ElSelectStub)[0].vm.$emit('change', 'en')

    expect(formatterMock.onChangeFormatCfgUnitLanguage).toHaveBeenCalledWith(formatterCfg, 'en')
    expect(formatterMock.valueFormatter).toHaveBeenCalled()
  })
})
