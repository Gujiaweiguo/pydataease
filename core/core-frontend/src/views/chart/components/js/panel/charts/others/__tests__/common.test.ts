import { describe, expect, it, vi } from 'vitest'

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  DEFAULT_BASIC_STYLE: {
    colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
    alpha: 100,
    gradient: false,
    lineWidth: 2,
    lineSymbol: 'circle',
    lineSymbolSize: 4,
    lineSmooth: false,
    radiusColumnBar: 'round',
    columnWidthRatio: 60
  }
}))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

import {
  CHART_MIX_EDITOR_PROPERTY,
  CHART_MIX_EDITOR_PROPERTY_INNER,
  CHART_MIX_AXIS_TYPE,
  CHART_MIX_DEFAULT_BASIC_STYLE
} from '../chart-mix-common'
import {
  SANKEY_EDITOR_PROPERTY,
  SANKEY_EDITOR_PROPERTY_INNER,
  SANKEY_AXIS_TYPE
} from '../sankey-common'

describe('others/chart-mix-common', () => {
  describe('CHART_MIX_EDITOR_PROPERTY', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(CHART_MIX_EDITOR_PROPERTY)).toBe(true)
      expect(CHART_MIX_EDITOR_PROPERTY.length).toBeGreaterThan(0)
    })

    it('contains dual-basic-style-selector instead of basic-style-selector', () => {
      expect(CHART_MIX_EDITOR_PROPERTY).toContain('dual-basic-style-selector')
      expect(CHART_MIX_EDITOR_PROPERTY).not.toContain('basic-style-selector')
    })

    it('contains dual-y-axis-selector', () => {
      expect(CHART_MIX_EDITOR_PROPERTY).toContain('dual-y-axis-selector')
    })

    it('contains required editor properties', () => {
      expect(CHART_MIX_EDITOR_PROPERTY).toContain('background-overall-component')
      expect(CHART_MIX_EDITOR_PROPERTY).toContain('border-style')
      expect(CHART_MIX_EDITOR_PROPERTY).toContain('x-axis-selector')
      expect(CHART_MIX_EDITOR_PROPERTY).toContain('title-selector')
      expect(CHART_MIX_EDITOR_PROPERTY).toContain('legend-selector')
      expect(CHART_MIX_EDITOR_PROPERTY).toContain('label-selector')
      expect(CHART_MIX_EDITOR_PROPERTY).toContain('tooltip-selector')
      expect(CHART_MIX_EDITOR_PROPERTY).toContain('assist-line')
      expect(CHART_MIX_EDITOR_PROPERTY).toContain('function-cfg')
      expect(CHART_MIX_EDITOR_PROPERTY).toContain('jump-set')
      expect(CHART_MIX_EDITOR_PROPERTY).toContain('linkage')
    })
  })

  describe('CHART_MIX_EDITOR_PROPERTY_INNER', () => {
    it('is an object', () => {
      expect(typeof CHART_MIX_EDITOR_PROPERTY_INNER).toBe('object')
      expect(CHART_MIX_EDITOR_PROPERTY_INNER).not.toBeNull()
    })

    it('has dual-basic-style-selector key', () => {
      expect(CHART_MIX_EDITOR_PROPERTY_INNER).toHaveProperty('dual-basic-style-selector')
      expect(Array.isArray(CHART_MIX_EDITOR_PROPERTY_INNER['dual-basic-style-selector'])).toBe(true)
    })

    it('dual-basic-style-selector includes mix-specific properties', () => {
      expect(CHART_MIX_EDITOR_PROPERTY_INNER['dual-basic-style-selector']).toContain('colors')
      expect(CHART_MIX_EDITOR_PROPERTY_INNER['dual-basic-style-selector']).toContain('alpha')
      expect(CHART_MIX_EDITOR_PROPERTY_INNER['dual-basic-style-selector']).toContain('gradient')
      expect(CHART_MIX_EDITOR_PROPERTY_INNER['dual-basic-style-selector']).toContain(
        'subSeriesColor'
      )
      expect(CHART_MIX_EDITOR_PROPERTY_INNER['dual-basic-style-selector']).toContain('seriesColor')
    })

    it('has dual-y-axis-selector key', () => {
      expect(CHART_MIX_EDITOR_PROPERTY_INNER).toHaveProperty('dual-y-axis-selector')
      expect(Array.isArray(CHART_MIX_EDITOR_PROPERTY_INNER['dual-y-axis-selector'])).toBe(true)
    })

    it('has expected top-level keys', () => {
      expect(CHART_MIX_EDITOR_PROPERTY_INNER).toHaveProperty('background-overall-component')
      expect(CHART_MIX_EDITOR_PROPERTY_INNER).toHaveProperty('border-style')
      expect(CHART_MIX_EDITOR_PROPERTY_INNER).toHaveProperty('label-selector')
      expect(CHART_MIX_EDITOR_PROPERTY_INNER).toHaveProperty('tooltip-selector')
      expect(CHART_MIX_EDITOR_PROPERTY_INNER).toHaveProperty('x-axis-selector')
      expect(CHART_MIX_EDITOR_PROPERTY_INNER).toHaveProperty('title-selector')
      expect(CHART_MIX_EDITOR_PROPERTY_INNER).toHaveProperty('legend-selector')
      expect(CHART_MIX_EDITOR_PROPERTY_INNER).toHaveProperty('function-cfg')
    })
  })

  describe('CHART_MIX_AXIS_TYPE', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(CHART_MIX_AXIS_TYPE)).toBe(true)
      expect(CHART_MIX_AXIS_TYPE.length).toBeGreaterThan(0)
    })

    it('contains expected axis types', () => {
      expect(CHART_MIX_AXIS_TYPE).toContain('xAxis')
      expect(CHART_MIX_AXIS_TYPE).toContain('yAxis')
      expect(CHART_MIX_AXIS_TYPE).toContain('drill')
      expect(CHART_MIX_AXIS_TYPE).toContain('filter')
      expect(CHART_MIX_AXIS_TYPE).toContain('extLabel')
      expect(CHART_MIX_AXIS_TYPE).toContain('extTooltip')
    })
  })

  describe('CHART_MIX_DEFAULT_BASIC_STYLE', () => {
    it('is an object', () => {
      expect(typeof CHART_MIX_DEFAULT_BASIC_STYLE).toBe('object')
      expect(CHART_MIX_DEFAULT_BASIC_STYLE).not.toBeNull()
    })

    it('has subAlpha property', () => {
      expect(CHART_MIX_DEFAULT_BASIC_STYLE).toHaveProperty('subAlpha', 100)
    })

    it('has subColorScheme property', () => {
      expect(CHART_MIX_DEFAULT_BASIC_STYLE).toHaveProperty('subColorScheme', 'fast')
    })

    it('has subColors as an array of color strings', () => {
      expect(Array.isArray(CHART_MIX_DEFAULT_BASIC_STYLE.subColors)).toBe(true)
      expect(CHART_MIX_DEFAULT_BASIC_STYLE.subColors.length).toBeGreaterThan(0)
    })

    it('has line-specific left properties', () => {
      expect(CHART_MIX_DEFAULT_BASIC_STYLE).toHaveProperty('leftLineWidth')
      expect(CHART_MIX_DEFAULT_BASIC_STYLE).toHaveProperty('leftLineSymbol')
      expect(CHART_MIX_DEFAULT_BASIC_STYLE).toHaveProperty('leftLineSymbolSize')
      expect(CHART_MIX_DEFAULT_BASIC_STYLE).toHaveProperty('leftLineSmooth')
    })
  })
})

