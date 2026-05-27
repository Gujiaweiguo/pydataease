import { describe, it, expect, vi } from 'vitest'

const chartApiMocks = vi.hoisted(() => ({
  innerExportDataSetDetails: vi.fn(),
  innerExportDetails: vi.fn()
}))
const linkStoreState = vi.hoisted(() => ({
  getLinkToken: ''
}))
const appStoreState = vi.hoisted(() => ({
  getIsDataEaseBi: false,
  getIsIframe: false
}))

// Mock external modules that are imported at module level
vi.mock('@/store/modules/map', () => ({
  useMapStoreWithOut: () => ({})
}))
vi.mock('@/api/map', () => ({ getGeoJson: vi.fn() }))
vi.mock('@/api/chart', () => ({
  innerExportDataSetDetails: chartApiMocks.innerExportDataSetDetails,
  innerExportDetails: chartApiMocks.innerExportDetails
}))
vi.mock('element-plus-secondary', () => ({
  ElMessage: { error: vi.fn() }
}))
vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))
vi.mock('@/store/modules/link', () => ({
  useLinkStoreWithOut: () => linkStoreState
}))
vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => appStoreState
}))

import {
  hexColorToRGBA,
  digToHex,
  customSort,
  customColor,
  parseJson,
  flow,
  isAlphaColor,
  convertToAlphaColor,
  getColorFormAlphaColor,
  isTransparent,
  exportExcelDownload
} from '../util'

// ---------------------------------------------------------------------------
// hexColorToRGBA
// ---------------------------------------------------------------------------
describe('hexColorToRGBA', () => {
  it('converts 6-digit hex to rgba', () => {
    expect(hexColorToRGBA('#FF0000', 100)).toBe('rgba(255,0,0,1)')
  })

  it('converts 3-digit hex to rgba', () => {
    expect(hexColorToRGBA('#F00', 50)).toBe('rgba(255,0,0,0.5)')
  })

  it('converts lowercase hex to rgba', () => {
    expect(hexColorToRGBA('#00ff00', 80)).toBe('rgba(0,255,0,0.8)')
  })

  it('converts rgb string to rgba', () => {
    expect(hexColorToRGBA('rgb(100,200,50)', 60)).toBe('rgba(100,200,50,0.6)')
  })

  it('returns black for invalid hex', () => {
    expect(hexColorToRGBA('#ZZZZZZ', 100)).toBe('rgb(0,0,0)')
  })
})

// ---------------------------------------------------------------------------
// digToHex
// ---------------------------------------------------------------------------
describe('digToHex', () => {
  it('converts 100 to FE (floating-point rounding)', () => {
    // 100 * 2.55 = 254.9999... → parseInt → 254 → FE
    expect(digToHex(100)).toBe('FE')
  })

  it('converts 0 to 00', () => {
    expect(digToHex(0)).toBe('00')
  })

  it('converts 50 to ~7F', () => {
    const result = digToHex(50)
    // 50 * 2.55 = 127.5 → parseInt → 127 → 7F
    expect(result).toBe('7F')
  })

  it('pads small values with leading zero', () => {
    // 5 * 2.55 = 12.75 → parseInt → 12 → 0C
    expect(digToHex(5)).toBe('0C')
  })
})

// ---------------------------------------------------------------------------
// customSort
// ---------------------------------------------------------------------------
describe('customSort', () => {
  it('sorts data by custom field order', () => {
    const custom = ['b', 'a']
    const data = [
      { field: 'a', value: 1 },
      { field: 'b', value: 2 },
      { field: 'c', value: 3 }
    ]
    const result = customSort(custom, data)
    expect(result.map(d => d.field)).toEqual(['b', 'a', 'c'])
  })

  it('returns all data when custom is empty', () => {
    const data = [{ field: 'x' }, { field: 'y' }]
    const result = customSort([], data)
    expect(result).toEqual(data)
  })
})

