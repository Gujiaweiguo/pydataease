import { describe, expect, it } from 'vitest'
import { TABLE_EDITOR_PROPERTY, TABLE_EDITOR_PROPERTY_INNER } from '../common'

describe('table/common', () => {
  describe('TABLE_EDITOR_PROPERTY', () => {
    it('is a non-empty array', () => {
      expect(Array.isArray(TABLE_EDITOR_PROPERTY)).toBe(true)
      expect(TABLE_EDITOR_PROPERTY.length).toBeGreaterThan(0)
    })

    it('contains basic-style-selector', () => {
      expect(TABLE_EDITOR_PROPERTY).toContain('basic-style-selector')
    })

    it('contains table-specific editor properties', () => {
      expect(TABLE_EDITOR_PROPERTY).toContain('table-header-selector')
      expect(TABLE_EDITOR_PROPERTY).toContain('table-cell-selector')
      expect(TABLE_EDITOR_PROPERTY).toContain('summary-selector')
      expect(TABLE_EDITOR_PROPERTY).toContain('scroll-cfg')
    })

    it('contains common editor properties', () => {
      expect(TABLE_EDITOR_PROPERTY).toContain('background-overall-component')
      expect(TABLE_EDITOR_PROPERTY).toContain('border-style')
      expect(TABLE_EDITOR_PROPERTY).toContain('title-selector')
      expect(TABLE_EDITOR_PROPERTY).toContain('tooltip-selector')
      expect(TABLE_EDITOR_PROPERTY).toContain('function-cfg')
      expect(TABLE_EDITOR_PROPERTY).toContain('threshold')
      expect(TABLE_EDITOR_PROPERTY).toContain('jump-set')
      expect(TABLE_EDITOR_PROPERTY).toContain('linkage')
    })

    it('does not contain axis selectors (table has no axes)', () => {
      expect(TABLE_EDITOR_PROPERTY).not.toContain('x-axis-selector')
      expect(TABLE_EDITOR_PROPERTY).not.toContain('y-axis-selector')
    })
  })

  describe('TABLE_EDITOR_PROPERTY_INNER', () => {
    it('is an object', () => {
      expect(typeof TABLE_EDITOR_PROPERTY_INNER).toBe('object')
      expect(TABLE_EDITOR_PROPERTY_INNER).not.toBeNull()
    })

    it('has basic-style-selector key mapping to an array', () => {
      expect(TABLE_EDITOR_PROPERTY_INNER).toHaveProperty('basic-style-selector')
      expect(Array.isArray(TABLE_EDITOR_PROPERTY_INNER['basic-style-selector'])).toBe(true)
    })

    it('basic-style-selector includes table-specific properties', () => {
      expect(TABLE_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('tableColumnMode')
      expect(TABLE_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('tableBorderColor')
      expect(TABLE_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('tableScrollBarColor')
      expect(TABLE_EDITOR_PROPERTY_INNER['basic-style-selector']).toContain('alpha')
    })

    it('table-header-selector includes expected properties', () => {
      expect(TABLE_EDITOR_PROPERTY_INNER['table-header-selector']).toContain('tableHeaderBgColor')
      expect(TABLE_EDITOR_PROPERTY_INNER['table-header-selector']).toContain('tableTitleFontSize')
      expect(TABLE_EDITOR_PROPERTY_INNER['table-header-selector']).toContain('tableHeaderFontColor')
      expect(TABLE_EDITOR_PROPERTY_INNER['table-header-selector']).toContain('showIndex')
    })

    it('table-cell-selector includes expected properties', () => {
      expect(TABLE_EDITOR_PROPERTY_INNER['table-cell-selector']).toContain('tableItemBgColor')
      expect(TABLE_EDITOR_PROPERTY_INNER['table-cell-selector']).toContain('tableItemFontSize')
      expect(TABLE_EDITOR_PROPERTY_INNER['table-cell-selector']).toContain('tableFontColor')
      expect(TABLE_EDITOR_PROPERTY_INNER['table-cell-selector']).toContain('enableTableCrossBG')
    })

    it('threshold uses tableThreshold', () => {
      expect(TABLE_EDITOR_PROPERTY_INNER['threshold']).toContain('tableThreshold')
    })

    it('has expected top-level keys', () => {
      expect(TABLE_EDITOR_PROPERTY_INNER).toHaveProperty('background-overall-component')
      expect(TABLE_EDITOR_PROPERTY_INNER).toHaveProperty('border-style')
      expect(TABLE_EDITOR_PROPERTY_INNER).toHaveProperty('basic-style-selector')
      expect(TABLE_EDITOR_PROPERTY_INNER).toHaveProperty('table-header-selector')
      expect(TABLE_EDITOR_PROPERTY_INNER).toHaveProperty('table-cell-selector')
      expect(TABLE_EDITOR_PROPERTY_INNER).toHaveProperty('title-selector')
      expect(TABLE_EDITOR_PROPERTY_INNER).toHaveProperty('tooltip-selector')
      expect(TABLE_EDITOR_PROPERTY_INNER).toHaveProperty('function-cfg')
      expect(TABLE_EDITOR_PROPERTY_INNER).toHaveProperty('threshold')
    })
  })
})