describe('others/sankey-common', () => {
  describe('SANKEY_EDITOR_PROPERTY', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(SANKEY_EDITOR_PROPERTY)).toBe(true)
      expect(SANKEY_EDITOR_PROPERTY.length).toBeGreaterThan(0)
    })

    it('contains basic-style-selector', () => {
      expect(SANKEY_EDITOR_PROPERTY).toContain('basic-style-selector')
    })

    it('contains required editor properties', () => {
      expect(SANKEY_EDITOR_PROPERTY).toContain('background-overall-component')
      expect(SANKEY_EDITOR_PROPERTY).toContain('border-style')
      expect(SANKEY_EDITOR_PROPERTY).toContain('label-selector')
      expect(SANKEY_EDITOR_PROPERTY).toContain('tooltip-selector')
      expect(SANKEY_EDITOR_PROPERTY).toContain('title-selector')
      expect(SANKEY_EDITOR_PROPERTY).toContain('jump-set')
      expect(SANKEY_EDITOR_PROPERTY).toContain('linkage')
    })

    it('does not contain axis selectors', () => {
      expect(SANKEY_EDITOR_PROPERTY).not.toContain('x-axis-selector')
      expect(SANKEY_EDITOR_PROPERTY).not.toContain('y-axis-selector')
    })
  })

  describe('SANKEY_EDITOR_PROPERTY_INNER', () => {
    it('is an object', () => {
      expect(typeof SANKEY_EDITOR_PROPERTY_INNER).toBe('object')
      expect(SANKEY_EDITOR_PROPERTY_INNER).not.toBeNull()
    })

    it('has basic-style-selector with colors, alpha, gradient', () => {
      expect(SANKEY_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('colors')
      expect(SANKEY_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('alpha')
      expect(SANKEY_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('gradient')
    })

    it('has expected top-level keys', () => {
      expect(SANKEY_EDITOR_PROPERTY_INNER).toHaveProperty('background-overall-component')
      expect(SANKEY_EDITOR_PROPERTY_INNER).toHaveProperty('border-style')
      expect(SANKEY_EDITOR_PROPERTY_INNER).toHaveProperty('basic-style-selector')
      expect(SANKEY_EDITOR_PROPERTY_INNER).toHaveProperty('label-selector')
      expect(SANKEY_EDITOR_PROPERTY_INNER).toHaveProperty('tooltip-selector')
      expect(SANKEY_EDITOR_PROPERTY_INNER).toHaveProperty('title-selector')
      expect(SANKEY_EDITOR_PROPERTY_INNER).toHaveProperty('function-cfg')
    })
  })

  describe('SANKEY_AXIS_TYPE', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(SANKEY_AXIS_TYPE)).toBe(true)
      expect(SANKEY_AXIS_TYPE.length).toBeGreaterThan(0)
    })

    it('contains xAxis and xAxisExt', () => {
      expect(SANKEY_AXIS_TYPE).toContain('xAxis')
      expect(SANKEY_AXIS_TYPE).toContain('xAxisExt')
      expect(SANKEY_AXIS_TYPE).toContain('yAxis')
    })

    it('contains filter and ext types', () => {
      expect(SANKEY_AXIS_TYPE).toContain('filter')
      expect(SANKEY_AXIS_TYPE).toContain('extLabel')
      expect(SANKEY_AXIS_TYPE).toContain('extTooltip')
    })
  })
})
