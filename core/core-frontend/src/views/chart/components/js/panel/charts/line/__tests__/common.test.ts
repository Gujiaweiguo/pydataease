import { describe, expect, it } from 'vitest'
import { LINE_EDITOR_PROPERTY, LINE_EDITOR_PROPERTY_INNER, LINE_AXIS_TYPE } from '../common'

describe('line/common', () => {
  describe('LINE_EDITOR_PROPERTY', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(LINE_EDITOR_PROPERTY)).toBe(true)
      expect(LINE_EDITOR_PROPERTY.length).toBeGreaterThan(0)
    })

    it('contains basic-style-selector', () => {
      expect(LINE_EDITOR_PROPERTY).toContain('basic-style-selector')
    })

    it('contains required editor properties', () => {
      expect(LINE_EDITOR_PROPERTY).toContain('background-overall-component')
      expect(LINE_EDITOR_PROPERTY).toContain('border-style')
      expect(LINE_EDITOR_PROPERTY).toContain('x-axis-selector')
      expect(LINE_EDITOR_PROPERTY).toContain('y-axis-selector')
      expect(LINE_EDITOR_PROPERTY).toContain('title-selector')
      expect(LINE_EDITOR_PROPERTY).toContain('legend-selector')
      expect(LINE_EDITOR_PROPERTY).toContain('label-selector')
      expect(LINE_EDITOR_PROPERTY).toContain('tooltip-selector')
      expect(LINE_EDITOR_PROPERTY).toContain('assist-line')
      expect(LINE_EDITOR_PROPERTY).toContain('function-cfg')
      expect(LINE_EDITOR_PROPERTY).toContain('threshold')
    })

    it('has at least 12 items', () => {
      expect(LINE_EDITOR_PROPERTY.length).toBeGreaterThanOrEqual(12)
    })
  })

  describe('LINE_EDITOR_PROPERTY_INNER', () => {
    it('is an object', () => {
      expect(typeof LINE_EDITOR_PROPERTY_INNER).toBe('object')
      expect(LINE_EDITOR_PROPERTY_INNER).not.toBeNull()
    })

    it('has basic-style-selector key mapping to an array', () => {
      expect(LINE_EDITOR_PROPERTY_INNER).toHaveProperty('basic-style-selector')
      expect(Array.isArray(LINE_EDITOR_PROPERTY_INNER['basic-style-selector'])).toBe(true)
    })

    it('basic-style-selector includes line-specific properties', () => {
      expect(LINE_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('colors')
      expect(LINE_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('alpha')
      expect(LINE_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('lineWidth')
      expect(LINE_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('lineSymbol')
      expect(LINE_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('lineSymbolSize')
      expect(LINE_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('lineSmooth')
    })

    it('has expected top-level keys', () => {
      expect(LINE_EDITOR_PROPERTY_INNER).toHaveProperty('background-overall-component')
      expect(LINE_EDITOR_PROPERTY_INNER).toHaveProperty('border-style')
      expect(LINE_EDITOR_PROPERTY_INNER).toHaveProperty('label-selector')
      expect(LINE_EDITOR_PROPERTY_INNER).toHaveProperty('tooltip-selector')
      expect(LINE_EDITOR_PROPERTY_INNER).toHaveProperty('x-axis-selector')
      expect(LINE_EDITOR_PROPERTY_INNER).toHaveProperty('y-axis-selector')
      expect(LINE_EDITOR_PROPERTY_INNER).toHaveProperty('title-selector')
      expect(LINE_EDITOR_PROPERTY_INNER).toHaveProperty('legend-selector')
      expect(LINE_EDITOR_PROPERTY_INNER).toHaveProperty('function-cfg')
      expect(LINE_EDITOR_PROPERTY_INNER).toHaveProperty('threshold')
    })
  })

  describe('LINE_AXIS_TYPE', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(LINE_AXIS_TYPE)).toBe(true)
      expect(LINE_AXIS_TYPE.length).toBeGreaterThan(0)
    })

    it('contains expected axis types', () => {
      expect(LINE_AXIS_TYPE).toContain('xAxis')
      expect(LINE_AXIS_TYPE).toContain('yAxis')
      expect(LINE_AXIS_TYPE).toContain('drill')
      expect(LINE_AXIS_TYPE).toContain('filter')
      expect(LINE_AXIS_TYPE).toContain('extLabel')
      expect(LINE_AXIS_TYPE).toContain('extTooltip')
    })
  })
})
