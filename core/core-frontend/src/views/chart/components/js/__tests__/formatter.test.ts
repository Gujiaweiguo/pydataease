import { describe, expect, it, vi } from 'vitest'

vi.mock('@/utils/utils', () => ({
  getLocale: () => 'zh-CN'
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/views/chart/components/js/util', () => ({
  parseJson: (s: string) => JSON.parse(s),
  isParent: () => false
}))

vi.mock('lodash-es', () => ({
  find: (arr: any[], fn: any) => arr.find(fn),
  merge: (target: any, ...sources: any[]) => {
    for (const source of sources) {
      if (source) {
        for (const key of Object.keys(source)) {
          if (
            source[key] &&
            typeof source[key] === 'object' &&
            !Array.isArray(source[key]) &&
            target[key] &&
            typeof target[key] === 'object' &&
            !Array.isArray(target[key])
          ) {
            const innerT = target[key]
            const innerS = source[key]
            for (const ik of Object.keys(innerS)) {
              innerT[ik] = innerS[ik]
            }
          } else {
            target[key] = source[key]
          }
        }
      }
    }
    return target
  }
}))

import {
  isEnLocal,
  formatterItem,
  unitType,
  unitEnType,
  getUnitTypeList,
  getUnitTypeValue,
  initFormatCfgUnit,
  onChangeFormatCfgUnitLanguage,
  formatterType,
  valueFormatter,
  listenYAxisNiceMinEvents,
  calcNiceMinValue,
  formatterViewInfo,
  mergeTooltipFormat
} from '../formatter'

describe('isEnLocal', () => {
  it('returns false when locale is zh-CN', () => {
    expect(isEnLocal).toBe(false)
  })
})

describe('formatterItem', () => {
  it('has expected default properties', () => {
    expect(formatterItem.type).toBe('auto')
    expect(formatterItem.unitLanguage).toBe('ch')
    expect(formatterItem.unit).toBe(1)
    expect(formatterItem.suffix).toBe('')
    expect(formatterItem.decimalCount).toBe(2)
    expect(formatterItem.thousandSeparator).toBe(true)
  })
})

describe('unitType', () => {
  it('contains 5 Chinese unit entries', () => {
    expect(unitType).toHaveLength(5)
    expect(unitType.map(u => u.value)).toEqual([1, 1000, 10000, 1000000, 100000000])
  })
})

describe('unitEnType', () => {
  it('contains 4 English unit entries', () => {
    expect(unitEnType).toHaveLength(4)
    expect(unitEnType.map(u => u.value)).toEqual([1, 1000, 1000000, 1000000000])
  })
})

describe('formatterType', () => {
  it('has auto, value, and percent types', () => {
    expect(formatterType).toHaveLength(3)
    expect(formatterType.map(t => t.value)).toEqual(['auto', 'value', 'percent'])
  })
})

describe('getUnitTypeList', () => {
  it('returns unitType when lang is ch', () => {
    expect(getUnitTypeList('ch')).toBe(unitType)
  })

  it('returns unitEnType when lang is not ch', () => {
    expect(getUnitTypeList('en')).toBe(unitEnType)
    expect(getUnitTypeList('fr')).toBe(unitEnType)
  })
})

describe('getUnitTypeValue', () => {
  it('returns the value when it exists in the unit list', () => {
    expect(getUnitTypeValue('ch', 1)).toBe(1)
    expect(getUnitTypeValue('ch', 1000)).toBe(1000)
    expect(getUnitTypeValue('ch', 10000)).toBe(10000)
    expect(getUnitTypeValue('en', 1000)).toBe(1000)
    expect(getUnitTypeValue('en', 1000000)).toBe(1000000)
  })

  it('returns 1 when value does not exist in the unit list', () => {
    expect(getUnitTypeValue('ch', 999)).toBe(1)
    expect(getUnitTypeValue('ch', 500)).toBe(1)
    expect(getUnitTypeValue('en', 500)).toBe(1)
  })
})

describe('initFormatCfgUnit', () => {
  it('sets unitLanguage to ch when undefined', () => {
    const cfg: Record<string, any> = { unit: 1 }
    initFormatCfgUnit(cfg)
    expect(cfg.unitLanguage).toBe('ch')
  })

  it('does not overwrite unitLanguage when already set', () => {
    const cfg: Record<string, any> = { unit: 1, unitLanguage: 'en' }
    initFormatCfgUnit(cfg)
    expect(cfg.unitLanguage).toBe('en')
  })

  it('throws on null cfg', () => {
    expect(() => initFormatCfgUnit(null)).toThrow()
  })

  it('throws on undefined cfg', () => {
    expect(() => initFormatCfgUnit(undefined)).toThrow()
  })
})

