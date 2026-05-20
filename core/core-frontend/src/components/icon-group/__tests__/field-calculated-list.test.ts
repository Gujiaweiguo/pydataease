import { describe, it, expect, vi } from 'vitest'

vi.mock('@/assets/svg/icon_link-calculated_outlined.svg', () => ({ default: 'link-calc.svg' }))
vi.mock('@/assets/svg/icon_link-calculated_outlined-1.svg', () => ({ default: 'link-calc-1.svg' }))
vi.mock('@/assets/svg/icon_text-calculated_outlined.svg', () => ({ default: 'text-calc.svg' }))
vi.mock('@/assets/svg/icon_text-calculated_outlined-1.svg', () => ({ default: 'text-calc-1.svg' }))
vi.mock('@/assets/svg/icon_number-calculated_outlined.svg', () => ({ default: 'num-calc.svg' }))
vi.mock('@/assets/svg/icon_number-calculated_outlined-1.svg', () => ({ default: 'num-calc-1.svg' }))
vi.mock('@/assets/svg/icon_local-calculated_outlined.svg', () => ({ default: 'local-calc.svg' }))
vi.mock('@/assets/svg/icon_local-calculated_outlined-1.svg', () => ({
  default: 'local-calc-1.svg'
}))
vi.mock('@/assets/svg/icon_calendar-calculated_outlined.svg', () => ({ default: 'cal-calc.svg' }))
vi.mock('@/assets/svg/icon_calendar-calculated_outlined-1.svg', () => ({
  default: 'cal-calc-1.svg'
}))

import * as mod from '../field-calculated-list'

describe('field-calculated-list', () => {
  it('exports iconFieldCalculatedMap and iconFieldCalculatedQMap', () => {
    expect(mod.iconFieldCalculatedMap).toBeDefined()
    expect(mod.iconFieldCalculatedQMap).toBeDefined()
    expect(Array.isArray(mod.iconFieldCalculatedMap)).toBe(true)
    expect(Array.isArray(mod.iconFieldCalculatedQMap)).toBe(true)
  })

  it('both maps have the same length', () => {
    expect(mod.iconFieldCalculatedMap).toHaveLength(mod.iconFieldCalculatedQMap.length)
  })

  it('iconFieldCalculatedMap has 8 entries', () => {
    expect(mod.iconFieldCalculatedMap).toHaveLength(8)
  })

  it('iconFieldCalculatedMap contains "binary" string entry', () => {
    expect(mod.iconFieldCalculatedMap).toContain('binary')
  })

  it('iconFieldCalculatedQMap contains "binary" string entry', () => {
    expect(mod.iconFieldCalculatedQMap).toContain('binary')
  })

  it('non-binary entries are strings (SVG paths)', () => {
    mod.iconFieldCalculatedMap.forEach(entry => {
      expect(typeof entry).toBe('string')
    })
  })
})
