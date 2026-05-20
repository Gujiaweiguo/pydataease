/* eslint-disable @typescript-eslint/no-empty-function */
import { describe, expect, it, vi } from 'vitest'

vi.mock('@antv/s2', () => {
  class MockClass {
    constructor(..._args: any[]) {}
  }
  return {
    BaseTooltip: MockClass,
    DataCellBrushSelection: MockClass,
    FONT_FAMILY: 'sans-serif',
    getAutoAdjustPosition: vi.fn(),
    getEmptyPlaceholder: vi.fn(),
    getPolygonPoints: vi.fn(),
    getTooltipDefaultOptions: vi.fn(),
    InteractionName: {},
    InteractionStateName: {},
    MergedCell: MockClass,
    MergedCellInfo: {},
    Meta: {},
    Node: {},
    PivotSheet: MockClass,
    renderPolygon: vi.fn(),
    renderText: vi.fn(),
    S2DataConfig: {},
    S2Event: {},
    S2Options: {},
    S2Theme: {},
    SERIES_NUMBER_FIELD: '__SERIAL_NUMBER__',
    EXTRA_FIELD: '__EXTRA_FIELD__',
    setTooltipContainerStyle: vi.fn(),
    SHAPE_STYLE_MAP: {},
    SpreadSheet: MockClass,
    Style: {},
    TableColCell: MockClass,
    TableDataCell: MockClass,
    updateShapeAttr: vi.fn(),
    ViewMeta: {}
  }
})
vi.mock('../../..//util', () => ({
  copyString: vi.fn(),
  hexColorToRGBA: vi.fn((_c: string, _a: number) => 'rgba(0,0,0,1)'),
  isAlphaColor: vi.fn(() => false),
  isTransparent: vi.fn(() => false),
  parseJson: vi.fn((s: any) => (typeof s === 'string' ? JSON.parse(s) : s)),
  resetRgbOpacity: vi.fn(),
  safeDecimalSum: vi.fn(),
  safeDecimalMean: vi.fn()
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  DEFAULT_BASIC_STYLE: { alpha: 1, tableBorderColor: '#ccc', tableScrollBarColor: '#999' },
  DEFAULT_TABLE_CELL: { tableItemBgColor: '#fff', tableItemAlign: 'left' },
  DEFAULT_TABLE_HEADER: { tableHeaderBgColor: '#eee', tableHeaderAlign: 'center' }
}))
vi.mock('lodash-es', () => ({
  cloneDeep: vi.fn((v: any) => JSON.parse(JSON.stringify(v))),
  filter: vi.fn(),
  find: vi.fn(),
  intersection: vi.fn(),
  keys: vi.fn(),
  map: vi.fn(),
  maxBy: vi.fn(),
  merge: vi.fn(),
  minBy: vi.fn(),
  repeat: vi.fn(),
  isNumber: vi.fn((v: any) => typeof v === 'number')
}))
vi.mock('vue', () => ({
  createVNode: vi.fn(),
  render: vi.fn()
}))
vi.mock('@/views/chart/components/editor/common/TableTooltip.vue', () => ({
  default: {}
}))
vi.mock('exceljs', () => ({}))
vi.mock('file-saver', () => ({ saveAs: vi.fn() }))
vi.mock('element-plus-secondary', () => ({
  ElMessage: { success: vi.fn(), warning: vi.fn() }
}))
vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {},
  PATH_URL: '/'
}))
vi.mock('@/config/axios/hmac', () => ({
  hmacSign: vi.fn()
}))
vi.mock('@/components/plugin/src/ImportXpackTool', () => ({
  PATH_URL: '/'
}))
vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({ baseUrl: '' })
}))
vi.mock('@/api/plugin', () => ({
  xpackModelApi: {}
}))
vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({ wsCache: { get: vi.fn(), set: vi.fn() } })
}))
vi.mock('decimal.js', () => ({
  default: class Decimal {
    value: number
    constructor(v: number) {
      this.value = v
    }
    plus(v: number) {
      return new Decimal(this.value + v)
    }
    toNumber() {
      return this.value
    }
  }
}))

