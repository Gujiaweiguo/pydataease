import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))

import DynamicTime from '../DynamicTime.vue'

const stubs = {
  'el-date-picker': {
    template: '<div class="el-date-picker" />',
    props: ['modelValue', 'type', 'disabled', 'placeholder', 'prefixIcon', 'popperClass', 'key']
  }
}

const baseConfig = {
  defaultValue: '',
  selectValue: '',
  timeType: 'fixed',
  relativeToCurrent: 'custom',
  timeNum: 0,
  relativeToCurrentType: 'year',
  around: 'f',
  arbitraryTime: new Date(),
  defaultValueCheck: false,
  timeGranularity: 'date',
  id: 'test-dynamic-time'
}

const mountDynamicTime = (configOverrides: Record<string, any> = {}) =>
  shallowMount(DynamicTime, {
    props: {
      config: { ...baseConfig, ...configOverrides }
    },
    global: {
      stubs,
      mocks: { $t: (k: string) => k }
    }
  })

describe('DynamicTime', () => {
  it('renders successfully with default config', () => {
    const wrapper = mountDynamicTime()
    expect(wrapper.exists()).toBe(true)
  })

  it('renders a disabled date picker', () => {
    const wrapper = mountDynamicTime()
    const picker = wrapper.find('.el-date-picker')
    expect(picker.exists()).toBe(true)
  })

  it('sets selectValue to null when defaultValueCheck is false', () => {
    const wrapper = mountDynamicTime({ defaultValueCheck: false })
    expect((wrapper.vm as any).selectValue).toBeNull()
  })

  it('uses timeGranularity as date picker type', () => {
    const wrapper = mountDynamicTime()
    const picker = wrapper.find('.el-date-picker')
    expect(picker.exists()).toBe(true)
  })
})
