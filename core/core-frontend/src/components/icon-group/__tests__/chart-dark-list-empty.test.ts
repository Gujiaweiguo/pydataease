import { describe, it, expect, vi } from 'vitest'

vi.mock('@/assets/svg/rich-text-dark.svg', () => ({ default: 'rich-text-dark.svg' }))
vi.mock('@/assets/svg/empty-dark/icon_line_light.svg', () => ({ default: 'line-dark.svg' }))

import * as mod from '../chart-dark-list-empty'

describe('chart-dark-list-empty', () => {
  it('exports iconChartDarkMap and iconChartMapEmpty', () => {
    expect(mod.iconChartDarkMap).toBeDefined()
    expect(mod.iconChartMapEmpty).toBeDefined()
    expect(typeof mod.iconChartDarkMap).toBe('object')
    expect(typeof mod.iconChartMapEmpty).toBe('object')
  })

  it('iconChartMapEmpty maps to dark chart type strings', () => {
    expect(mod.iconChartMapEmpty['icon_bar_light']).toBe('bar-dark')
    expect(mod.iconChartMapEmpty['icon_pie_light']).toBe('pie-dark')
    expect(mod.iconChartMapEmpty['icon_line_light']).toBe('line-dark')
  })

  it('iconChartMapEmpty has all dark-suffixed values', () => {
    Object.values(mod.iconChartMapEmpty).forEach(val => {
      expect(val).toMatch(/-dark$/)
    })
  })

  it('iconChartDarkMap contains base dark entries', () => {
    expect(mod.iconChartDarkMap).toHaveProperty('chart-mix-dual-line-dark')
    expect(mod.iconChartDarkMap).toHaveProperty('rich-text-dark')
  })
})
