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
    mobileInPc: { value: false }
  })
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: [],
  DEFAULT_TABLE_CELL: {
    tableItemBgColor: '#ffffff',
    tableItemSubBgColor: '#f5f5f5',
    tableFontColor: '#000000',
    tableItemFontSize: 12,
    tableItemAlign: 'left',
    tableItemHeight: 40,
    enableTableCrossBG: false,
    isBolder: false,
    isItalic: false,
    tableFreeze: false,
    tableColumnFreezeHead: 0,
    tableRowFreezeHead: 0,
    mergeCells: false,
    showHorizonBorder: true,
    showVerticalBorder: true,
    alignConfig: []
  }
}))
vi.mock('@/views/chart/components/js/util', () => ({
  convertToAlphaColor: vi.fn((c, _a) => c),
  isAlphaColor: vi.fn(() => false)
}))

import TableCellSelector from '../TableCellSelector.vue'

describe('TableCellSelector', () => {
  const mockChart = {
    type: 'table-info',
    customAttr: {
      basicStyle: { alpha: 100 },
      tableCell: {
        tableItemBgColor: '#ffffff',
        tableItemSubBgColor: '#f5f5f5',
        tableFontColor: '#000000',
        tableItemFontSize: 12,
        tableItemAlign: 'left',
        tableItemHeight: 40,
        enableTableCrossBG: false,
        isBolder: false,
        isItalic: false,
        tableFreeze: false,
        tableColumnFreezeHead: 0,
        tableRowFreezeHead: 0,
        mergeCells: false,
        showHorizonBorder: true,
        showVerticalBorder: true,
        alignConfig: []
      },
      tableHeader: {}
    },
    xAxis: [],
    yAxis: []
  }

  it('renders component', () => {
    const wrapper = shallowMount(TableCellSelector, {
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
          Icon: { template: '<div><slot /></div>' },
          icon_bold_outlined: true,
          icon_italic_outlined: true,
          icon_leftAlignment_outlined: true,
          icon_centerAlignment_outlined: true,
          icon_rightAlignment_outlined: true,
          icon_customAlignment_outlined: true,
          icon_info_outlined: true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