describe('onChangeFormatCfgUnitLanguage', () => {
  it('keeps unit when valid in the chosen language list', () => {
    const cfg: Record<string, any> = { unit: 1000, unitLanguage: 'ch' }
    onChangeFormatCfgUnitLanguage(cfg, 'ch')
    expect(cfg.unit).toBe(1000)
  })

  it('resets unit to 1 when not valid in the chosen language list', () => {
    const cfg: Record<string, any> = { unit: 1000000000, unitLanguage: 'ch' }
    onChangeFormatCfgUnitLanguage(cfg, 'ch')
    expect(cfg.unit).toBe(1)
  })
})

describe('valueFormatter', () => {
  const baseCfg = {
    type: 'value',
    unitLanguage: 'ch',
    unit: 1,
    suffix: '',
    decimalCount: 2,
    thousandSeparator: true
  }

  it('returns null for null', () => {
    expect(valueFormatter(null, { ...baseCfg })).toBeNull()
  })

  it('returns null for undefined', () => {
    expect(valueFormatter(undefined, { ...baseCfg })).toBeNull()
  })

  describe('type=auto', () => {
    const autoCfg = { ...baseCfg, type: 'auto' }

    it('formats a simple integer with thousand separator', () => {
      expect(valueFormatter(1234, { ...autoCfg })).toBe('1,234')
    })

    it('formats zero', () => {
      expect(valueFormatter(0, { ...autoCfg })).toBe('0')
    })

    it('formats a negative number', () => {
      expect(valueFormatter(-5678, { ...autoCfg })).toBe('-5,678')
    })
  })

  describe('type=value', () => {
    it('formats with decimal places', () => {
      expect(valueFormatter(1234.567, { ...baseCfg })).toBe('1,234.57')
    })

    it('formats without thousand separator', () => {
      expect(valueFormatter(1234.567, { ...baseCfg, thousandSeparator: false })).toBe('1234.57')
    })

    it('pads decimal with zeros', () => {
      expect(valueFormatter(5, { ...baseCfg })).toBe('5.00')
    })

    it('handles zero', () => {
      expect(valueFormatter(0, { ...baseCfg })).toBe('0.00')
    })

    it('handles negative numbers', () => {
      expect(valueFormatter(-1234.5, { ...baseCfg })).toBe('-1,234.50')
    })

    it('respects decimalCount=0', () => {
      expect(valueFormatter(1234.567, { ...baseCfg, decimalCount: 0 })).toBe('1,235')
    })

    it('respects decimalCount=4', () => {
      expect(valueFormatter(1.2, { ...baseCfg, decimalCount: 4 })).toBe('1.2000')
    })

    it('trims whitespace from suffix before appending', () => {
      expect(valueFormatter(100, { ...baseCfg, suffix: ' USD' })).toBe('100.00USD')
    })

    it('applies unit division (thousands) and appends Chinese unit suffix', () => {
      expect(valueFormatter(1234.567, { ...baseCfg, unit: 1000 })).toBe('1.23chart.unit_thousand')
    })

    it('applies unit division (ten thousands) and appends Chinese unit suffix', () => {
      expect(valueFormatter(12345, { ...baseCfg, unit: 10000 })).toBe('1.23chart.unit_ten_thousand')
    })

    it('appends Chinese unit suffix for unit=1000', () => {
      const result = valueFormatter(5000, { ...baseCfg, unit: 1000, decimalCount: 2 })
      expect(result).toBe('5.00chart.unit_thousand')
    })

    it('appends English unit suffix K for unit=1000 (en)', () => {
      const result = valueFormatter(5000, {
        ...baseCfg,
        unit: 1000,
        unitLanguage: 'en',
        decimalCount: 2
      })
      expect(result).toBe('5.00K')
    })

    it('appends English unit suffix M for unit=1000000 (en)', () => {
      const result = valueFormatter(5000000, {
        ...baseCfg,
        unit: 1000000,
        unitLanguage: 'en',
        decimalCount: 2
      })
      expect(result).toBe('5.00M')
    })

    it('appends English unit suffix B for unit=1000000000 (en)', () => {
      const result = valueFormatter(5000000000, {
        ...baseCfg,
        unit: 1000000000,
        unitLanguage: 'en',
        decimalCount: 2
      })
      expect(result).toBe('5.00B')
    })

    it('appends Chinese unit suffix for unit=10000', () => {
      const result = valueFormatter(50000, { ...baseCfg, unit: 10000, decimalCount: 2 })
      expect(result).toBe('5.00chart.unit_ten_thousand')
    })

    it('appends Chinese unit suffix for unit=1000000', () => {
      const result = valueFormatter(5000000, { ...baseCfg, unit: 1000000, decimalCount: 2 })
      expect(result).toBe('5.00chart.unit_million')
    })

    it('appends Chinese unit suffix for unit=100000000', () => {
      const result = valueFormatter(500000000, { ...baseCfg, unit: 100000000, decimalCount: 2 })
      expect(result).toBe('5.00chart.unit_hundred_million')
    })

    it('strips leading minus for -0 edge case', () => {
      expect(valueFormatter(-0.001, { ...baseCfg })).toBe('0.00')
    })
  })

  describe('type=percent', () => {
    const pctCfg = { ...baseCfg, type: 'percent' }

    it('multiplies by 100 and appends %', () => {
      expect(valueFormatter(0.5678, { ...pctCfg })).toBe('56.78%')
    })

    it('formats 1 as 100%', () => {
      expect(valueFormatter(1, { ...pctCfg })).toBe('100.00%')
    })

    it('formats 0 as 0.00%', () => {
      expect(valueFormatter(0, { ...pctCfg })).toBe('0.00%')
    })

    it('handles negative percentage', () => {
      expect(valueFormatter(-0.25, { ...pctCfg })).toBe('-25.00%')
    })

    it('respects decimalCount for percent', () => {
      expect(valueFormatter(0.12345, { ...pctCfg, decimalCount: 0 })).toBe('12%')
    })

    it('does not add unit suffix for percent type', () => {
      const result = valueFormatter(0.5, { ...pctCfg, unit: 1000 })
      expect(result).toBe('50.00%')
    })
  })

  describe('unknown type', () => {
    it('returns raw value', () => {
      expect(valueFormatter(42, { ...baseCfg, type: 'unknown' })).toBe(42)
    })
  })

  describe('scientific notation edge case', () => {
    it('handles very small numbers without e- in output', () => {
      const cfg = { ...baseCfg, type: 'value', unit: 1, decimalCount: 2, thousandSeparator: true }
      const result = valueFormatter(0.0000001, cfg)
      expect(typeof result).toBe('string')
      expect(result).not.toMatch(/e-/)
    })
  })
})

