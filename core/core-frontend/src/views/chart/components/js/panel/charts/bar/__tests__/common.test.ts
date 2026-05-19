import { describe, expect, it } from 'vitest'
import {
  BAR_EDITOR_PROPERTY,
  BAR_RANGE_EDITOR_PROPERTY,
  BAR_EDITOR_PROPERTY_INNER,
  BAR_AXIS_TYPE
} from '../common'

describe('bar/common', () => {
  describe('BAR_EDITOR_PROPERTY', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(BAR_EDITOR_PROPERTY)).toBe(true)
      expect(BAR_EDITOR_PROPERTY.length).toBeGreaterThan(0)
    })

    it('contains basic-style-selector', () => {
      expect(BAR_EDITOR_PROPERTY).toContain('basic-style-selector')
    })

    it('contains required editor properties', () => {
      expect(BAR_EDITOR_PROPERTY).toContain('background-overall-component')
      expect(BAR_EDITOR_PROPERTY).toContain('border-style')
      expect(BAR_EDITOR_PROPERTY).toContain('label-selector')
      expect(BAR_EDITOR_PROPERTY).toContain('tooltip-selector')
      expect(BAR_EDITOR_PROPERTY).toContain('x-axis-selector')
      expect(BAR_EDITOR_PROPERTY).toContain('y-axis-selector')
      expect(BAR_EDITOR_PROPERTY).toContain('title-selector')
      expect(BAR_EDITOR_PROPERTY).toContain('legend-selector')
      expect(BAR_EDITOR_PROPERTY).toContain('function-cfg')
      expect(BAR_EDITOR_PROPERTY).toContain('threshold')
    })

    it('has at least 13 items', () => {
      expect(BAR_EDITOR_PROPERTY.length).toBeGreaterThanOrEqual(13)
    })
  })

  describe('BAR_RANGE_EDITOR_PROPERTY', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(BAR_RANGE_EDITOR_PROPERTY)).toBe(true)
      expect(BAR_RANGE_EDITOR_PROPERTY.length).toBeGreaterThan(0)
    })

    it('contains basic-style-selector', () => {
      expect(BAR_RANGE_EDITOR_PROPERTY).toContain('basic-style-selector')
    })

    it('does not contain assist-line (unlike BAR_EDITOR_PROPERTY)', () => {
      expect(BAR_RANGE_EDITOR_PROPERTY).not.toContain('assist-line')
    })
  })

  describe('BAR_EDITOR_PROPERTY_INNER', () => {
    it('is an object', () => {
      expect(typeof BAR_EDITOR_PROPERTY_INNER).toBe('object')
      expect(BAR_EDITOR_PROPERTY_INNER).not.toBeNull()
    })

    it('has basic-style-selector key mapping to an array', () => {
      expect(BAR_EDITOR_PROPERTY_INNER).toHaveProperty('basic-style-selector')
      expect(Array.isArray(BAR_EDITOR_PROPERTY_INNER['basic-style-selector'])).toBe(true)
    })

    it('basic-style-selector includes colors and alpha', () => {
      expect(BAR_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('colors')
      expect(BAR_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('alpha')
    })

    it('has expected top-level keys', () => {
      expect(BAR_EDITOR_PROPERTY_INNER).toHaveProperty('background-overall-component')
      expect(BAR_EDITOR_PROPERTY_INNER).toHaveProperty('border-style')
      expect(BAR_EDITOR_PROPERTY_INNER).toHaveProperty('label-selector')
      expect(BAR_EDITOR_PROPERTY_INNER).toHaveProperty('tooltip-selector')
      expect(BAR_EDITOR_PROPERTY_INNER).toHaveProperty('x-axis-selector')
      expect(BAR_EDITOR_PROPERTY_INNER).toHaveProperty('y-axis-selector')
      expect(BAR_EDITOR_PROPERTY_INNER).toHaveProperty('title-selector')
      expect(BAR_EDITOR_PROPERTY_INNER).toHaveProperty('legend-selector')
      expect(BAR_EDITOR_PROPERTY_INNER).toHaveProperty('function-cfg')
      expect(BAR_EDITOR_PROPERTY_INNER).toHaveProperty('threshold')
    })
  })

  describe('BAR_AXIS_TYPE', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(BAR_AXIS_TYPE)).toBe(true)
      expect(BAR_AXIS_TYPE.length).toBeGreaterThan(0)
    })

    it('contains expected axis types', () => {
      expect(BAR_AXIS_TYPE).toContain('xAxis')
      expect(BAR_AXIS_TYPE).toContain('yAxis')
      expect(BAR_AXIS_TYPE).toContain('filter')
      expect(BAR_AXIS_TYPE).toContain('drill')
      expect(BAR_AXIS_TYPE).toContain('extLabel')
      expect(BAR_AXIS_TYPE).toContain('extTooltip')
    })
  })
})
