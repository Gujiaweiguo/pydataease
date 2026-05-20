/* eslint-disable @typescript-eslint/no-empty-function */
import { describe, expect, it, vi } from 'vitest'

vi.mock('@antv/g2plot/esm/core/plot', () => ({
  PickOptions: class {},
  Plot: class {}
}))
vi.mock('@antv/g2plot', () => ({ Options: class {} }))
vi.mock('@antv/s2', () => ({
  S2Theme: {},
  Style: {},
  S2Options: {},
  Meta: {},
  SERIES_NUMBER_FIELD: '',
  setTooltipContainerStyle: vi.fn(),
  S2DataConfig: {},
  S2Event: {},
  SpreadSheet: class {},
  BaseTooltip: class {}
}))
vi.mock('@antv/l7-scene', () => ({ Scene: class {} }))
vi.mock('@antv/l7plot', () => ({}))
vi.mock('@antv/l7plot-component', () => ({}))
vi.mock('@antv/l7plot/dist/esm/plots/choropleth/types', () => ({}))
vi.mock('@antv/l7plot/dist/esm/types/plot', () => ({ PlotOptions: class {} }))
vi.mock('@antv/l7plot/dist/esm/core/plot', () => ({ Plot: class {} }))
vi.mock('lodash-es', () => ({
  cloneDeep: (v: any) => JSON.parse(JSON.stringify(v)),
  defaultsDeep: (...args: any[]) => args.reduce((acc: any, obj: any) => ({ ...acc, ...obj }), {}),
  find: (arr: any[], fn: any) => arr.find(fn)
}))
vi.mock('element-plus-secondary', () => ({
  ElMessage: { success: () => {}, error: () => {}, warning: () => {} }
}))
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/views/chart/components/js/util', () => ({
  isParent: () => false,
  parseJson: (s: string) => JSON.parse(s),
  hexColorToRGBA: (_hex: string, alpha: number) => `rgba(0,0,0,${alpha})`,
  hexToRgba: (_hex: string, alpha: number) => `rgba(0,0,0,${alpha})`,
  measureText: () => 100,
  getColor: vi.fn(),
  getGroupColor: vi.fn(),
  getSingleDimensionColor: vi.fn(),
  getStackColor: vi.fn(),
  handleEmptyDataStrategy: vi.fn(),
  setupSeriesColor: vi.fn()
}))
vi.mock('@/views/chart/components/js/panel/common/common_antv', () => ({
  getAnalyse: vi.fn(),
  getAnalyseHorizontal: vi.fn(),
  getLabel: vi.fn(),
  getLegend: vi.fn(),
  getMultiSeriesTooltip: vi.fn(),
  getSlider: vi.fn(),
  getTheme: vi.fn(),
  getTooltip: vi.fn(),
  getXAxis: vi.fn(),
  getYAxis: vi.fn(),
  getConditions: vi.fn(),
  handleConditionsStyle: vi.fn(),
  addConditionsStyleColorToData: vi.fn(),
  configEmptyDataStyle: vi.fn(),
  configL7Label: vi.fn(),
  configL7Tooltip: vi.fn(),
  configL7Zoom: vi.fn(),
  configL7Legend: vi.fn(),
  configL7Style: vi.fn(),
  configL7PlotZoom: vi.fn()
}))
vi.mock('@/views/chart/components/js/panel/common/common_table', () => ({
  getCustomTheme: vi.fn(),
  getStyle: vi.fn(),
  getCurrentField: vi.fn(),
  getConditions: vi.fn(),
  handleTableEmptyStrategy: vi.fn(),
  configHeaderInteraction: vi.fn(),
  configTooltip: vi.fn(),
  configMergeCells: vi.fn(),
  CustomDataCell: class {},
  SortTooltip: class {},
  copyContent: vi.fn(),
  exportGridPivot: vi.fn(),
  exportRowQuotaGridPivot: vi.fn(),
  exportTreePivot: vi.fn(),
  exportRowQuotaTreePivot: vi.fn(),
  exportPivotExcel: vi.fn(),
  getRowIndex: vi.fn(),
  mappingColorCustom: vi.fn(),
  mappingColor: vi.fn(),
  getPivotConditions: vi.fn(),
  mappingPivotColor: vi.fn()
}))
vi.mock('@/api/setting/sysParameter', () => ({ queryMapKeyApi: () => Promise.resolve('') }))
vi.mock('@/store/modules/map', () => ({ useMapStoreWithOut: () => ({}) }))

