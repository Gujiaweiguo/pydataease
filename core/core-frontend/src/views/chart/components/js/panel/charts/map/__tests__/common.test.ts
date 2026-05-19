import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

import {
  MAP_EDITOR_PROPERTY,
  MAP_EDITOR_PROPERTY_INNER,
  MAP_AXIS_TYPE,
  gaodeMapStyleOptions,
  tdtMapStyleOptions,
  qqMapStyleOptions
} from '../common'

describe('map/common', () => {
  describe('MAP_EDITOR_PROPERTY', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(MAP_EDITOR_PROPERTY)).toBe(true)
      expect(MAP_EDITOR_PROPERTY.length).toBeGreaterThan(0)
    })

    it('contains basic-style-selector', () => {
      expect(MAP_EDITOR_PROPERTY).toContain('basic-style-selector')
    })

    it('contains map-mapping', () => {
      expect(MAP_EDITOR_PROPERTY).toContain('map-mapping')
    })

    it('contains required editor properties', () => {
      expect(MAP_EDITOR_PROPERTY).toContain('background-overall-component')
      expect(MAP_EDITOR_PROPERTY).toContain('border-style')
      expect(MAP_EDITOR_PROPERTY).toContain('title-selector')
      expect(MAP_EDITOR_PROPERTY).toContain('label-selector')
      expect(MAP_EDITOR_PROPERTY).toContain('tooltip-selector')
      expect(MAP_EDITOR_PROPERTY).toContain('function-cfg')
      expect(MAP_EDITOR_PROPERTY).toContain('jump-set')
      expect(MAP_EDITOR_PROPERTY).toContain('linkage')
    })

    it('does not contain axis selectors', () => {
      expect(MAP_EDITOR_PROPERTY).not.toContain('x-axis-selector')
      expect(MAP_EDITOR_PROPERTY).not.toContain('y-axis-selector')
    })
  })

  describe('MAP_EDITOR_PROPERTY_INNER', () => {
    it('is an object', () => {
      expect(typeof MAP_EDITOR_PROPERTY_INNER).toBe('object')
      expect(MAP_EDITOR_PROPERTY_INNER).not.toBeNull()
    })

    it('has basic-style-selector with map-specific properties', () => {
      expect(MAP_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('colors')
      expect(MAP_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('alpha')
      expect(MAP_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('areaBorderColor')
      expect(MAP_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('zoom')
    })

    it('has label-selector with map-specific properties', () => {
      expect(MAP_EDITOR_PROPERTY_INNER['label-selector']).toContain('labelBgColor')
      expect(MAP_EDITOR_PROPERTY_INNER['label-selector']).toContain('labelShadow')
      expect(MAP_EDITOR_PROPERTY_INNER['label-selector']).toContain('showDimension')
      expect(MAP_EDITOR_PROPERTY_INNER['label-selector']).toContain('showQuota')
    })

    it('has map-mapping key', () => {
      expect(MAP_EDITOR_PROPERTY_INNER).toHaveProperty('map-mapping')
    })

    it('has expected top-level keys', () => {
      expect(MAP_EDITOR_PROPERTY_INNER).toHaveProperty('background-overall-component')
      expect(MAP_EDITOR_PROPERTY_INNER).toHaveProperty('border-style')
      expect(MAP_EDITOR_PROPERTY_INNER).toHaveProperty('basic-style-selector')
      expect(MAP_EDITOR_PROPERTY_INNER).toHaveProperty('title-selector')
      expect(MAP_EDITOR_PROPERTY_INNER).toHaveProperty('label-selector')
      expect(MAP_EDITOR_PROPERTY_INNER).toHaveProperty('tooltip-selector')
      expect(MAP_EDITOR_PROPERTY_INNER).toHaveProperty('function-cfg')
    })
  })

  describe('MAP_AXIS_TYPE', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(MAP_AXIS_TYPE)).toBe(true)
      expect(MAP_AXIS_TYPE.length).toBeGreaterThan(0)
    })

    it('contains expected axis types', () => {
      expect(MAP_AXIS_TYPE).toContain('xAxis')
      expect(MAP_AXIS_TYPE).toContain('yAxis')
      expect(MAP_AXIS_TYPE).toContain('area')
      expect(MAP_AXIS_TYPE).toContain('drill')
      expect(MAP_AXIS_TYPE).toContain('filter')
      expect(MAP_AXIS_TYPE).toContain('extLabel')
      expect(MAP_AXIS_TYPE).toContain('extTooltip')
    })
  })

  describe('gaodeMapStyleOptions', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(gaodeMapStyleOptions)).toBe(true)
      expect(gaodeMapStyleOptions.length).toBeGreaterThan(0)
    })

    it('each option has name and value', () => {
      for (const opt of gaodeMapStyleOptions) {
        expect(opt).toHaveProperty('name')
        expect(opt).toHaveProperty('value')
        expect(typeof opt.value).toBe('string')
      }
    })

    it('contains normal style', () => {
      expect(gaodeMapStyleOptions.find(o => o.value === 'normal')).toBeDefined()
    })

    it('contains custom style', () => {
      expect(gaodeMapStyleOptions.find(o => o.value === 'custom')).toBeDefined()
    })
  })

  describe('tdtMapStyleOptions', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(tdtMapStyleOptions)).toBe(true)
      expect(tdtMapStyleOptions.length).toBeGreaterThan(0)
    })

    it('each option has name and value', () => {
      for (const opt of tdtMapStyleOptions) {
        expect(opt).toHaveProperty('name')
        expect(opt).toHaveProperty('value')
      }
    })
  })

  describe('qqMapStyleOptions', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(qqMapStyleOptions)).toBe(true)
      expect(qqMapStyleOptions.length).toBeGreaterThan(0)
    })

    it('each option has name and value', () => {
      for (const opt of qqMapStyleOptions) {
        expect(opt).toHaveProperty('name')
        expect(opt).toHaveProperty('value')
      }
    })

    it('contains normal and custom styles', () => {
      expect(qqMapStyleOptions.find(o => o.value === 'normal')).toBeDefined()
      expect(qqMapStyleOptions.find(o => o.value === 'custom')).toBeDefined()
    })
  })
})