// ---------------------------------------------------------------------------
// customColor
// ---------------------------------------------------------------------------
describe('customColor', () => {
  it('merges custom colors into res by name', () => {
    const custom = [{ name: 'A', color: '#ff0000', isCustom: true }]
    const res = [
      { name: 'A', color: '#000000', isCustom: false },
      { name: 'B', color: '#00ff00', isCustom: false }
    ]
    const result = customColor(custom, res)
    expect(result[0].color).toBe('#ff0000')
    expect(result[1].color).toBe('#00ff00')
  })

  it('keeps all res items even when no custom matches', () => {
    const custom = [{ name: 'X', color: '#ffffff', isCustom: true }]
    const res = [{ name: 'A', color: '#000' }]
    const result = customColor(custom, res)
    expect(result).toHaveLength(1)
    expect(result[0].name).toBe('A')
  })
})

// ---------------------------------------------------------------------------
// parseJson
// ---------------------------------------------------------------------------
describe('parseJson', () => {
  it('parses JSON string', () => {
    expect(parseJson('{"a":1}')).toEqual({ a: 1 })
  })

  it('returns non-string as-is', () => {
    const obj = { a: 1 }
    expect(parseJson(obj)).toBe(obj)
  })

  it('parses array string', () => {
    expect(parseJson('[1,2,3]')).toEqual([1, 2, 3])
  })
})

// ---------------------------------------------------------------------------
// flow
// ---------------------------------------------------------------------------
describe('flow', () => {
  it('composes functions left-to-right', () => {
    const add1 = (_p: any, r: number) => r + 1
    const mul2 = (_p: any, r: number) => r * 2
    const composed = flow(add1, mul2)
    // (0 + 1) * 2 = 2
    expect(composed(null, 0)).toBe(2)
  })

  it('works with single function', () => {
    const fn = (_p: any, r: string) => r.toUpperCase()
    const composed = flow(fn)
    expect(composed(null, 'hello')).toBe('HELLO')
  })

  it('passes context to each step', () => {
    const fn = (_p: any, r: number, ctx?: any) => r + (ctx?.offset ?? 0)
    const composed = flow(fn, fn)
    expect(composed(null, 0, { offset: 5 })).toBe(10)
  })

  it('calls functions with thisArg when provided', () => {
    const obj = { multiplier: 3 }
    const fn = function (this: any, _p: any, r: number) {
      return r * this.multiplier
    }
    const composed = flow(fn)
    expect(composed(null, 4, undefined, obj)).toBe(12)
  })
})

// ---------------------------------------------------------------------------
// isAlphaColor
// ---------------------------------------------------------------------------
describe('isAlphaColor', () => {
  it('returns true for 8-char hex (#RRGGBBAA)', () => {
    expect(isAlphaColor('#FF0000FF')).toBe(true)
  })

  it('returns false for 6-char hex (#RRGGBB)', () => {
    expect(isAlphaColor('#FF0000')).toBe(false)
  })

  it('returns true for rgba string', () => {
    expect(isAlphaColor('rgba(255,0,0,0.5)')).toBe(true)
  })

  it('returns false for rgb string', () => {
    expect(isAlphaColor('rgb(255,0,0)')).toBe(false)
  })

  it('returns false for empty string', () => {
    expect(isAlphaColor('')).toBe(false)
  })

  it('returns false for whitespace', () => {
    expect(isAlphaColor('   ')).toBe(false)
  })
})

