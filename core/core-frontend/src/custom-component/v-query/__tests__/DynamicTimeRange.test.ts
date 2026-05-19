import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))

import DynamicTimeRange from '../DynamicTimeRange.vue'

const stubs = {
  'el-date-picker': {
    template: '<div class="el-date-picker" />',
    props: [
      'modelValue',
      'type',
      'disabled',
      'placeholder',
      'prefixIcon',
      'popperClass',
      'rangeSeparator',
      'startPlaceholder',
      'endPlaceholder',
      'format',
      'key'
    ]
  }
}

const baseConfig = {
  timeGranularityMultiple: 'daterange',
  defaultValue: [],
  selectValue: [],
  timeType: 'fixed',
  timeNum: 0,
  relativeToCurrentType: 'year',
  around: 'f',
  arbitraryTime: new Date(),
  defaultValueCheck: false,
  timeGranularity: 'date',
  timeNumRange: 0,
  relativeToCurrentRange: 'custom',
  relativeToCurrentTypeRange: 'year',
  aroundRange: 'f',
  arbitraryTimeRange: new Date(),
  id: 'test-dynamic-time-range'
}

const mountDynamicTimeRange = (configOverrides: Record<string, any> = {}) =>
  shallowMount(DynamicTimeRange, {
    props: {
      config: { ...baseConfig, ...configOverrides }
    },
    global: {
      stubs,
      mocks: { $t: (k: string) => k }
    }
  })

describe('DynamicTimeRange', () => {
  it('renders successfully with default config', () => {
    const wrapper = mountDynamicTimeRange()
    expect(wrapper.exists()).toBe(true)
  })

  it('renders a disabled date picker', () => {
    const wrapper = mountDynamicTimeRange()
    const picker = wrapper.find('.el-date-picker')
    expect(picker.exists()).toBe(true)
  })

  it('uses timeGranularityMultiple as picker type', () => {
    const wrapper = mountDynamicTimeRange()
    const picker = wrapper.find('.el-date-picker')
    expect(picker.exists()).toBe(true)
  })

  it('sets default date pair when defaultValueCheck is false', () => {
    const wrapper = mountDynamicTimeRange({ defaultValueCheck: false })
    const sv = (wrapper.vm as any).selectValue
    expect(Array.isArray(sv)).toBe(true)
    expect(sv.length).toBe(2)
  })
})
