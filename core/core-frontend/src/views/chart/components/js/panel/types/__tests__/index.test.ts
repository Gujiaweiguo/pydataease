import { describe, expect, it, vi } from 'vitest'

import { ChartRenderType, ChartLibraryType, AbstractChartView } from '../index'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

describe('ChartRenderType', () => {
  it('has ANT_V = "antv"', () => {
    expect(ChartRenderType.ANT_V).toBe('antv')
  })

  it('has ECHARTS = "echarts"', () => {
    expect(ChartRenderType.ECHARTS).toBe('echarts')
  })

  it('has CUSTOM = "custom"', () => {
    expect(ChartRenderType.CUSTOM).toBe('custom')
  })

  it('has exactly 3 members', () => {
    expect(Object.keys(ChartRenderType)).toHaveLength(3)
  })
})

describe('ChartLibraryType', () => {
  it('has G2_PLOT = "g2plot"', () => {
    expect(ChartLibraryType.G2_PLOT).toBe('g2plot')
  })

  it('has L7_PLOT = "l7plot"', () => {
    expect(ChartLibraryType.L7_PLOT).toBe('l7plot')
  })

  it('has L7 = "l7"', () => {
    expect(ChartLibraryType.L7).toBe('l7')
  })

  it('has ECHARTS = "echarts"', () => {
    expect(ChartLibraryType.ECHARTS).toBe('echarts')
  })

  it('has S2 = "s2"', () => {
    expect(ChartLibraryType.S2).toBe('s2')
  })

  it('has RICH_TEXT = "rich-text"', () => {
    expect(ChartLibraryType.RICH_TEXT).toBe('rich-text')
  })

  it('has PICTURE_GROUP = "picture-group"', () => {
    expect(ChartLibraryType.PICTURE_GROUP).toBe('picture-group')
  })

  it('has INDICATOR = "indicator"', () => {
    expect(ChartLibraryType.INDICATOR).toBe('indicator')
  })

  it('has exactly 8 members', () => {
    expect(Object.keys(ChartLibraryType)).toHaveLength(8)
  })
})

describe('AbstractChartView', () => {
  it('cannot be instantiated directly', () => {
    expect(AbstractChartView).toBeDefined()
    expect(typeof AbstractChartView).toBe('function')
  })

  it('can be extended by a concrete subclass', () => {
    class ConcreteChartView extends AbstractChartView {
      properties = [] as any[]
      propertyInner = {} as any
      axis = [] as any[]
      axisConfig = {} as any
      selectorSpec = {} as any

      constructor() {
        super(ChartRenderType.ECHARTS, ChartLibraryType.ECHARTS, 'test-chart')
      }
    }

    const instance = new ConcreteChartView()
    expect(instance.render).toBe(ChartRenderType.ECHARTS)
    expect(instance.library).toBe(ChartLibraryType.ECHARTS)
    expect(instance.name).toBe('test-chart')
    expect(instance.properties).toEqual([])
    expect(instance.propertyInner).toEqual({})
    expect(instance.axis).toEqual([])
    expect(instance.axisConfig).toEqual({})
    expect(instance.selectorSpec).toEqual({})
  })

  it('sets defaultData when provided', () => {
    class ConcreteWithData extends AbstractChartView {
      properties = [] as any[]
      propertyInner = {} as any
      axis = [] as any[]
      axisConfig = {} as any
      selectorSpec = {} as any

      constructor() {
        super(ChartRenderType.ANT_V, ChartLibraryType.G2_PLOT, 'data-chart', [1, 2, 3])
      }
    }

    const instance = new ConcreteWithData()
    expect((instance as any).defaultData).toEqual([1, 2, 3])
  })

  it('defaultData is undefined when not provided', () => {
    class ConcreteNoData extends AbstractChartView {
      properties = [] as any[]
      propertyInner = {} as any
      axis = [] as any[]
      axisConfig = {} as any
      selectorSpec = {} as any

      constructor() {
        super(ChartRenderType.CUSTOM, ChartLibraryType.INDICATOR, 'no-data-chart')
      }
    }

    const instance = new ConcreteNoData()
    expect((instance as any).defaultData).toBeUndefined()
  })

  it('setupDefaultOptions returns the chart object unchanged', () => {
    class ConcreteSetup extends AbstractChartView {
      properties = [] as any[]
      propertyInner = {} as any
      axis = [] as any[]
      axisConfig = {} as any
      selectorSpec = {} as any

      constructor() {
        super(ChartRenderType.ECHARTS, ChartLibraryType.ECHARTS, 'setup-chart')
      }
    }

    const instance = new ConcreteSetup()
    const chartObj = { id: 1, title: 'test' }
    expect(instance.setupDefaultOptions(chartObj as any)).toBe(chartObj)
  })
})
