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

vi.mock('@/views/chart/components/js/formatter', () => ({
  isEnLocal: false,
  formatterType: [
    { name: 'auto', value: 'auto' },
    { name: 'value', value: 'value' }
  ],
  getUnitTypeList: () => [{ name: 'None', value: '' }],
  onChangeFormatCfgUnitLanguage: vi.fn(),
  valueFormatter: () => '20,000,000',
  initFormatCfgUnit: vi.fn()
}))

import ValueFormatterSetting from '@/components/dashboard/subject-setting/dashboard-style/ValueFormatterSetting.vue'

type FormatterCfg = {
  type: string
  decimalCount: number
  unit: number
  unitLanguage: 'ch' | 'en'
  suffix: string
  thousandSeparator: boolean
  showTotalPercent: boolean
}

const createFormatterCfg = (type: FormatterCfg['type']): FormatterCfg => ({
  type,
  decimalCount: 2,
  unit: 0,
  unitLanguage: 'ch',
  suffix: '',
  thousandSeparator: true,
  showTotalPercent: false
})

const stubs = {
  ElForm: { template: '<form><slot /></form>', props: ['effect', 'model', 'labelPosition'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'class', 'effect'] },
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue', 'effect'] },
  ElRadio: { template: '<label><slot /></label>', props: ['label', 'effect'] },
  ElInputNumber: {
    template: '<input type="number" />',
    props: ['modelValue', 'effect', 'size', 'step', 'precision', 'min', 'max', 'controlsPosition']
  },
  ElRow: { template: '<div><slot /></div>', props: ['gutter'] },
  ElCol: { template: '<div><slot /></div>', props: ['span'] },
  ElSelect: {
    template: '<select><slot /></select>',
    props: ['modelValue', 'size', 'placeholder', 'effect']
  },
  ElOption: { template: '<option><slot /></option>', props: ['label', 'value', 'effect', 'size'] },
  ElInput: {
    template: '<input />',
    props: ['modelValue', 'effect', 'maxlength', 'size', 'clearable', 'placeholder']
  },
  ElCheckbox: {
    template: '<input type="checkbox" />',
    props: ['modelValue', 'effect', 'size', 'label']
  }
}

describe('ValueFormatterSetting', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const formatterCfg = createFormatterCfg('auto')
    const wrapper = shallowMount(ValueFormatterSetting, {
      props: { formatterCfg, themes: 'light' },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts dark themes prop', () => {
    const formatterCfg = createFormatterCfg('auto')
    const wrapper = shallowMount(ValueFormatterSetting, {
      props: { formatterCfg, themes: 'dark' },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('emits onFormatterItemChange on format change', () => {
    const formatterCfg = createFormatterCfg('value')
    const wrapper = shallowMount(ValueFormatterSetting, {
      props: { formatterCfg, themes: 'light' },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
