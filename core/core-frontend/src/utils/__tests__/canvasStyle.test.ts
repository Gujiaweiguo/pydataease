import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/utils/translate', () => ({
  cos: vi.fn(() => 1),
  sin: vi.fn(() => 0)
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  CHART_FONT_FAMILY_MAP_TRANS: {},
  DEFAULT_COLOR_CASE: {},
  DEFAULT_COLOR_CASE_DARK: {}
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    canvasStyleData: {
      dashboard: { themeColor: 'light' },
      component: { chartColor: {}, chartTitle: {} }
    },
    componentData: [],
    canvasViewInfo: {}
  })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: vi.fn() } })
}))

vi.mock('@/views/chart/components/js/formatter', () => ({
  formatterViewInfo: {}
}))

import {
  colorRgb,
  getScaleValue,
  getStyle,
  recursionThemTransObj,
  seriesAdaptor
} from '../canvasStyle'

describe('canvasStyle utils', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('converts long hex colors to rgba with opacity', () => {
    expect(colorRgb('#AABBCC', 0.4)).toBe('rgba(170,187,204,0.4)')
  })

  it('converts short hex colors to rgba without opacity', () => {
    expect(colorRgb('#abc', undefined)).toBe('rgba(170,187,204)')
  })

  it('returns original values for non-hex colors', () => {
    expect(colorRgb('transparent', undefined)).toBe('transparent')
  })

  it('builds inline styles with px units, transforms, and normalized background opacity', () => {
    const style = getStyle({
      fontSize: 10,
      width: 120,
      height: 60,
      rotate: 45,
      opacity: 0.5,
      backgroundColor: '#ffffff'
    }) as Record<string, string>

    expect(style).toMatchObject({
      fontSize: '12px',
      width: '120px',
      height: '60px',
      transform: 'rotate(45deg)',
      backgroundColor: 'rgba(255,255,255,0.5)'
    })
    expect(style.opacity).toBeUndefined()
  })

  it('scales arrays and enforces a minimum value of one', () => {
    expect(getScaleValue([0.2, 3], 2)).toEqual([1, 6])
  })

  it('scales numbers and enforces a minimum value of one', () => {
    expect(getScaleValue(0.2, 2)).toBe(1)
    expect(getScaleValue(3, 2)).toBe(6)
  })

  it('applies theme colors recursively to nested objects', () => {
    const target = {
      textStyle: { color: 'old' },
      axisLabel: { color: 'old' },
      deep: { lineStyle: { color: 'old' } }
    }

    recursionThemTransObj(
      {
        textStyle: ['color'],
        axisLabel: ['color'],
        deep: { lineStyle: ['color'] }
      },
      target as any,
      '#123456'
    )

    expect(target).toEqual({
      textStyle: { color: '#123456' },
      axisLabel: { color: '#123456' },
      deep: { lineStyle: { color: '#123456' } }
    })
  })

  it('adds color settings to series label and tooltip formatters', () => {
    const template = {
      label: {
        seriesLabelFormatter: [{ name: 'a' }],
        seriesTooltipFormatter: [{ name: 'b' }]
      }
    } as any

    seriesAdaptor(template, '#ff9900')

    expect(template.label.seriesLabelFormatter[0].color).toBe('#ff9900')
    expect(template.label.seriesTooltipFormatter[0].color).toBe('#ff9900')
  })
})