import { getCurrentField, getRowIndex } from '../common_table'

describe('common_table pure functions', () => {
  describe('getCurrentField', () => {
    it('returns null for empty list', () => {
      const result = getCurrentField([], { dataeaseName: 'f1' } as any)
      expect(result).toBeNull()
    })

    it('returns matching field from array', () => {
      const fields = [
        { dataeaseName: 'f1', name: 'Field 1' },
        { dataeaseName: 'f2', name: 'Field 2' }
      ]
      const result = getCurrentField(fields as any[], { dataeaseName: 'f2' } as any)
      expect(result).toEqual({ dataeaseName: 'f2', name: 'Field 2' })
    })

    it('returns null when no field matches', () => {
      const fields = [{ dataeaseName: 'f1', name: 'Field 1' }]
      const result = getCurrentField(fields as any[], { dataeaseName: 'f99' } as any)
      expect(result).toBeNull()
    })

    it('returns first matching field', () => {
      const fields = [
        { dataeaseName: 'f1', name: 'First' },
        { dataeaseName: 'f1', name: 'Second' }
      ]
      const result = getCurrentField(fields as any[], { dataeaseName: 'f1' } as any)
      expect(result).toEqual({ dataeaseName: 'f1', name: 'First' })
    })

    it('handles JSON-stringified valueFieldList', () => {
      const fields = JSON.stringify([{ dataeaseName: 'f1', name: 'Field 1' }])
      const result = getCurrentField(fields as any, { dataeaseName: 'f1' } as any)
      expect(result).toEqual({ dataeaseName: 'f1', name: 'Field 1' })
    })
  })

  describe('getRowIndex', () => {
    it('returns rowIndex + 1 when no mergedCellsInfo', () => {
      const meta = { rowIndex: 5 } as any
      expect(getRowIndex([], meta)).toBe(6)
    })

    it('returns rowIndex + 1 when mergedCellsInfo is undefined', () => {
      const meta = { rowIndex: 3 } as any
      expect(getRowIndex(undefined as any, meta)).toBe(4)
    })

    it('accounts for lost cells from merged ranges', () => {
      const mergedCellsInfo = [
        [
          { rowIndex: 0, colIndex: 0 },
          { rowIndex: 1, colIndex: 0 }
        ]
      ] as any[][]
      const meta = { rowIndex: 2 } as any
      // merged range rows 0-1, lost = 1-0 = 1, meta.rowIndex=2 > end=1, so lostCells=1
      // result = 2 - 1 + 1 = 2
      expect(getRowIndex(mergedCellsInfo, meta)).toBe(2)
    })

    it('skips merged ranges that do not start at colIndex 0', () => {
      const mergedCellsInfo = [
        [
          { rowIndex: 0, colIndex: 1 },
          { rowIndex: 1, colIndex: 1 }
        ]
      ] as any[][]
      const meta = { rowIndex: 2 } as any
      // colIndex !== 0, skipped entirely, lostCells = 0, result = 2 + 1 = 3
      expect(getRowIndex(mergedCellsInfo, meta)).toBe(3)
    })

    it('adjusts curRangeStartIndex when meta is inside a merged range', () => {
      const mergedCellsInfo = [
        [
          { rowIndex: 0, colIndex: 0 },
          { rowIndex: 2, colIndex: 0 }
        ]
      ] as any[][]
      const meta = { rowIndex: 1 } as any
      // start=0, end=2, meta.rowIndex=1 is inside [0,2], curRangeStartIndex=0
      // lost = 2-0 = 2, but meta.rowIndex(1) <= end(2) so no addition to lostCells
      // result = 0 - 0 + 1 = 1
      expect(getRowIndex(mergedCellsInfo, meta)).toBe(1)
    })
  })
})
