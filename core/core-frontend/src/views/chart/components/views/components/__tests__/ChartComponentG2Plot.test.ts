import { shallowMount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/api/chart', () => ({
  getData: () => Promise.resolve({ data: { fields: [] } })
}))
vi.mock('@/views/chart/components/js/panel', () => ({
  default: {
    getChartView: () => ({
      library: 'g2plot',
      drawChart: () => ({ render: () => undefined, destroy: () => undefined })
    })
  }
}))
vi.mock('@/views/chart/components/js/panel/types', () => ({
  ChartLibraryType: { G2_PLOT: 'g2plot', L7_PLOT: 'l7plot', L7: 'l7' }
}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    nowPanelTrackInfo: {},
    nowPanelJumpInfo: {},
    mobileInPc: false,
    embeddedCallBack: 'no',
    inMobile: false,
    setViewDataDetails: () => undefined,
    setViewOriginData: () => undefined,
    addViewTrackFilter: () => undefined
  })
}))
vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: () => undefined, on: () => undefined } })
}))
vi.mock('pinia', () => ({
  storeToRefs: () => ({
    nowPanelTrackInfo: { value: {} },
    nowPanelJumpInfo: { value: {} },
    mobileInPc: { value: false },
    embeddedCallBack: { value: 'no' },
    inMobile: { value: false }
  }),
  createPinia: () => ({}),
  defineStore: () => () => ({})
}))
vi.mock('@/utils/canvasStyle', () => ({
  customAttrTrans: {},
  customStyleTrans: {},
  recursionTransObj: () => undefined
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  BASE_VIEW_CONFIG: {}
}))
vi.mock('@/utils/utils', () => ({
  deepCopy: (v: any) => JSON.parse(JSON.stringify(v)),
  isMobile: () => false,
  getLocale: () => 'zh'
}))
vi.mock('@/utils/canvasUtils', () => ({
  isDashboard: () => true,
  trackBarStyleCheck: () => undefined
}))
vi.mock('lodash-es', () => ({
  defaultsDeep: (t: any, ...s: any[]) => Object.assign({}, ...s, t),
  cloneDeep: (v: any) => JSON.parse(JSON.stringify(v)),
  concat: (...args: any[]) => args.flat()
}))
vi.mock('@/views/chart/components/js/panel/common/common_antv', () => ({
  configEmptyDataStyle: () => undefined
}))
vi.mock('@antv/l7', () => ({
  ExportImage: class {
    hide() { return undefined }
  }
}))

import ChartComponentG2Plot from '../ChartComponentG2Plot.vue'

const globalStubs = {
  ViewTrackBar: { template: '<div />', props: ['trackMenu', 'fontFamily', 'isDataVMobile', 'style'], methods: { trackButtonClick: () => undefined } },
  ChartError: { template: '<div />', props: ['errMsg'] }
}

describe('ChartComponentG2Plot', () => {
  let origGetElementById: typeof document.getElementById

  beforeEach(() => {
    origGetElementById = document.getElementById.bind(document)
    document.getElementById = vi.fn().mockReturnValue({
      offsetWidth: 400,
      offsetHeight: 300,
      querySelectorAll: () => [],
      style: {},
      setAttribute: () => undefined
    })
  })

  afterEach(() => {
    document.getElementById = origGetElementById
  })

  it('renders with default props', () => {
    const wrapper = shallowMount(ChartComponentG2Plot, {
      props: {
        element: { propValue: null, actionSelection: { linkageActive: 'auto' } },
        view: { id: 'test-view', type: 'bar', render: 'antv', xAxis: [], yAxis: [], xAxisExt: [], extStack: [], drillFields: [], customAttr: '{}', customStyle: '{}' }
      },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('computes trackMenu as empty for multiplexing position', () => {
    const wrapper = shallowMount(ChartComponentG2Plot, {
      props: {
        element: { propValue: null, actionSelection: { linkageActive: 'auto' } },
        view: { id: 'test-view', type: 'bar', render: 'antv', xAxis: [], yAxis: [], xAxisExt: [], extStack: [], drillFields: [], customAttr: '{}', customStyle: '{}' },
        showPosition: 'multiplexing'
      },
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.trackMenu).toEqual([])
  })

  it('exposes calcData, renderChart, trackMenu, clearLinkage', () => {
    const wrapper = shallowMount(ChartComponentG2Plot, {
      props: {
        element: { propValue: null, actionSelection: { linkageActive: 'auto' } },
        view: { id: 'test-view', type: 'bar', render: 'antv', xAxis: [], yAxis: [], xAxisExt: [], extStack: [], drillFields: [], customAttr: '{}', customStyle: '{}' }
      },
      global: { stubs: globalStubs }
    })
    expect(typeof (wrapper.vm as any).calcData).toBe('function')
    expect(typeof (wrapper.vm as any).renderChart).toBe('function')
    expect(typeof (wrapper.vm as any).clearLinkage).toBe('function')
  })
})
