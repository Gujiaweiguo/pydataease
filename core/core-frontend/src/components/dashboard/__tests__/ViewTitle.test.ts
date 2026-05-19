import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#000000', '#ffffff']
}))

vi.mock('@/config/axios', () => ({}))

import ViewTitle from '@/components/dashboard/subject-setting/dashboard-style/ViewTitle.vue'

const stubs = {
  ElCol: { template: '<div><slot /></div>' },
  ElForm: { template: '<form><slot /></form>', props: ['model', 'labelWidth', 'size'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'class'] },
  ElCheckbox: { template: '<input type="checkbox" />', props: ['modelValue'] },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue', 'placeholder', 'size'] },
  ElOption: { template: '<option><slot /></option>', props: ['label', 'value'] },
  ElColorPicker: { template: '<input type="color" />', props: ['modelValue', 'predefine'] },
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

  it('renders the show checkbox', () => {
    const wrapper = shallowMount(ViewTitle, { global: { stubs } })
    expect(wrapper.findAll('input[type="checkbox"]').length).toBeGreaterThan(0)
  })

  it('emits onTextChange when checkbox changes', async () => {
    const wrapper = shallowMount(ViewTitle, { global: { stubs } })
    const checkbox = wrapper.find('input[type="checkbox"]')
    await checkbox.trigger('change')
    expect(wrapper.emitted('onTextChange')).toBeTruthy()
  })
})
