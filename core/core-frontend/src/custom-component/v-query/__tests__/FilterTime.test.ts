import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))

import FilterTime from '../FilterTime.vue'

const stubs = {
  'el-radio-group': {
    template: '<div class="el-radio-group"><slot /></div>',
    props: ['modelValue']
  },
  'el-radio': { template: '<label class="el-radio"><slot /></label>', props: ['label', 'value'] },
  'el-select': {
    template: '<select class="el-select"><slot /></select>',
    props: ['modelValue', 'teleported']
  },
  'el-option': { template: '<option><slot /></option>', props: ['label', 'value', 'key'] },
  'el-input-number': {
    template: '<input type="number" class="el-input-number" />',
    props: ['modelValue', 'min', 'controlsPosition', 'stepStrictly']
  },
  DynamicTimeFiltering: { template: '<div class="dynamic-time-filtering" />' },
  DynamicTimeRangeFiltering: { template: '<div class="dynamic-time-range-filtering" />' },
  DynamicTime: {
    template: '<div class="dynamic-time" />',
    props: ['config', 'timeGranularityMultiple']
  },
  DynamicTimeRange: {
    template: '<div class="dynamic-time-range" />',
    props: ['config', 'timeGranularityMultiple']
  }
}

const mountFilterTime = (propsOverrides: Record<string, any> = {}) =>
  shallowMount(FilterTime, {
    props: {
      timeRange: {
        intervalType: 'none',
        dynamicWindow: false,
        maximumSingleQuery: 0,
        regularOrTrends: 'fixed',
        relativeToCurrentRange: 'custom',
        regularOrTrendsValue: '',
        relativeToCurrent: 'custom',
        timeNum: 0,
        relativeToCurrentType: 'year',
        around: 'f',
        timeNumRange: 0,
        relativeToCurrentTypeRange: 'year',
        aroundRange: 'f'
      },
      timeGranularity: 'date',
      ...propsOverrides
    },
    global: { stubs }
  })

describe('FilterTime', () => {
  it('renders successfully with default props', () => {
    const wrapper = mountFilterTime()
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the set-time-filtering-range container', () => {
    const wrapper = mountFilterTime()
    expect(wrapper.find('.set-time-filtering-range').exists()).toBe(true)
  })

  it('renders interval type radio group', () => {
    const wrapper = mountFilterTime()
    expect(wrapper.find('.el-radio-group').exists()).toBe(true)
  })

  it('hides settings section when intervalType is none', () => {
    const wrapper = mountFilterTime()
    const listItems = wrapper.findAll('.list-item')
    expect(listItems.length).toBe(1)
  })
})
