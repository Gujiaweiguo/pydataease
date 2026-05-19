import { describe, expect, it, vi } from 'vitest'

vi.mock('@antv/g2', () => ({}))
vi.mock('@antv/g2plot', () => ({
  Options: class {},
  PickOptions: class {}
}))
vi.mock('@antv/g2plot/esm/core/plot', () => ({
  PickOptions: class {},
  Plot: class {}
}))
vi.mock('@antv/g2plot/esm', () => ({ Options: class {} }))
vi.mock('@antv/l7', () => {
  class Zoom {}
  class Control {}
  class Scene {}
  return { Zoom, Control, Scene }
})
vi.mock('@antv/l7-scene', () => ({ Scene: class {} }))
vi.mock('@antv/l7plot', () => ({}))
vi.mock('@antv/l7plot-component', () => ({}))
vi.mock('element-plus-secondary', () => ({
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  ElMessage: { success: () => {}, error: () => {}, warning: () => {} }
}))
vi.mock('lodash-es', () => ({
  cloneDeep: (v: any) => JSON.parse(JSON.stringify(v)),
  defaultsDeep: (...args: any[]) => args.reduce((acc: any, obj: any) => ({ ...acc, ...obj }), {}),
  find: (arr: any[], fn: any) => arr.find(fn)
}))
vi.mock('decimal.js', () => ({
  Decimal: class {
    constructor(v: any) {
      return v
    }
  }
}))
vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/views/chart/components/js/util', () => ({
  isParent: () => false,
  parseJson: (s: string) => JSON.parse(s)
}))
vi.mock('@/api/setting/sysParameter', () => ({
  queryMapKeyApi: () => Promise.resolve('')
}))
vi.mock('@/store/modules/map', () => ({
  useMapStoreWithOut: () => ({})
}))
vi.mock('@/store/modules/link', () => ({
  useLinkStoreWithOut: () => ({})
}))
vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({})
}))
vi.mock('@/api/map', () => ({
  getGeoJson: () => Promise.resolve({})
}))
vi.mock('@/api/chart', () => ({
  innerExportDataSetDetails: () => Promise.resolve({}),
  innerExportDetails: () => Promise.resolve({})
}))

vi.stubGlobal(
  'Worker',
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  class {
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    constructor() {}
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    postMessage() {}
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    terminate() {}
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    addEventListener() {}
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    removeEventListener() {}
  }
)

const RENDER_ANTV = 'antv'
const RENDER_ECHARTS = 'echarts'
const RENDER_CUSTOM = 'custom'

interface MockChartView {
  render: string
  library: string
  name: string
  properties: any[]
  propertyInner: Record<string, any>
  axis: any[]
  axisConfig: Record<string, any>
  selectorSpec: Record<string, any>
}

class MockChartView {
  render = RENDER_ANTV
  library = 'g2plot'
  name = 'mock-chart'
  properties: any[] = []
  propertyInner: Record<string, any> = {}
  axis: any[] = []
  axisConfig: Record<string, any> = {}
  selectorSpec: Record<string, any> = {}
}

class MockChartView2 {
  render = RENDER_ECHARTS
  library = 'echarts'
  name = 'mock-chart-2'
  properties: any[] = []
  propertyInner: Record<string, any> = {}
  axis: any[] = []
  axisConfig: Record<string, any> = {}
  selectorSpec: Record<string, any> = {}
}

import chartViewManager from '../index'

describe('chartViewManager', () => {
  it('is defined with registerChartView and getChartView methods', () => {
    expect(chartViewManager).toBeDefined()
    expect(typeof chartViewManager.registerChartView).toBe('function')
    expect(typeof chartViewManager.getChartView).toBe('function')
  })

  it('registerChartView stores a chart retrievable with getChartView', () => {
    const view = new MockChartView() as unknown as MockChartView
    chartViewManager.registerChartView(RENDER_ANTV, 'mock-chart', view as any)

    const retrieved = chartViewManager.getChartView(RENDER_ANTV, 'mock-chart')
    expect(retrieved).toBe(view)
    expect(retrieved.name).toBe('mock-chart')
  })

  it('getChartView returns undefined for unregistered charts', () => {
    const result = chartViewManager.getChartView('nonexistent', 'no-such-chart')
    expect(result).toBeUndefined()
  })

  it('allows multiple charts under the same render type', () => {
    const view1 = new MockChartView() as unknown as MockChartView
    const view2 = {
      ...new MockChartView2(),
      render: RENDER_ANTV,
      name: 'mock-chart-2-antv'
    } as unknown as MockChartView

    chartViewManager.registerChartView(RENDER_ANTV, 'mock-chart-alpha', view1 as any)
    chartViewManager.registerChartView(RENDER_ANTV, 'mock-chart-beta', view2 as any)

    const retrieved1 = chartViewManager.getChartView(RENDER_ANTV, 'mock-chart-alpha')
    const retrieved2 = chartViewManager.getChartView(RENDER_ANTV, 'mock-chart-beta')

    expect(retrieved1).toBe(view1)
    expect(retrieved2).toBe(view2)
    expect(retrieved1).not.toBe(retrieved2)
  })

  it('allows charts under different render types', () => {
    const antvView = new MockChartView() as unknown as MockChartView
    const echartsView = new MockChartView2() as unknown as MockChartView

    chartViewManager.registerChartView(RENDER_ANTV, 'multi-antv', antvView as any)
    chartViewManager.registerChartView(RENDER_ECHARTS, 'multi-echarts', echartsView as any)

    const retrievedAntv = chartViewManager.getChartView(RENDER_ANTV, 'multi-antv')
    const retrievedEcharts = chartViewManager.getChartView(RENDER_ECHARTS, 'multi-echarts')

    expect(retrievedAntv).toBe(antvView)
    expect(retrievedEcharts).toBe(echartsView)
    expect(retrievedAntv).not.toBe(retrievedEcharts)
  })

  it('overwrites a previously registered chart with same render+name', () => {
    const view1 = new MockChartView() as unknown as MockChartView
    const view2 = new MockChartView() as unknown as MockChartView

    chartViewManager.registerChartView(RENDER_CUSTOM, 'overwrite-test', view1 as any)
    chartViewManager.registerChartView(RENDER_CUSTOM, 'overwrite-test', view2 as any)

    const retrieved = chartViewManager.getChartView(RENDER_CUSTOM, 'overwrite-test')
    expect(retrieved).toBe(view2)
    expect(retrieved).not.toBe(view1)
  })
})
