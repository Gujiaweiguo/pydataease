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
  storeToRefs: vi.fn(() => ({ batchOptStatus: { value: false }, mobileInPc: { value: false } })),
  createPinia: vi.fn()
}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: vi.fn()
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: [],
  DEFAULT_TABLE_HEADER: {
    tableHeaderBgColor: '#f0f0f0',
    tableHeaderFontColor: '#000000',
    tableTitleFontSize: 12,
    tableHeaderAlign: 'left',
    tableTitleHeight: 36,
    isBolder: false,
    isItalic: false,
    showIndex: false,
    indexLabel: '',
    tableHeaderSort: false,
    showTableHeader: true,
    showHorizonBorder: true,
    showVerticalBorder: true,
    rowHeaderFreeze: false,
    headerGroup: false,
    headerGroupConfig: { columns: [], meta: [] },
    alignConfig: []
  }
}))
vi.mock('@/views/chart/components/js/util', () => ({
  convertToAlphaColor: vi.fn(c => c),
  isAlphaColor: vi.fn(() => false)
}))
vi.mock('@/views/chart/components/js/panel/common/common_table', () => ({
  getLeafNodes: vi.fn(() => [])
}))

import TableHeaderSelector from '../TableHeaderSelector.vue'

describe('TableHeaderSelector', () => {
  const mockChart = {
    type: 'table-info',
    customAttr: {
      basicStyle: { alpha: 100 },
      tableHeader: {
        tableHeaderBgColor: '#f0f0f0',
        tableHeaderFontColor: '#000000',
        tableTitleFontSize: 12,
        tableHeaderAlign: 'left',
        tableTitleHeight: 36,
        isBolder: false,
        isItalic: false,
        showIndex: false,
        indexLabel: '',
        tableHeaderSort: false,
        showTableHeader: true,
        showHorizonBorder: true,
        showVerticalBorder: true,
        rowHeaderFreeze: false,
        headerGroup: false,
        headerGroupConfig: { columns: [], meta: [] },
        alignConfig: []
      },
      tableCell: {}
    },
    xAxis: [],
    yAxis: []
  } as any

  it('renders component', () => {
    const wrapper = shallowMount(TableHeaderSelector, {
      props: { chart: mockChart, themes: 'dark' },
      global: {
        stubs: {
          'el-form': { template: '<div><slot /></div>' },
          'el-form-item': { template: '<div><slot /></div>' },
          'el-input': true,
          'el-select': true,
          'el-option': true,
          'el-checkbox': true,
          'el-icon': { template: '<div><slot /></div>' },
          'el-tooltip': { template: '<div><slot /></div>' },
          'el-color-picker': true,
          'el-input-number': true,
          'el-radio-group': { template: '<div><slot /></div>' },
          'el-radio': { template: '<div><slot /></div>' },
          'el-row': { template: '<div><slot /></div>' },
          'el-col': { template: '<div><slot /></div>' },
          'el-space': { template: '<div><slot /></div>' },
          'el-divider': true,
          'el-dialog': { template: '<div><slot /><slot name="header" /></div>' },
          Icon: { template: '<div><slot /></div>' },
          icon_bold_outlined: true,
          icon_italic_outlined: true,
          icon_leftAlignment_outlined: true,
          icon_centerAlignment_outlined: true,
          icon_rightAlignment_outlined: true,
          icon_customAlignment_outlined: true,
          icon_edit_outlined: true,
          'table-header-group-config': true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