describe('formatterViewInfo', () => {
  const createViewInfo = () => ({
    type: 'bar',
    xAxis: [{ formatterCfg: { type: 'auto' } as Record<string, any> }],
    xAxisExt: [{ formatterCfg: { type: 'auto' } as Record<string, any> }],
    yAxis: [{ formatterCfg: { type: 'auto' } as Record<string, any> }],
    extStack: [{ formatterCfg: { type: 'auto' } as Record<string, any> }],
    extBubble: [{ formatterCfg: { type: 'auto' } as Record<string, any> }],
    extLabel: [{ formatterCfg: { type: 'auto' } as Record<string, any> }],
    extTooltip: [{ formatterCfg: { type: 'auto' } as Record<string, any> }],
    customAttr: {
      label: {
        labelFormatter: { type: 'auto' } as Record<string, any>,
        quotaLabelFormatter: { type: 'auto' } as Record<string, any>,
        seriesLabelFormatter: [{ formatterCfg: { type: 'auto' } as Record<string, any> }],
        totalFormatter: { type: 'auto' } as Record<string, any>
      },
      tooltip: {
        tooltipFormatter: { type: 'auto' } as Record<string, any>,
        seriesTooltipFormatter: [{ formatterCfg: { type: 'auto' } as Record<string, any> }]
      }
    },
    customStyle: {
      xAxis: { axisLabelFormatter: { type: 'auto' } as Record<string, any> },
      yAxis: { axisLabelFormatter: { type: 'auto' } as Record<string, any> },
      yAxisExt: { axisLabelFormatter: { type: 'auto' } as Record<string, any> }
    }
  })

  it('merges value into all axis formatterCfg fields', () => {
    const viewInfo = createViewInfo()
    formatterViewInfo(viewInfo, { decimalCount: 4 })

    expect(viewInfo.xAxis[0].formatterCfg.decimalCount).toBe(4)
    expect(viewInfo.xAxisExt[0].formatterCfg.decimalCount).toBe(4)
    expect(viewInfo.yAxis[0].formatterCfg.decimalCount).toBe(4)
    expect(viewInfo.extStack[0].formatterCfg.decimalCount).toBe(4)
    expect(viewInfo.extBubble[0].formatterCfg.decimalCount).toBe(4)
    expect(viewInfo.extLabel[0].formatterCfg.decimalCount).toBe(4)
    expect(viewInfo.extTooltip[0].formatterCfg.decimalCount).toBe(4)
  })

  it('merges value into label formatters', () => {
    const viewInfo = createViewInfo()
    formatterViewInfo(viewInfo, { suffix: ' USD' })

    expect(viewInfo.customAttr.label.labelFormatter.suffix).toBe(' USD')
    expect(viewInfo.customAttr.label.quotaLabelFormatter.suffix).toBe(' USD')
    expect(viewInfo.customAttr.label.seriesLabelFormatter[0].formatterCfg.suffix).toBe(' USD')
    expect(viewInfo.customAttr.label.totalFormatter.suffix).toBe(' USD')
  })

  it('merges value into tooltip formatters for non-excluded type', () => {
    const viewInfo = createViewInfo()
    formatterViewInfo(viewInfo, { thousandSeparator: false })

    expect(viewInfo.customAttr.tooltip.tooltipFormatter.thousandSeparator).toBe(false)
    expect(
      viewInfo.customAttr.tooltip.seriesTooltipFormatter[0].formatterCfg.thousandSeparator
    ).toBe(false)
  })

  it('skips tooltip merge for excluded chart type table-info', () => {
    const viewInfo = createViewInfo()
    viewInfo.type = 'table-info'
    formatterViewInfo(viewInfo, { thousandSeparator: false })

    expect(viewInfo.customAttr.tooltip.tooltipFormatter.thousandSeparator).toBeUndefined()
  })

  it('merges value into customStyle axis formatters', () => {
    const viewInfo = createViewInfo()
    formatterViewInfo(viewInfo, { unit: 1000 })

    expect(viewInfo.customStyle.xAxis.axisLabelFormatter.unit).toBe(1000)
    expect(viewInfo.customStyle.yAxis.axisLabelFormatter.unit).toBe(1000)
    expect(viewInfo.customStyle.yAxisExt.axisLabelFormatter.unit).toBe(1000)
  })
})