import { ChartLibraryType, ChartRenderType } from '@/views/chart/components/js/panel/types'
import { G2PlotChartView, G2PlotWrapper } from '../g2plot'
import { S2ChartView } from '../s2'
import { L7ChartView, L7Wrapper } from '../l7'
import { L7PlotChartView } from '../l7plot'

class TestG2PlotChart extends G2PlotChartView {
  properties = [] as EditorProperty[]
  propertyInner = {} as EditorPropertyInner
  axis = [] as AxisType[]
  axisConfig = {} as AxisConfig
  selectorSpec = {} as EditorSelectorSpec
  constructor(name: string, defaultData: any[]) {
    super(name, defaultData)
  }
  drawChart() {
    return null as any
  }
  protected setupOptions(_chart: Chart, options: any): any {
    return options
  }
}

class TestS2Chart extends S2ChartView<any> {
  properties = [] as EditorProperty[]
  propertyInner = {} as EditorPropertyInner
  axis = [] as AxisType[]
  axisConfig = {} as AxisConfig
  selectorSpec = {} as EditorSelectorSpec
  constructor(name: string, defaultData: any[]) {
    super(name, defaultData)
  }
  drawChart() {
    return null as any
  }
}

class TestL7Chart extends L7ChartView<any, any> {
  properties = [] as EditorProperty[]
  propertyInner = {} as EditorPropertyInner
  axis = [] as AxisType[]
  axisConfig = {} as AxisConfig
  selectorSpec = {} as EditorSelectorSpec
  constructor(name: string, defaultData: any[]) {
    super(name, defaultData)
  }
  drawChart() {
    return null as any
  }
  protected setupOptions(_chart: Chart, options: any): any {
    return options
  }
}

class TestL7PlotChart extends L7PlotChartView<any, any> {
  properties = [] as EditorProperty[]
  propertyInner = {} as EditorPropertyInner
  axis = [] as AxisType[]
  axisConfig = {} as AxisConfig
  selectorSpec = {} as EditorSelectorSpec
  constructor(name: string, defaultData?: any[]) {
    super(name, defaultData)
  }
  drawChart() {
    return null as any
  }
  protected setupOptions(_chart: Chart, options: any): any {
    return options
  }
}

describe('G2PlotChartView', () => {
  it('sets library type to g2plot', () => {
    const instance = new TestG2PlotChart('test-g2plot', [])
    expect(instance.library).toBe(ChartLibraryType.G2_PLOT)
    expect(instance.library).toBe('g2plot')
  })

  it('sets render type to ANT_V', () => {
    const instance = new TestG2PlotChart('test-g2plot', [])
    expect(instance.render).toBe(ChartRenderType.ANT_V)
  })

  it('sets name via constructor', () => {
    const instance = new TestG2PlotChart('my-g2plot-chart', [])
    expect(instance.name).toBe('my-g2plot-chart')
  })

  it('stores defaultData via constructor', () => {
    const data = [{ value: 1 }, { value: 2 }]
    const instance = new TestG2PlotChart('test', data)
    expect((instance as any).defaultData).toEqual(data)
  })

  it('drawChart is defined on prototype', () => {
    const instance = new TestG2PlotChart('test', [])
    expect(typeof instance.drawChart).toBe('function')
  })

  it('has configTheme method', () => {
    const instance = new TestG2PlotChart('test', [])
    expect(typeof (instance as any).configTheme).toBe('function')
  })

  it('has configLabel method', () => {
    const instance = new TestG2PlotChart('test', [])
    expect(typeof (instance as any).configLabel).toBe('function')
  })

  it('has configTooltip method', () => {
    const instance = new TestG2PlotChart('test', [])
    expect(typeof (instance as any).configTooltip).toBe('function')
  })

  it('has configLegend method', () => {
    const instance = new TestG2PlotChart('test', [])
    expect(typeof (instance as any).configLegend).toBe('function')
  })

  it('has configXAxis method', () => {
    const instance = new TestG2PlotChart('test', [])
    expect(typeof (instance as any).configXAxis).toBe('function')
  })

  it('has configYAxis method', () => {
    const instance = new TestG2PlotChart('test', [])
    expect(typeof (instance as any).configYAxis).toBe('function')
  })
})

