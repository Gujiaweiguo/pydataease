/* eslint-disable @typescript-eslint/no-empty-function */
import { describe, expect, it, vi } from 'vitest'

vi.mock('@antv/g2plot/esm/core/plot', () => ({
  PickOptions: class {},
  Plot: class {}
}))
vi.mock('@antv/g2plot', () => ({ Options: class {} }))
vi.mock('@antv/g2plot/esm/plots/liquid', () => ({
  Liquid: class {
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    on() {}
    destroy() {}
    // eslint-disable-next-line @typescript-eslint/no-empty-function
    render() {}
  }
}))
// eslint-disable-next-line @typescript-eslint/no-empty-function
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
  flow:
    (...fns: any[]) =>
    (...args: any[]) =>
      fns.reduce(
        (result: any, fn: any) => fn(result[0], result[1] !== undefined ? result[1] : args[1]),
        args
      ),
  isParent: () => false,
  parseJson: (s: any) => (typeof s === 'string' ? JSON.parse(s) : s),
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
  copyContent: vi.fn()
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  DEFAULT_MISC: {
    liquidShape: 'circle',
    liquidSize: 80,
    liquidMax: undefined,
    liquidShowBorder: false,
    liquidBorderWidth: 3,
    liquidBorderDistance: 4
  }
}))
vi.mock('@/views/chart/components/js/formatter', () => ({
  valueFormatter: (v: number) => String(v)
}))
vi.mock('@/api/setting/sysParameter', () => ({ queryMapKeyApi: () => Promise.resolve('') }))
vi.mock('@/store/modules/map', () => ({ useMapStoreWithOut: () => ({}) }))

import { ChartLibraryType, ChartRenderType } from '@/views/chart/components/js/panel/types'
import { Liquid } from '../liquid'

describe('Liquid', () => {
  it('is exported as a class', () => {
    expect(Liquid).toBeDefined()
    expect(typeof Liquid).toBe('function')
  })

  it('sets name to "liquid"', () => {
    const instance = new Liquid()
    expect(instance.name).toBe('liquid')
  })

  it('sets library type to G2_PLOT (g2plot)', () => {
    const instance = new Liquid()
    expect(instance.library).toBe(ChartLibraryType.G2_PLOT)
    expect(instance.library).toBe('g2plot')
  })

  it('sets render type to ANT_V', () => {
    const instance = new Liquid()
    expect(instance.render).toBe(ChartRenderType.ANT_V)
  })

  describe('properties', () => {
    it('is a non-empty array', () => {
      const instance = new Liquid()
      expect(Array.isArray(instance.properties)).toBe(true)
      expect(instance.properties.length).toBeGreaterThan(0)
    })

    it('contains basic-style-selector', () => {
      const instance = new Liquid()
      expect(instance.properties).toContain('basic-style-selector')
    })

    it('contains label-selector', () => {
      const instance = new Liquid()
      expect(instance.properties).toContain('label-selector')
    })

    it('contains misc-selector', () => {
      const instance = new Liquid()
      expect(instance.properties).toContain('misc-selector')
    })

    it('contains title-selector', () => {
      const instance = new Liquid()
      expect(instance.properties).toContain('title-selector')
    })

    it('contains threshold', () => {
      const instance = new Liquid()
      expect(instance.properties).toContain('threshold')
    })

    it('contains background-overall-component', () => {
      const instance = new Liquid()
      expect(instance.properties).toContain('background-overall-component')
    })

    it('contains border-style', () => {
      const instance = new Liquid()
      expect(instance.properties).toContain('border-style')
    })
  })

  describe('propertyInner', () => {
    it('has basic-style-selector with colors and alpha', () => {
      const instance = new Liquid()
      expect(instance.propertyInner['basic-style-selector']).toContain('colors')
      expect(instance.propertyInner['basic-style-selector']).toContain('alpha')
    })

    it('has label-selector with expected properties', () => {
      const instance = new Liquid()
      expect(instance.propertyInner['label-selector']).toContain('fontSize')
      expect(instance.propertyInner['label-selector']).toContain('color')
      expect(instance.propertyInner['label-selector']).toContain('showQuota')
      expect(instance.propertyInner['label-selector']).toContain('showProportion')
    })

    it('has misc-selector with liquid-specific properties', () => {
      const instance = new Liquid()
      expect(instance.propertyInner['misc-selector']).toContain('liquidShape')
      expect(instance.propertyInner['misc-selector']).toContain('liquidSize')
      expect(instance.propertyInner['misc-selector']).toContain('liquidMaxType')
    })

    it('has title-selector with expected properties', () => {
      const instance = new Liquid()
      expect(instance.propertyInner['title-selector']).toContain('title')
      expect(instance.propertyInner['title-selector']).toContain('fontSize')
      expect(instance.propertyInner['title-selector']).toContain('color')
    })

    it('has threshold with liquidThreshold', () => {
      const instance = new Liquid()
      expect(instance.propertyInner['threshold']).toContain('liquidThreshold')
    })
  })

  describe('axis', () => {
    it('contains yAxis', () => {
      const instance = new Liquid()
      expect(instance.axis).toContain('yAxis')
    })

    it('contains filter', () => {
      const instance = new Liquid()
      expect(instance.axis).toContain('filter')
    })

    it('does not contain xAxis', () => {
      const instance = new Liquid()
      expect(instance.axis).not.toContain('xAxis')
    })
  })

  describe('axisConfig', () => {
    it('has yAxis config', () => {
      const instance = new Liquid()
      expect(instance.axisConfig).toHaveProperty('yAxis')
    })

    it('yAxis has type q', () => {
      const instance = new Liquid()
      expect(instance.axisConfig.yAxis.type).toBe('q')
    })

    it('yAxis has limit 1', () => {
      const instance = new Liquid()
      expect(instance.axisConfig.yAxis.limit).toBe(1)
    })
  })

  it('has drawChart method', () => {
    const instance = new Liquid()
    expect(typeof instance.drawChart).toBe('function')
  })

  it('has setupDefaultOptions method', () => {
    const instance = new Liquid()
    expect(typeof instance.setupDefaultOptions).toBe('function')
  })

  it('defaultData is an empty array', () => {
    const instance = new Liquid()
    expect((instance as any).defaultData).toEqual([])
  })
})
