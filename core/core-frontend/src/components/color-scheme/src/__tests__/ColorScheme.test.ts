import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/assets/svg/icon_admin_outlined.svg', () => ({ default: '' }))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_CASES: [
    { name: 'Default', value: 'default', colors: ['#5470C6', '#91CC75', '#FAC858'] },
    { name: 'Retro', value: 'retro', colors: ['#E76F51', '#2A9D8F', '#264653'] }
  ],
  COLOR_PANEL: ['#5470C6', '#91CC75', '#FAC858', '#EE6666']
}))
vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (k: string) => k
  })
}))

import ColorScheme from '../ColorScheme.vue'

describe('ColorScheme', () => {
  const globalConfig = {
    global: {
      stubs: {
        'el-select': { template: '<select><slot /></select>', props: ['modelValue', 'size', 'placeholder'] },
        'el-option': { template: '<option><slot /></option>', props: ['key', 'label', 'value'] },
        'el-button': { template: '<button><slot /><slot name="icon" /></button>', props: ['style', 'size', 'plain'] },
        'el-color-picker': { template: '<input type="color" />', props: ['modelValue', 'predefine'] }
      },
      mocks: { $t: (k: string) => k }
    }
  }

  it('should render without errors', () => {
    const wrapper = shallowMount(ColorScheme, globalConfig)
    expect(wrapper.find('.color-scheme').exists()).toBe(true)
  })

  it('should contain color select section', () => {
    const wrapper = shallowMount(ColorScheme, globalConfig)
    expect(wrapper.find('.color-select').exists()).toBe(true)
  })
})
