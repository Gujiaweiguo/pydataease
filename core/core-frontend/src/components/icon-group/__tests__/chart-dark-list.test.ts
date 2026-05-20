import { describe, it, expect, vi } from 'vitest'

vi.mock('@/assets/svg/rich-text-dark.svg', () => ({ default: 'rich-text-dark.svg' }))
vi.mock('@/assets/svg/empty-dark/icon_line_light.svg', () => ({ default: 'line-dark.svg' }))

vi.mock('../chart-dark-list-empty', () => ({
  iconChartMapEmpty: {}
}))

import * as mod from '../chart-dark-list'

describe('chart-dark-list', () => {
  it('exports iconChartDarkMap', () => {
    expect(mod.iconChartDarkMap).toBeDefined()
    expect(typeof mod.iconChartDarkMap).toBe('object')
  })

  it('contains base dark entries', () => {
    expect(mod.iconChartDarkMap).toHaveProperty('chart-mix-dual-line-dark')
    expect(mod.iconChartDarkMap).toHaveProperty('rich-text-dark')
  })

  it('has at least 2 entries', () => {
    expect(Object.keys(mod.iconChartDarkMap).length).toBeGreaterThanOrEqual(2)
  })
})
