import { describe, expect, it, vi } from 'vitest'

// Mock heavy dependencies before importing the module under test
vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))
vi.mock('@/utils/utils', () => ({
  isMobile: () => false
}))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {},
  PATH_URL: '/'
}))
vi.mock('@/config/axios/hmac', () => ({
  hmacSign: vi.fn()
}))
vi.mock('@/components/plugin/src/ImportXpackTool', () => ({
  PATH_URL: '/'
}))
vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({ baseUrl: '' })
}))
vi.mock('@/api/plugin', () => ({
  xpackModelApi: {}
}))
vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({ wsCache: { get: vi.fn(), set: vi.fn() } })
}))
vi.mock('../../util', () => ({
  hexColorToRGBA: vi.fn((_c: string, a: number) => `rgba(0,0,0,${a})`),
  hexToRgba: vi.fn(),
  measureText: vi.fn(() => 0),
  parseJson: vi.fn((s: any) => (typeof s === 'string' ? JSON.parse(s) : s))
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  DEFAULT_BASIC_STYLE: {},
  DEFAULT_LEGEND_STYLE: {},
  DEFAULT_XAXIS_STYLE: {},
  DEFAULT_YAXIS_STYLE: {},
  DEFAULT_YAXIS_EXT_STYLE: {}
}))
vi.mock('@/views/chart/components/js/formatter', () => ({
  valueFormatter: vi.fn()
}))
vi.mock('mathjs', () => ({
  add: (a: number, b: number) => a + b
}))
vi.mock('lodash-es/isEmpty', () => ({
  default: (v: any) =>
    v === undefined || v === null || v === '' || (Array.isArray(v) && v.length === 0)
}))
vi.mock('lodash', () => ({
  default: {
    isEmpty: (v: any) => v === undefined || v === null || v === ''
  }
}))
vi.mock('lodash-es', () => ({
  defaults: vi.fn(),
  find: vi.fn()
}))
vi.mock('@antv/g2plot/esm/types/common', () => ({}))
vi.mock('@antv/g2plot/esm', () => ({}))
vi.mock('@antv/g2plot', () => ({}))
vi.mock('@antv/l7plot', () => ({}))
vi.mock('@antv/l7plot/dist/lib/types/tooltip', () => ({}))
vi.mock('@antv/l7plot/dist/esm/plots/choropleth/types', () => ({}))
vi.mock('@antv/l7plot/dist/esm/types/legend', () => ({}))
vi.mock('@antv/l7plot-component/dist/lib/types/legend', () => ({}))
vi.mock('@antv/l7plot-component/dist/esm/legend/category/constants', () => ({
  CONTAINER_TPL: '',
  ITEM_TPL: '',
  LIST_CLASS: ''
}))
vi.mock('@antv/dom-util/esm/create-dom', () => ({
  default: vi.fn()
}))
vi.mock('@antv/util/esm/substitute', () => ({
  default: vi.fn()
}))
vi.mock('@antv/l7', () => ({ Zoom: vi.fn() }))
vi.mock('@antv/l7-utils', () => ({ DOM: {} }))
vi.mock('@antv/l7-scene', () => ({ Scene: vi.fn() }))
vi.mock('@antv/l7-component', () => ({}))
vi.mock('@antv/l7-core', () => ({ PositionType: {} }))
vi.mock('@turf/centroid', () => ({ centroid: vi.fn() }))
vi.mock('@antv/l7-maps', () => ({
  GaodeMap: vi.fn(),
  TMap: vi.fn(),
  TencentMap: vi.fn()
}))
vi.mock('@/views/chart/components/js/panel/charts/map/common', () => ({
  gaodeMapStyleOptions: [],
  qqMapStyleOptions: [],
  tdtMapStyleOptions: []
}))
vi.mock('@/views/chart/components/js/g2plot_tooltip_carousel', () => ({
  default: vi.fn(),
  isPie: vi.fn(),
  isColumn: vi.fn(),
  isMix: vi.fn(),
  isSupport: vi.fn()
}))

