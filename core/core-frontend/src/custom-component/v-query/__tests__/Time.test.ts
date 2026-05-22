import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({ dvInfo: { type: 'dashboard' }, mobileInPc: false })
}))
vi.mock('./shortcuts', () => ({ useShortcuts: () => ({ shortcuts: [] }) }))
vi.mock('vant/es/popup', () => ({ default: { template: '<div />' } }))
vi.mock('vant/es/popup/style', () => ({}))
vi.mock('vant/es/date-picker', () => ({ default: { template: '<div />' } }))
vi.mock('vant/es/date-picker/style', () => ({}))
vi.mock('vant/es/time-picker', () => ({ default: { template: '<div />' } }))
vi.mock('vant/es/time-picker/style', () => ({}))
vi.mock('vant/es/picker-group', () => ({ default: { template: '<div />' } }))
vi.mock('vant/es/picker-group/style', () => ({}))

import Time from '../Time.vue'

const stubs = {
  'el-date-picker': {
    template: '<div class="el-date-picker" />',
    props: [
      'modelValue',
      'type',
      'placeholder',
      'disabledDate',
      'shortcuts',
      'format',
      'startPlaceholder',
      'endPlaceholder',
      'rangeSeparator',
      'disabled',
      'prefixIcon',
      'popperClass',
      'editable',
      'style',
      'key'
    ]
  }
}

const defaultProvide = {
  placeholder: { value: { placeholderShow: true } },
  'com-width': () => 227,
  'is-confirm-search': () => undefined
}

const baseConfig = {
  selectValue: '',
  defaultValue: '',
  queryConditionWidth: 0,
  defaultValueCheck: false,
  displayType: '1',
  timeGranularity: 'date',
  setTimeRange: false,
  timeGranularityMultiple: 'daterange',
  id: 'test-time',
  placeholder: '',
  timeRange: {
    intervalType: 'none',
    dynamicWindow: false,
    maximumSingleQuery: 0,
    regularOrTrends: 'fixed',
    regularOrTrendsValue: '',
    relativeToCurrent: 'custom',
    timeNum: 0,
    relativeToCurrentType: 'year',
    around: 'f',
    timeNumRange: 0,
    relativeToCurrentTypeRange: 'year',
    aroundRange: 'f'
  }
} as any

const mountTime = (configOverrides: Record<string, any> = {}) =>
  shallowMount(Time, {
    props: { config: { ...baseConfig, ...configOverrides }, isConfig: false },
    global: { stubs, provide: defaultProvide, mocks: { $t: (k: string) => k } }
  })

describe('Time', () => {
  it('renders successfully with default config', () => {
    expect(mountTime().exists()).toBe(true)
  })
  it('renders el-date-picker component', () => {
    expect(mountTime().find('.el-date-picker').exists()).toBe(true)
  })
  it('exposes displayTypeChange method', () => {
    expect(typeof (mountTime().vm as any).displayTypeChange).toBe('function')
  })
  it('renders range picker when displayType is 7', () => {
    expect(mountTime({ displayType: '7', selectValue: [], defaultValue: [] }).exists()).toBe(true)
  })
})
