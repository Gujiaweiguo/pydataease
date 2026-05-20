import { describe, it, expect, vi } from 'vitest'

vi.mock('@/assets/svg/icon_params_setting.svg', () => ({ default: 'params.svg' }))
vi.mock('@/assets/svg/filter.svg', () => ({ default: 'filter.svg' }))
vi.mock('@/assets/svg/picture-group.svg', () => ({ default: 'pic-group.svg' }))
vi.mock('@/assets/svg/rich-text.svg', () => ({ default: 'rich-text.svg' }))
vi.mock('@/assets/svg/empty-light/icon_line_light.svg', () => ({ default: 'line-light.svg' }))

vi.mock('../chart-list-empty', () => ({
  iconChartMapEmpty: {}
}))

import * as mod from '../chart-list'

describe('chart-list', () => {
  it('exports iconChartMap', () => {
    expect(mod.iconChartMap).toBeDefined()
    expect(typeof mod.iconChartMap).toBe('object')
  })

  it('contains base chart entries', () => {
    expect(mod.iconChartMap).toHaveProperty('chart-mix-dual-line')
    expect(mod.iconChartMap).toHaveProperty('rich-text')
    expect(mod.iconChartMap).toHaveProperty('picture-group')
    expect(mod.iconChartMap).toHaveProperty('filter')
    expect(mod.iconChartMap).toHaveProperty('outerParams')
  })

  it('has at least 5 entries', () => {
    expect(Object.keys(mod.iconChartMap).length).toBeGreaterThanOrEqual(5)
  })
})
