import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

import {
  PIE_EDITOR_PROPERTY,
  PIE_EDITOR_PROPERTY_INNER,
  PIE_AXIS_TYPE,
  PIE_AXIS_CONFIG
} from '../common'

describe('pie/common', () => {
  describe('PIE_EDITOR_PROPERTY', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(PIE_EDITOR_PROPERTY)).toBe(true)
      expect(PIE_EDITOR_PROPERTY.length).toBeGreaterThan(0)
    })

    it('contains basic-style-selector', () => {
      expect(PIE_EDITOR_PROPERTY).toContain('basic-style-selector')
    })

    it('contains required editor properties', () => {
      expect(PIE_EDITOR_PROPERTY).toContain('background-overall-component')
      expect(PIE_EDITOR_PROPERTY).toContain('border-style')
      expect(PIE_EDITOR_PROPERTY).toContain('title-selector')
      expect(PIE_EDITOR_PROPERTY).toContain('legend-selector')
      expect(PIE_EDITOR_PROPERTY).toContain('label-selector')
      expect(PIE_EDITOR_PROPERTY).toContain('tooltip-selector')
      expect(PIE_EDITOR_PROPERTY).toContain('jump-set')
      expect(PIE_EDITOR_PROPERTY).toContain('linkage')
    })

    it('does not contain axis selectors (pie has no axes)', () => {
      expect(PIE_EDITOR_PROPERTY).not.toContain('x-axis-selector')
      expect(PIE_EDITOR_PROPERTY).not.toContain('y-axis-selector')
    })
  })

  describe('PIE_EDITOR_PROPERTY_INNER', () => {
    it('is an object', () => {
      expect(typeof PIE_EDITOR_PROPERTY_INNER).toBe('object')
      expect(PIE_EDITOR_PROPERTY_INNER).not.toBeNull()
    })

    it('has basic-style-selector key mapping to an array', () => {
      expect(PIE_EDITOR_PROPERTY_INNER).toHaveProperty('basic-style-selector')
      expect(Array.isArray(PIE_EDITOR_PROPERTY_INNER['basic-style-selector'])).toBe(true)
    })

    it('basic-style-selector includes pie-specific properties', () => {
      expect(PIE_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('colors')
      expect(PIE_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('alpha')
      expect(PIE_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('radius')
      expect(PIE_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('seriesColor')
    })

    it('label-selector includes pie-specific properties', () => {
      expect(PIE_EDITOR_PROPERTY_INNER['label-selector']).toContain('rPosition')
      expect(PIE_EDITOR_PROPERTY_INNER['label-selector']).toContain('showDimension')
      expect(PIE_EDITOR_PROPERTY_INNER['label-selector']).toContain('showQuota')
      expect(PIE_EDITOR_PROPERTY_INNER['label-selector']).toContain('showProportion')
    })

    it('has expected top-level keys', () => {
      expect(PIE_EDITOR_PROPERTY_INNER).toHaveProperty('background-overall-component')
      expect(PIE_EDITOR_PROPERTY_INNER).toHaveProperty('border-style')
      expect(PIE_EDITOR_PROPERTY_INNER).toHaveProperty('label-selector')
      expect(PIE_EDITOR_PROPERTY_INNER).toHaveProperty('tooltip-selector')
      expect(PIE_EDITOR_PROPERTY_INNER).toHaveProperty('basic-style-selector')
      expect(PIE_EDITOR_PROPERTY_INNER).toHaveProperty('title-selector')
      expect(PIE_EDITOR_PROPERTY_INNER).toHaveProperty('legend-selector')
    })
  })

  describe('PIE_AXIS_TYPE', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(PIE_AXIS_TYPE)).toBe(true)
      expect(PIE_AXIS_TYPE.length).toBeGreaterThan(0)
    })

    it('contains expected axis types', () => {
      expect(PIE_AXIS_TYPE).toContain('xAxis')
      expect(PIE_AXIS_TYPE).toContain('yAxis')
      expect(PIE_AXIS_TYPE).toContain('drill')
      expect(PIE_AXIS_TYPE).toContain('filter')
      expect(PIE_AXIS_TYPE).toContain('extLabel')
      expect(PIE_AXIS_TYPE).toContain('extTooltip')
    })
  })

  describe('PIE_AXIS_CONFIG', () => {
    it('is an object', () => {
      expect(typeof PIE_AXIS_CONFIG).toBe('object')
      expect(PIE_AXIS_CONFIG).not.toBeNull()
    })

    it('has xAxis config with name and type', () => {
      expect(PIE_AXIS_CONFIG).toHaveProperty('xAxis')
      expect(PIE_AXIS_CONFIG.xAxis).toHaveProperty('name')
      expect(PIE_AXIS_CONFIG.xAxis).toHaveProperty('type', 'd')
    })

    it('has yAxis config with name, type, and limit', () => {
      expect(PIE_AXIS_CONFIG).toHaveProperty('yAxis')
      expect(PIE_AXIS_CONFIG.yAxis).toHaveProperty('name')
      expect(PIE_AXIS_CONFIG.yAxis).toHaveProperty('type', 'q')
      expect(PIE_AXIS_CONFIG.yAxis).toHaveProperty('limit', 1)
    })
  })
})
