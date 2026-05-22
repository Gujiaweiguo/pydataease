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
vi.mock('@/store', () => ({ store: {} }))
vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  storeToRefs: vi.fn(() => ({})),
  createPinia: vi.fn()
}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: vi.fn()
}))
vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: vi.fn()
}))
vi.mock('@/views/chart/components/js/formatter', () => ({
  formatterItem: {},
  valueFormatter: vi.fn()
}))
vi.mock('@/views/chart/components/js/panel/common/common_table', () => ({
  getColumns: vi.fn(),
  getCustomTheme: vi.fn(() => ({})),
  getLeafNodes: vi.fn(() => [])
}))

import TableHeaderGroupConfig from '../TableHeaderGroupConfig.vue'

describe('TableHeaderGroupConfig', () => {
  const mockChart = {
    id: 'test-chart',
    type: 'table-info',
    xAxis: [],
    yAxis: [],
    customAttr: {
      tableHeader: {
        headerGroupConfig: { columns: [], meta: [] }
      },
      tableCell: {}
    }
  } as any

  it('renders component', () => {
    const wrapper = shallowMount(TableHeaderGroupConfig, {
      props: { chart: mockChart, themes: 'dark' },
      global: {
        stubs: {
          'el-button': true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains table-container element', () => {
    const wrapper = shallowMount(TableHeaderGroupConfig, {
      props: { chart: mockChart, themes: 'dark' },
      global: {
        stubs: {
          'el-button': true
        }
      }
    })
    expect(wrapper.find('.table-container').exists()).toBe(true)
  })

  it('contains button-group element', () => {
    const wrapper = shallowMount(TableHeaderGroupConfig, {
      props: { chart: mockChart, themes: 'dark' },
      global: {
        stubs: {
          'el-button': true
        }
      }
    })
    expect(wrapper.find('.button-group').exists()).toBe(true)
  })
})