import {
  getLineDash,
  getTooltipSeriesTotalMap,
  setGradientColor,
  transAxisPosition
} from '../common_antv'

describe('common_antv pure functions', () => {
  describe('getLineDash', () => {
    it('returns [0, 0] for solid', () => {
      expect(getLineDash('solid')).toEqual([0, 0])
    })

    it('returns [10, 8] for dashed', () => {
      expect(getLineDash('dashed')).toEqual([10, 8])
    })

    it('returns [2, 2] for dotted', () => {
      expect(getLineDash('dotted')).toEqual([2, 2])
    })

    it('returns [0, 0] for unknown type', () => {
      expect(getLineDash('other')).toEqual([0, 0])
    })

    it('returns [0, 0] for undefined', () => {
      expect(getLineDash(undefined)).toEqual([0, 0])
    })
  })

  describe('setGradientColor', () => {
    const rawColor = 'rgba(255,0,0,1)'

    it('returns rawColor when show is false', () => {
      expect(setGradientColor(rawColor, false)).toBe(rawColor)
    })

    it('returns gradient string when show is true (default start=0)', () => {
      const result = setGradientColor(rawColor, true)
      expect(result).toContain('l(0)')
      expect(result).toContain(rawColor)
      expect(result).not.toBe(rawColor)
    })

    it('includes start position when start > 0', () => {
      const result = setGradientColor(rawColor, true, 0, 0.5)
      expect(result).toContain('0.5:')
      expect(result).toContain('rgba(255,255,255,0)')
    })

    it('uses 0.1 offset when start < 0', () => {
      const result = setGradientColor(rawColor, true, 0, -1)
      expect(result).toContain('0.1:')
      expect(result).toContain('rgba(255,255,255,0)')
    })

    it('respects custom angle', () => {
      const result = setGradientColor(rawColor, true, 90)
      expect(result).toContain('l(90)')
    })
  })

  describe('transAxisPosition', () => {
    it('maps top → left', () => {
      expect(transAxisPosition('top')).toBe('left')
    })

    it('maps bottom → right', () => {
      expect(transAxisPosition('bottom')).toBe('right')
    })

    it('maps left → bottom', () => {
      expect(transAxisPosition('left')).toBe('bottom')
    })

    it('maps right → top', () => {
      expect(transAxisPosition('right')).toBe('top')
    })

    it('returns input unchanged for unknown position', () => {
      expect(transAxisPosition('center')).toBe('center')
    })
  })

  describe('getTooltipSeriesTotalMap', () => {
    it('returns empty object for empty array', () => {
      expect(getTooltipSeriesTotalMap([])).toEqual({})
    })

    it('returns empty object for undefined input', () => {
      expect(getTooltipSeriesTotalMap(undefined as any)).toEqual({})
    })

    it('sums values by fieldId', () => {
      const data = [
        {
          dynamicTooltipValue: [
            { fieldId: 'f1', value: 10 },
            { fieldId: 'f2', value: 5 }
          ]
        },
        {
          dynamicTooltipValue: [{ fieldId: 'f1', value: 20 }]
        }
      ]
      const result = getTooltipSeriesTotalMap(data)
      expect(result).toEqual({ f1: 30, f2: 5 })
    })

    it('handles items without dynamicTooltipValue', () => {
      const data = [{}, { dynamicTooltipValue: [{ fieldId: 'f1', value: 3 }] }]
      const result = getTooltipSeriesTotalMap(data)
      expect(result).toEqual({ f1: 3 })
    })

    it('skips entries where value is falsy', () => {
      const data = [
        {
          dynamicTooltipValue: [
            { fieldId: 'f1', value: 0 },
            { fieldId: 'f2', value: null }
          ]
        }
      ]
      const result = getTooltipSeriesTotalMap(data)
      // f1 gets initialized to 0 but add(0, 0) = 0; f2 gets initialized to 0 but value is falsy
      expect(result).toEqual({ f1: 0, f2: 0 })
    })
  })
})