describe('G2PlotWrapper', () => {
  it('has destroy and render methods', () => {
    const wrapper = new G2PlotWrapper(null as any)
    expect(typeof wrapper.destroy).toBe('function')
    expect(typeof wrapper.render).toBe('function')
  })

  it('destroy does not throw when chartInstance is null', () => {
    const wrapper = new G2PlotWrapper(null as any)
    expect(() => wrapper.destroy()).not.toThrow()
  })

  it('render does not throw when chartInstance is null', () => {
    const wrapper = new G2PlotWrapper(null as any)
    expect(() => wrapper.render()).not.toThrow()
  })

  it('destroy calls destroy on single chart instance', () => {
    const mockChart = { destroy: vi.fn() }
    const wrapper = new G2PlotWrapper(mockChart as any)
    wrapper.destroy()
    expect(mockChart.destroy).toHaveBeenCalled()
  })

  it('destroy calls destroy on each chart in array', () => {
    const mock1 = { destroy: vi.fn() }
    const mock2 = { destroy: vi.fn() }
    const wrapper = new G2PlotWrapper([mock1, mock2] as any)
    wrapper.destroy()
    expect(mock1.destroy).toHaveBeenCalled()
    expect(mock2.destroy).toHaveBeenCalled()
  })

  it('render calls render on single chart instance', () => {
    const mockChart = { render: vi.fn() }
    const wrapper = new G2PlotWrapper(mockChart as any)
    wrapper.render()
    expect(mockChart.render).toHaveBeenCalled()
  })

  it('render calls render on each chart in array', () => {
    const mock1 = { render: vi.fn() }
    const mock2 = { render: vi.fn() }
    const wrapper = new G2PlotWrapper([mock1, mock2] as any)
    wrapper.render()
    expect(mock1.render).toHaveBeenCalled()
    expect(mock2.render).toHaveBeenCalled()
  })
})

describe('S2ChartView', () => {
  it('sets library type to s2', () => {
    const instance = new TestS2Chart('test-s2', [])
    expect(instance.library).toBe(ChartLibraryType.S2)
    expect(instance.library).toBe('s2')
  })

  it('sets render type to ANT_V', () => {
    const instance = new TestS2Chart('test-s2', [])
    expect(instance.render).toBe(ChartRenderType.ANT_V)
  })

  it('sets name via constructor', () => {
    const instance = new TestS2Chart('my-s2-chart', [])
    expect(instance.name).toBe('my-s2-chart')
  })

  it('stores defaultData via constructor', () => {
    const data = [{ row: 'a', col: 'b' }]
    const instance = new TestS2Chart('test', data)
    expect((instance as any).defaultData).toEqual(data)
  })

  it('drawChart is defined on prototype', () => {
    const instance = new TestS2Chart('test', [])
    expect(typeof instance.drawChart).toBe('function')
  })

  it('has configTheme method', () => {
    const instance = new TestS2Chart('test', [])
    expect(typeof (instance as any).configTheme).toBe('function')
  })

  it('has configStyle method', () => {
    const instance = new TestS2Chart('test', [])
    expect(typeof (instance as any).configStyle).toBe('function')
  })

  it('has configEmptyDataStrategy method', () => {
    const instance = new TestS2Chart('test', [])
    expect(typeof (instance as any).configEmptyDataStrategy).toBe('function')
  })

  it('has configConditions method', () => {
    const instance = new TestS2Chart('test', [])
    expect(typeof (instance as any).configConditions).toBe('function')
  })
})

describe('L7ChartView', () => {
  it('sets library type to l7', () => {
    const instance = new TestL7Chart('test-l7', [])
    expect(instance.library).toBe(ChartLibraryType.L7)
    expect(instance.library).toBe('l7')
  })

  it('sets render type to ANT_V', () => {
    const instance = new TestL7Chart('test-l7', [])
    expect(instance.render).toBe(ChartRenderType.ANT_V)
  })

  it('sets name via constructor', () => {
    const instance = new TestL7Chart('my-l7-chart', [])
    expect(instance.name).toBe('my-l7-chart')
  })

  it('drawChart is defined on prototype', () => {
    const instance = new TestL7Chart('test', [])
    expect(typeof instance.drawChart).toBe('function')
  })

  it('has configLabel method', () => {
    const instance = new TestL7Chart('test', [])
    expect(typeof (instance as any).configLabel).toBe('function')
  })

  it('has configTooltip method', () => {
    const instance = new TestL7Chart('test', [])
    expect(typeof (instance as any).configTooltip).toBe('function')
  })

  it('has configZoomButton method', () => {
    const instance = new TestL7Chart('test', [])
    expect(typeof (instance as any).configZoomButton).toBe('function')
  })

  it('has configEmptyDataStrategy method', () => {
    const instance = new TestL7Chart('test', [])
    expect(typeof (instance as any).configEmptyDataStrategy).toBe('function')
  })

  it('has getMapKey method', () => {
    const instance = new TestL7Chart('test', [])
    expect(typeof (instance as any).getMapKey).toBe('function')
  })
})

