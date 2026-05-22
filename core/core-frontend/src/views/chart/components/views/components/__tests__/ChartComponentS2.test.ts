import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/api/chart', () => ({
  getData: () => Promise.resolve({ data: { fields: [] } })
}))
vi.mock('@/views/chart/components/js/panel', () => ({
  default: {
    getChartView: () => ({
      drawChart: () => ({
        render: () => undefined,
        destroy: () => undefined,
        facet: { timer: { stop: () => undefined } },
        getCanvasElement: () => ({ remove: () => undefined })
      })
    })
  }
}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    nowPanelTrackInfo: {},
    nowPanelJumpInfo: {},
    mobileInPc: false,
    embeddedCallBack: 'no',
    inMobile: false,
    canvasStyleData: { component: { seniorStyleSetting: { pagerSize: 14, pagerColor: '#333' } } },
    setViewDataDetails: () => undefined,
    addViewTrackFilter: () => undefined,
    setViewInstanceInfo: () => undefined,
    setViewPageInfo: () => undefined
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
    canvasStyleData: {
      value: { component: { seniorStyleSetting: { pagerSize: 14, pagerColor: '#333' } } }
    },
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
  isISOMobile: () => false,
  getLocale: () => 'zh'
}))
vi.mock('@/utils/canvasUtils', () => ({
  isDashboard: () => true,
  trackBarStyleCheck: () => undefined
}))
vi.mock('lodash-es', () => ({
  defaultsDeep: (t: any, ...s: any[]) => Object.assign({}, ...s, t),
  cloneDeep: (v: any) => JSON.parse(JSON.stringify(v)),
  debounce: (fn: any) => fn
}))
vi.mock('element-plus-secondary', () => ({
  ElPagination: {
    template: '<div />',
    props: ['layout', 'pageSize', 'currentPage', 'pagerCount', 'total']
  }
}))
vi.mock('@antv/s2', () => ({
  SpreadSheet: {}
}))

import ChartComponentS2 from '../ChartComponentS2.vue'

const globalStubs = {
  ViewTrackBar: {
    template: '<div />',
    props: ['trackMenu', 'fontFamily', 'isDataVMobile', 'style'],
    methods: { trackButtonClick: () => undefined }
  },
  ChartError: { template: '<div />', props: ['errMsg'] },
  ElRow: { template: '<div><slot /></div>', props: ['style'] },
  ElDialog: { template: '<div><slot /></div>', props: ['modelValue'] },
  ElPagination: {
    template: '<div />',
    props: ['layout', 'pageSize', 'currentPage', 'pagerCount', 'total']
  }
}

const defaultView = () => ({
  id: 's2-view',
  type: 'table-info',
  render: 'antv',
  xAxis: [],
  yAxis: [],
  drillFields: [],
  customAttr: {
    basicStyle: { tablePageMode: 'page', tablePageStyle: 'simple', tablePageSize: 20 },
    tableCell: { mergeCells: false },
    tableHeader: {}
  },
  customStyle: {}
})

const mountProps = (view = defaultView()) =>
  ({
    element: { propValue: null, actionSelection: { linkageActive: 'auto' } },
    view: view as any
  } as any)

describe('ChartComponentS2', () => {
  it('renders with default props', () => {
    const wrapper = shallowMount(ChartComponentS2, {
      props: mountProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('computes trackMenu correctly for table-info type', () => {
    const wrapper = shallowMount(ChartComponentS2, {
      props: mountProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(Array.isArray(vm.trackMenu)).toBe(true)
  })

  it('exposes calcData, renderChart, renderChartFromDialog, trackMenu', () => {
    const wrapper = shallowMount(ChartComponentS2, {
      props: mountProps(),
      global: { stubs: globalStubs }
    })
    expect(typeof (wrapper.vm as any).calcData).toBe('function')
    expect(typeof (wrapper.vm as any).renderChart).toBe('function')
    expect(typeof (wrapper.vm as any).renderChartFromDialog).toBe('function')
  })

  it('showPage is false when chart type is not table-info or table-normal', () => {
    const view = defaultView()
    view.type = 'bar'
    const wrapper = shallowMount(ChartComponentS2, {
      props: mountProps(view),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.showPage).toBe(false)
  })
})