describe('mergeTooltipFormat', () => {
  it('merges value into item formatterCfg for non-excluded type', () => {
    const item: Record<string, any> = { formatterCfg: { type: 'auto' } }
    mergeTooltipFormat(item, 'bar', { decimalCount: 3 })
    expect(item.formatterCfg.decimalCount).toBe(3)
  })

  it('skips merge for table-info', () => {
    const item: Record<string, any> = { formatterCfg: { type: 'auto' } }
    mergeTooltipFormat(item, 'table-info', { decimalCount: 3 })
    expect(item.formatterCfg.decimalCount).toBeUndefined()
  })

  it('skips merge for stock-line', () => {
    const item: Record<string, any> = { formatterCfg: { type: 'auto' } }
    mergeTooltipFormat(item, 'stock-line', { decimalCount: 3 })
    expect(item.formatterCfg.decimalCount).toBeUndefined()
  })

  it('skips merge for bullet-graph', () => {
    const item: Record<string, any> = { formatterCfg: { type: 'auto' } }
    mergeTooltipFormat(item, 'bullet-graph', { decimalCount: 3 })
    expect(item.formatterCfg.decimalCount).toBeUndefined()
  })
})

describe('calcNiceMinValue', () => {
  it('returns tmpOptions with yAxis.min set when data is valid', () => {
    const chart = { senior: JSON.stringify({ functionCfg: { sliderShow: false } }) }
    const options = { data: [{ value: 10 }, { value: 50 }, { value: 100 }] }
    const tmpOptions = { yAxis: { min: 0 } }

    const result = calcNiceMinValue(chart as any, options, tmpOptions)
    expect(result.yAxis.min).toBeDefined()
    expect(typeof result.yAxis.min).toBe('number')
    expect(result.yAxis.min).toBeLessThanOrEqual(10)
  })

  it('slices data based on slider range', () => {
    const chart = {
      senior: JSON.stringify({ functionCfg: { sliderShow: true, sliderRange: [0, 50] } })
    }
    const options = { data: [{ value: 10 }, { value: 20 }, { value: 90 }, { value: 100 }] }
    const tmpOptions = { yAxis: { min: 0 } }

    const result = calcNiceMinValue(chart as any, options, tmpOptions)
    expect(result.yAxis.min).toBeDefined()
  })

  it('returns tmpOptions unchanged when filtered values produce NaN', () => {
    const chart = { senior: JSON.stringify({ functionCfg: { sliderShow: false } }) }
    const options = { data: [] as any[] }
    const tmpOptions = { yAxis: { min: 0 } }

    const result = calcNiceMinValue(chart as any, options, tmpOptions)
    expect(result).toBe(tmpOptions)
  })

  it('preserves existing tmpOptions properties', () => {
    const chart = { senior: JSON.stringify({ functionCfg: { sliderShow: false } }) }
    const options = { data: [{ value: 10 }, { value: 50 }] }
    const tmpOptions = { yAxis: { min: 0 }, xAxis: { visible: true } }

    const result = calcNiceMinValue(chart as any, options, tmpOptions)
    expect(result.xAxis.visible).toBe(true)
    expect(result.yAxis).toBeDefined()
  })
})