describe('L7Wrapper', () => {
  it('has destroy and render methods', () => {
    const wrapper = new L7Wrapper(null as any, null)
    expect(typeof wrapper.destroy).toBe('function')
    expect(typeof wrapper.render).toBe('function')
  })

  it('destroy does not throw when chartInstance is null', () => {
    const wrapper = new L7Wrapper(null as any, null)
    expect(() => wrapper.destroy()).not.toThrow()
  })

  it('getScene returns scene', () => {
    const mockScene = { loaded: false } as any
    const wrapper = new L7Wrapper(mockScene, null)
    expect(wrapper.getScene()).toBe(mockScene)
  })

  it('destroy calls destroy on scene', () => {
    const mockScene = { destroy: vi.fn() } as any
    const wrapper = new L7Wrapper(mockScene, null)
    wrapper.destroy()
    expect(mockScene.destroy).toHaveBeenCalled()
  })
})

describe('L7PlotChartView', () => {
  it('sets library type to l7plot', () => {
    const instance = new TestL7PlotChart('test-l7plot', [])
    expect(instance.library).toBe(ChartLibraryType.L7_PLOT)
    expect(instance.library).toBe('l7plot')
  })

  it('sets render type to ANT_V', () => {
    const instance = new TestL7PlotChart('test-l7plot', [])
    expect(instance.render).toBe(ChartRenderType.ANT_V)
  })

  it('sets name via constructor', () => {
    const instance = new TestL7PlotChart('my-l7plot-chart', [])
    expect(instance.name).toBe('my-l7plot-chart')
  })

  it('stores defaultData via constructor', () => {
    const data = [{ region: 'us' }]
    const instance = new TestL7PlotChart('test', data)
    expect((instance as any).defaultData).toEqual(data)
  })

  it('drawChart is defined on prototype', () => {
    const instance = new TestL7PlotChart('test', [])
    expect(typeof instance.drawChart).toBe('function')
  })

  it('has configLabel method', () => {
    const instance = new TestL7PlotChart('test', [])
    expect(typeof (instance as any).configLabel).toBe('function')
  })

  it('has configTooltip method', () => {
    const instance = new TestL7PlotChart('test', [])
    expect(typeof (instance as any).configTooltip).toBe('function')
  })

  it('has configLegend method', () => {
    const instance = new TestL7PlotChart('test', [])
    expect(typeof (instance as any).configLegend).toBe('function')
  })

  it('has configStyle method', () => {
    const instance = new TestL7PlotChart('test', [])
    expect(typeof (instance as any).configStyle).toBe('function')
  })

  it('has configZoomButton method', () => {
    const instance = new TestL7PlotChart('test', [])
    expect(typeof (instance as any).configZoomButton).toBe('function')
  })

  it('has configEmptyDataStrategy method', () => {
    const instance = new TestL7PlotChart('test', [])
    expect(typeof (instance as any).configEmptyDataStrategy).toBe('function')
  })
})

describe('Impl class hierarchy', () => {
  it('G2PlotChartView is defined', () => {
    expect(G2PlotChartView).toBeDefined()
    expect(typeof G2PlotChartView).toBe('function')
  })

  it('S2ChartView is defined', () => {
    expect(S2ChartView).toBeDefined()
    expect(typeof S2ChartView).toBe('function')
  })

  it('L7ChartView is defined', () => {
    expect(L7ChartView).toBeDefined()
    expect(typeof L7ChartView).toBe('function')
  })

  it('L7PlotChartView is defined', () => {
    expect(L7PlotChartView).toBeDefined()
    expect(typeof L7PlotChartView).toBe('function')
  })

  it('each impl class has a distinct library type', () => {
    const g2plot = new TestG2PlotChart('g2', [])
    const s2 = new TestS2Chart('s2', [])
    const l7 = new TestL7Chart('l7', [])
    const l7plot = new TestL7PlotChart('l7plot', [])

    const libraries = [g2plot.library, s2.library, l7.library, l7plot.library]
    const unique = new Set(libraries)
    expect(unique.size).toBe(4)
  })
})
