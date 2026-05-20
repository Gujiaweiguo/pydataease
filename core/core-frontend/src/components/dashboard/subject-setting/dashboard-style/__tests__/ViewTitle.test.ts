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

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#5470c6']
}))

import ViewTitle from '@/components/dashboard/subject-setting/dashboard-style/ViewTitle.vue'

const stubs = {
  ElCol: { template: '<div><slot /></div>' },
  ElForm: { template: '<form><slot /></form>', props: ['model', 'labelWidth', 'size'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'class'] },
  ElCheckbox: { template: '<input type="checkbox" />', props: ['modelValue'] },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue', 'size', 'placeholder'] },
  ElOption: { template: '<option><slot /></option>', props: ['label', 'value'] },
  ElColorPicker: { template: '<div />', props: ['modelValue', 'class', 'predefine'] },
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue', 'size'] },
  ElRadioButton: { template: '<label><slot /></label>', props: ['label'] }
}

describe('ViewTitle', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(ViewTitle, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders root div', () => {
    const wrapper = shallowMount(ViewTitle, { global: { stubs } })
    expect(wrapper.find('div').exists()).toBe(true)
  })
})