describe('listenYAxisNiceMinEvents', () => {
  const createChart = () => ({
    customStyle: JSON.stringify({ yAxis: { axisValue: { auto: true } } })
  })

  it('registers handlers when yAxis is auto', () => {
    const newChart = { on: vi.fn() }
    listenYAxisNiceMinEvents(createChart() as any, newChart as any)

    expect(newChart.on).toHaveBeenCalledWith('legend-item-group:click', expect.any(Function))
    expect(newChart.on).toHaveBeenCalledWith('slider:valuechanged', expect.any(Function))
  })

  it('does not register handlers when yAxis is not auto', () => {
    const chart = { customStyle: JSON.stringify({ yAxis: { axisValue: { auto: false } } }) }
    const newChart = { on: vi.fn() }
    listenYAxisNiceMinEvents(chart as any, newChart as any)

    expect(newChart.on).not.toHaveBeenCalled()
  })

  it('legend click handler sets nice min on view scales and re-renders', () => {
    const onHandlers: Record<string, (...args: any[]) => void> = {}
    const newChart = {
      on: vi.fn((event: string, handler: (...args: any[]) => void) => {
        onHandlers[event] = handler
      })
    }

    listenYAxisNiceMinEvents(createChart() as any, newChart as any)

    const mockView = { options: { scales: { value: { min: 0 } } }, render: vi.fn() }
    onHandlers['legend-item-group:click']({
      view: { ...mockView, filteredData: [{ value: 10 }, { value: 50 }, { value: 100 }] }
    })

    expect(mockView.options.scales.value.min).toBeDefined()
    expect(mockView.render).toHaveBeenCalledWith(true)
  })

  it('slider handler sets nice min when max !== min', () => {
    const onHandlers: Record<string, (...args: any[]) => void> = {}
    const newChart = {
      on: vi.fn((event: string, handler: (...args: any[]) => void) => {
        onHandlers[event] = handler
      })
    }

    listenYAxisNiceMinEvents(createChart() as any, newChart as any)

    const sliderEvent = {
      view: {
        options: { scales: { value: { min: 0 } } },
        filteredData: [{ value: 10 }, { value: 50 }, { value: 100 }]
      }
    }
    onHandlers['slider:valuechanged'](sliderEvent)

    expect(typeof sliderEvent.view.options.scales.value.min).toBe('number')
  })

  it('slider handler skips update when max === min', () => {
    const onHandlers: Record<string, (...args: any[]) => void> = {}
    const newChart = {
      on: vi.fn((event: string, handler: (...args: any[]) => void) => {
        onHandlers[event] = handler
      })
    }

    listenYAxisNiceMinEvents(createChart() as any, newChart as any)

    const originalMin = 42
    const sliderEvent = {
      view: {
        options: { scales: { value: { min: originalMin } } },
        filteredData: [{ value: 5 }, { value: 5 }, { value: 5 }]
      }
    }
    onHandlers['slider:valuechanged'](sliderEvent)

    expect(sliderEvent.view.options.scales.value.min).toBe(originalMin)
  })
})
