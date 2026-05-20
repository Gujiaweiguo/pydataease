import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/api/watermark', () => ({
  watermarkFind: vi.fn(() => Promise.resolve({ data: { settingContent: '{}' } })),
  watermarkSave: vi.fn(() => Promise.resolve())
}))
vi.mock('@/api/user', () => ({
  personInfoApi: vi.fn(() => Promise.resolve({ data: {} }))
}))
vi.mock('@/components/watermark/watermark', () => ({
  watermark: vi.fn(),
  getNow: vi.fn(() => '2026-01-01')
}))

import Watermark from '../index.vue'

describe('Watermark', () => {
  const stubs = {
    ElRow: { template: '<div><slot /></div>' },
    ElCol: { template: '<div><slot /></div>', props: ['span'] },
    ElForm: { template: '<form><slot /></form>', props: ['model', 'labelWidth'] },
    ElFormItem: { template: '<div><slot /></div>', props: ['label', 'style'] },
    ElSwitch: { template: '<input type="checkbox" />', props: ['modelValue', 'disabled'] },
    ElCheckbox: { template: '<input type="checkbox" />', props: ['modelValue', 'disabled'] },
    ElSelect: { template: '<select><slot /></select>', props: ['modelValue', 'disabled'] },
    ElOption: { template: '<option><slot /></option>', props: ['label', 'value'] },
    ElInput: { template: '<textarea />', props: ['modelValue', 'disabled', 'type', 'autosize'] },
    ElColorPicker: { template: '<input />', props: ['modelValue', 'disabled', 'predefine'] },
    ElInputNumber: { template: '<input />', props: ['modelValue', 'disabled', 'min', 'max'] },
    ElButton: { template: '<button><slot /></button>', props: ['type'] },
    ParamsTips: { template: '<div />' }
  }

  it('renders component', () => {
    const wrapper = shallowMount(Watermark, {
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has watermark-table__content class', () => {
    const wrapper = shallowMount(Watermark, {
      global: { stubs }
    })
    expect(wrapper.find('.watermark-table__content').exists()).toBe(true)
  })
})
