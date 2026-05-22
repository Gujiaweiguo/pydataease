import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  DEFAULT_BASIC_STYLE: {
    quotaPosition: 'col',
    tableLayoutMode: 'grid'
  },
  DEFAULT_TABLE_TOTAL: {
    row: {
      showGrandTotals: false,
      showSubTotals: false,
      reverseLayout: false,
      reverseSubLayout: false,
      label: '',
      subLabel: '',
      totalSort: 'none',
      totalSortField: '',
      calcTotals: { cfg: [] },
      calcSubTotals: { cfg: [] },
      subTotalsDimensions: [],
      subTotalsDimensionsNew: false
    },
    col: {
      showGrandTotals: false,
      showSubTotals: false,
      reverseLayout: false,
      reverseSubLayout: false,
      label: '',
      subLabel: '',
      totalSort: 'none',
      totalSortField: '',
      calcTotals: { cfg: [] },
      calcSubTotals: { cfg: [] }
    }
  }
}))

import TableTotalSelector from '../TableTotalSelector.vue'

describe('TableTotalSelector', () => {
  const mockChart = {
    id: 'test-chart',
    type: 'table-pivot',
    tableId: 'test-table',
    xAxis: [],
    xAxisExt: [],
    yAxis: [],
    customAttr: {
      basicStyle: {
        quotaPosition: 'col',
        tableLayoutMode: 'grid'
      },
      tableTotal: {
        row: {
          showGrandTotals: false,
          showSubTotals: false,
          reverseLayout: false,
          reverseSubLayout: false,
          label: '',
          subLabel: '',
          totalSort: 'none',
          totalSortField: '',
          calcTotals: { cfg: [] },
          calcSubTotals: { cfg: [] },
          subTotalsDimensions: [],
          subTotalsDimensionsNew: false
        },
        col: {
          showGrandTotals: false,
          showSubTotals: false,
          reverseLayout: false,
          reverseSubLayout: false,
          label: '',
          subLabel: '',
          totalSort: 'none',
          totalSortField: '',
          calcTotals: { cfg: [] },
          calcSubTotals: { cfg: [] }
        }
      }
    }
  } as any

  it('renders component', () => {
    const wrapper = shallowMount(TableTotalSelector, {
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
          'el-radio-group': { template: '<div><slot /></div>' },
          'el-radio': { template: '<div><slot /></div>' },
          'el-divider': true,
          'el-col': { template: '<div><slot /></div>' },
          'el-icon': { template: '<div><slot /></div>' },
          'el-dialog': { template: '<div><slot /><slot name="footer" /></div>' },
          'el-button': true,
          Setting: true,
          'custom-aggr-edit': true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
