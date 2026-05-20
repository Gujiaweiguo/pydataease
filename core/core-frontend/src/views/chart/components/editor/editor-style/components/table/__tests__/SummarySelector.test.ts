import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/store', () => ({ store: {} }))
vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  storeToRefs: vi.fn(() => ({})),
  createPinia: vi.fn()
}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    batchOptStatus: { value: false }
  })
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  DEFAULT_BASIC_STYLE: {
    seriesSummary: [],
    showSummary: false,
    summaryLabel: '',
    alpha: 100
  }
}))

import SummarySelector from '../SummarySelector.vue'

describe('SummarySelector', () => {
  const mockChart = {
    id: 'test-chart',
    type: 'table-info',
    tableId: 'test-table',
    customAttr: {
      basicStyle: {
        showSummary: false,
        seriesSummary: [],
        summaryLabel: '',
        alpha: 100
      }
    },
    xAxis: [],
    yAxis: []
  }

  it('renders component', () => {
    const wrapper = shallowMount(SummarySelector, {
      props: { chart: mockChart, themes: 'dark' },
      global: {
        provide: {
          dimension: () => [],
          quota: () => []
        },
        stubs: {
          'el-form': { template: '<div><slot /></div>' },
          'el-form-item': { template: '<div><slot /></div>' },
          'el-input': true,
          'el-select': true,
          'el-option': true,
          'el-checkbox': true,
          'el-icon': { template: '<div><slot /></div>' },
          'el-dialog': { template: '<div><slot /><slot name="footer" /></div>' },
          'el-button': true,
          'el-col': { template: '<div><slot /></div>' },
          Setting: true,
          'custom-aggr-edit': true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
