import { describe, it, expect, vi } from 'vitest'

vi.mock('@/assets/svg/field_text.svg', () => ({ default: 'field_text.svg' }))
vi.mock('@/assets/svg/field_time.svg', () => ({ default: 'field_time.svg' }))
vi.mock('@/assets/svg/field_value.svg', () => ({ default: 'field_value.svg' }))
vi.mock('@/assets/svg/field_location.svg', () => ({ default: 'field_location.svg' }))
vi.mock('@/assets/svg/field_url.svg', () => ({ default: 'field_url.svg' }))

import * as mod from '../field-list'

describe('field-list', () => {
  it('exports iconFieldMap', () => {
    expect(mod.iconFieldMap).toBeDefined()
    expect(typeof mod.iconFieldMap).toBe('object')
  })

  it('contains expected field type keys', () => {
    expect(mod.iconFieldMap).toHaveProperty('text')
    expect(mod.iconFieldMap).toHaveProperty('value')
    expect(mod.iconFieldMap).toHaveProperty('location')
    expect(mod.iconFieldMap).toHaveProperty('time')
    expect(mod.iconFieldMap).toHaveProperty('url')
  })

  it('has exactly 5 entries', () => {
    expect(Object.keys(mod.iconFieldMap)).toHaveLength(5)
  })

  it('each entry maps to a string value', () => {
    Object.values(mod.iconFieldMap).forEach(val => {
      expect(typeof val).toBe('string')
    })
  })
})
