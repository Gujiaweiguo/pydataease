import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/api/chart', () => ({ getData: vi.fn() }))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    addViewTrackFilter: vi.fn(),
    setViewDataDetails: vi.fn()
  })
}))
vi.mock('@/utils/canvasStyle', () => ({
  customAttrTrans: {},
  customStyleTrans: {},
  recursionTransObj: vi.fn()
}))
vi.mock('@/utils/utils', () => ({ deepCopy: vi.fn(x => x), isMobile: vi.fn(() => false) }))
vi.mock('lodash-es', () => ({
  cloneDeep: vi.fn(x => JSON.parse(JSON.stringify(x))),
  defaultsDeep: vi.fn((a, b) => ({ ...b, ...a })),
  defaultTo: vi.fn((v, d) => v ?? d)
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  BASE_VIEW_CONFIG: { customAttr: { basicStyle: {} } },
  CHART_FONT_FAMILY_MAP: {},
  DEFAULT_INDICATOR_NAME_STYLE: {
    color: '#999',
    fontSize: 14,
    fontFamily: 'inherit',
    isBolder: false,
    isItalic: false,
    letterSpace: 0,
    fontShadow: false,
    nameValueSpacing: 0
  },
  DEFAULT_INDICATOR_STYLE: {
    color: '#5470C6',
    backgroundColor: 'transparent',
    fontSize: 20,
    fontFamily: 'inherit',
    isBolder: false,
    isItalic: false,
    letterSpace: 0,
    fontShadow: false,
    suffixEnable: false,
    suffixFontSize: 14,
    suffixFontFamily: 'inherit',
    suffixIsBolder: false,
    suffixIsItalic: false,
    suffixLetterSpace: 0,
    suffixFontShadow: false,
    suffixColor: '#999'
  }
}))
vi.mock('@/views/chart/components/js/formatter', () => ({
  valueFormatter: vi.fn(v => v)
}))
vi.mock('pinia', () => ({
  storeToRefs: () => ({
    embeddedCallBack: { value: 'no' },
    nowPanelTrackInfo: { value: {} },
    nowPanelJumpInfo: { value: {} },
    mobileInPc: { value: false },
    inMobile: { value: false }
  })
}))
vi.mock('@/utils/canvasUtils', () => ({
  isDashboard: vi.fn(() => true),
  trackBarStyleCheck: vi.fn()
}))
vi.mock('@/components/visualization/ViewTrackBar.vue', () => ({
  default: { template: '<div>track-bar</div>' }
}))

import DeIndicator from '../DeIndicator.vue'

const { getData: mockGetData } = vi.mocked(await import('@/api/chart'))

describe('DeIndicator', () => {
  it('should render without errors', () => {
    const wrapper = shallowMount(DeIndicator, {
      props: {
        element: { propValue: null },
        view: { propValue: null, yAxis: [], drillFields: [], senior: {} } as any,
        showPosition: 'canvas',
        scale: 1,
        terminal: 'pc',
        suffixId: 'common',
        fontFamily: 'inherit'
      },
      global: {
        stubs: { ViewTrackBar: true }
      }
    })
    expect(wrapper.find('.menu-point').exists() || wrapper.find('div').exists()).toBe(true)
  })

  it('should expose calcData and renderChart methods', () => {
    const wrapper = shallowMount(DeIndicator, {
      props: {
        element: { propValue: null },
        view: { propValue: null, yAxis: [], drillFields: [], senior: {} } as any
      },
      global: {
        stubs: { ViewTrackBar: true }
      }
    })
    expect(typeof (wrapper.vm as any).calcData).toBe('function')
    expect(typeof (wrapper.vm as any).renderChart).toBe('function')
  })

  it('reads indicator value from flat data array when series is absent', async () => {
    mockGetData.mockResolvedValue({
      data: [{ value: 1990.0 }],
      drillFilters: []
    } as any)

    const wrapper = shallowMount(DeIndicator, {
      props: {
        element: { propValue: null },
        view: {
          propValue: null,
          tableId: 123,
          yAxis: [{ name: 'revenue', chartShowName: '营业收入' }],
          drillFields: [],
          senior: { functionCfg: { emptyDataStrategy: 'breakLine' } }
        } as any,
        showPosition: 'canvas',
        scale: 1,
        terminal: 'pc',
        suffixId: 'common',
        fontFamily: 'inherit'
      },
      global: { stubs: { ViewTrackBar: true } }
    })

    const vm = wrapper.vm as any
    await vm.calcData(wrapper.props('view'))

    await vi.dynamicImportSettled()

    expect(vm.resultObject).toBeDefined()
    expect(vm.result).toBe(1990.0)
    expect(vm.resultName).toBe('营业收入')
  })

  it('reads indicator value from series when present', async () => {
    mockGetData.mockResolvedValue({
      data: { series: [{ data: [42] }] },
      drillFilters: []
    } as any)

    const wrapper = shallowMount(DeIndicator, {
      props: {
        element: { propValue: null },
        view: {
          propValue: null,
          tableId: 123,
          yAxis: [{ name: 'sales' }],
          drillFields: [],
          senior: {}
        } as any,
        showPosition: 'canvas',
        scale: 1,
        terminal: 'pc',
        suffixId: 'common',
        fontFamily: 'inherit'
      },
      global: { stubs: { ViewTrackBar: true } }
    })

    const vm = wrapper.vm as any
    await vm.calcData(wrapper.props('view'))

    await vi.dynamicImportSettled()

    expect(vm.resultObject).toBeDefined()
    expect(vm.result).toBe(42)
  })

  it('shows undefined when data is empty and no setZero strategy', async () => {
    mockGetData.mockResolvedValue({
      data: [],
      drillFilters: []
    } as any)

    const wrapper = shallowMount(DeIndicator, {
      props: {
        element: { propValue: null },
        view: {
          propValue: null,
          tableId: 123,
          yAxis: [{ name: 'empty' }],
          drillFields: [],
          senior: { functionCfg: { emptyDataStrategy: 'breakLine' } }
        } as any,
        showPosition: 'canvas',
        scale: 1,
        terminal: 'pc',
        suffixId: 'common',
        fontFamily: 'inherit'
      },
      global: { stubs: { ViewTrackBar: true } }
    })

    const vm = wrapper.vm as any
    await vm.calcData(wrapper.props('view'))

    await vi.dynamicImportSettled()

    expect(vm.result).toBe('-')
  })
})
