import { describe, it, expect, vi } from 'vitest'

vi.mock('@/assets/svg/icon_params_setting.svg', () => ({ default: 'params.svg' }))
vi.mock('@/assets/svg/filter.svg', () => ({ default: 'filter.svg' }))
vi.mock('@/assets/svg/picture-group.svg', () => ({ default: 'pic-group.svg' }))
vi.mock('@/assets/svg/rich-text.svg', () => ({ default: 'rich-text.svg' }))
vi.mock('@/assets/svg/empty-light/icon_line_light.svg', () => ({ default: 'line-light.svg' }))

import * as mod from '../chart-list-empty'

describe('chart-list-empty', () => {
  it('exports iconChartMapEmpty and iconChartMap', () => {
    expect(mod.iconChartMapEmpty).toBeDefined()
    expect(mod.iconChartMap).toBeDefined()
    expect(typeof mod.iconChartMapEmpty).toBe('object')
    expect(typeof mod.iconChartMap).toBe('object')
  })

  it('iconChartMapEmpty maps SVG file names to chart type strings', () => {
    expect(mod.iconChartMapEmpty['icon_bar_light']).toBe('bar')
    expect(mod.iconChartMapEmpty['icon_pie_light']).toBe('pie')
    expect(mod.iconChartMapEmpty['icon_line_light']).toBe('line')
    expect(mod.iconChartMapEmpty['icon_radar_light']).toBe('radar')
  })

  it('iconChartMapEmpty has all expected entries', () => {
    const keys = Object.keys(mod.iconChartMapEmpty)
    expect(keys.length).toBeGreaterThanOrEqual(30)
  })

  it('iconChartMap contains base entries', () => {
    expect(mod.iconChartMap).toHaveProperty('chart-mix-dual-line')
    expect(mod.iconChartMap).toHaveProperty('rich-text')
    expect(mod.iconChartMap).toHaveProperty('picture-group')
    expect(mod.iconChartMap).toHaveProperty('filter')
    expect(mod.iconChartMap).toHaveProperty('outerParams')
  })
})