// ---------------------------------------------------------------------------
// convertToAlphaColor
// ---------------------------------------------------------------------------
describe('convertToAlphaColor', () => {
  it('converts 6-digit hex with alpha', () => {
    const result = convertToAlphaColor('#FF0000', 100)
    expect(result).toBe('#FF0000FF')
  })

  it('converts 3-digit hex with alpha', () => {
    const result = convertToAlphaColor('#F00', 50)
    expect(result).toMatch(/^#[0-9A-F]{8}$/)
  })

  it('converts rgb string with alpha', () => {
    const result = convertToAlphaColor('rgb(255,0,0)', 80)
    expect(result).toBe('rgba(255,0,0,0.8)')
  })

  it('returns white for empty string', () => {
    expect(convertToAlphaColor('', 50)).toBe('rgba(255,255,255,1)')
  })

  it('returns white for whitespace', () => {
    expect(convertToAlphaColor('   ', 50)).toBe('rgba(255,255,255,1)')
  })
})

// ---------------------------------------------------------------------------
// getColorFormAlphaColor
// ---------------------------------------------------------------------------
describe('getColorFormAlphaColor', () => {
  it('strips alpha from 8-char hex', () => {
    expect(getColorFormAlphaColor('#FF0000AA')).toBe('#FF0000')
  })

  it('strips alpha from rgba string', () => {
    expect(getColorFormAlphaColor('rgba(255,0,0,0.5)')).toBe('rgba(255,0,0)')
  })

  it('returns color as-is if not alpha', () => {
    expect(getColorFormAlphaColor('#FF0000')).toBe('#FF0000')
  })
})

// ---------------------------------------------------------------------------
// isTransparent
// ---------------------------------------------------------------------------
describe('isTransparent', () => {
  it('returns true for empty string', () => {
    expect(isTransparent('')).toBe(true)
  })

  it('returns true for whitespace', () => {
    expect(isTransparent('   ')).toBe(true)
  })

  it('returns false for opaque hex', () => {
    expect(isTransparent('#FF0000')).toBe(false)
  })

  it('returns true for hex with 00 alpha', () => {
    expect(isTransparent('#FF000000')).toBe(true)
  })

  it('returns false for hex with non-zero alpha', () => {
    expect(isTransparent('#FF0000FF')).toBe(false)
  })

  it('returns true for rgba with alpha 0', () => {
    expect(isTransparent('rgba(255,0,0,0)')).toBe(true)
  })

  it('returns false for rgba with non-zero alpha', () => {
    expect(isTransparent('rgba(255,0,0,0.5)')).toBe(false)
  })
})

describe('exportExcelDownload', () => {
  it('builds excel request from flat series data and opens export center callback in normal mode', async () => {
    chartApiMocks.innerExportDetails.mockResolvedValue({ data: { code: 0 } })
    linkStoreState.getLinkToken = ''
    appStoreState.getIsDataEaseBi = false
    appStoreState.getIsIframe = false
    const callback = vi.fn()

    await exportExcelDownload(
      {
        id: 'view-1',
        sceneId: 'dv-1',
        title: '销售额走势',
        type: 'area',
        xAxis: [{ name: '销售日期', dataeaseName: 'sale_date', deType: 1 }],
        yAxis: [{ name: '销售金额', dataeaseName: 'amount', deType: 2 }],
        data: [
          {
            field: '2024-03-10',
            value: 956,
            category: '销售金额',
            dimensionList: [{ value: '2024-03-10' }]
          }
        ]
      },
      '看板',
      callback
    )

    expect(chartApiMocks.innerExportDetails).toHaveBeenCalledOnce()
    const request = chartApiMocks.innerExportDetails.mock.calls[0][0]
    expect(request.header).toEqual(['销售日期', '销售金额'])
    expect(request.details).toEqual([['2024-03-10', 956]])
    expect(callback).toHaveBeenCalledWith({ data: { code: 0 } })
  })

  it('forces direct download mode for link-token users', async () => {
    chartApiMocks.innerExportDetails.mockResolvedValue({ data: new Blob(['xlsx']) })
    linkStoreState.getLinkToken = 'token-1'
    appStoreState.getIsDataEaseBi = false
    appStoreState.getIsIframe = false
    const createObjectURL = vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:url')
    const revokeObjectURL = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => undefined)

    await exportExcelDownload(
      {
        id: 'view-2',
        sceneId: 'dv-1',
        title: '冷热占比',
        type: 'pie-donut',
        xAxis: [{ name: '冷热', dataeaseName: 'hot_cold', deType: 0 }],
        yAxis: [{ name: '记录数*', dataeaseName: 'value', deType: 2 }],
        data: [
          {
            field: '冷',
            value: 82,
            category: '记录数*',
            dimensionList: [{ value: '冷' }]
          }
        ]
      },
      '看板'
    )

    const request = chartApiMocks.innerExportDetails.mock.calls.at(-1)?.[0]
    expect(request.dataEaseBi).toBe(true)
    expect(createObjectURL).toHaveBeenCalled()
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:url')

    createObjectURL.mockRestore()
    revokeObjectURL.mockRestore()
    linkStoreState.getLinkToken = ''
  })
})
