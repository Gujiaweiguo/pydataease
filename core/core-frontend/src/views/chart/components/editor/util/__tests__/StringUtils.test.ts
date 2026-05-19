import { afterEach, describe, expect, it, vi } from 'vitest'

import {
  equalsAny,
  includesAny,
  pdfTemplateReplaceAll,
  randomRange,
  replaceInlineI18n
} from '../StringUtils'

describe('StringUtils', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('replaces every matching template token across multiple lines', () => {
    const content = 'Hello $panelName$\n$panelName$ dashboard\n$other$'

    expect(pdfTemplateReplaceAll(content, 'panelName', 'Sales')).toBe(
      'Hello Sales\nSales dashboard\n$other$'
    )
  })

  it('returns a fixed-length random string when max is omitted', () => {
    vi.spyOn(Math, 'random').mockReturnValue(0)

    expect(randomRange(3, undefined)).toBe('AAA')
  })

  it('uses the computed upper bound when min and max are provided', () => {
    vi.spyOn(Math, 'random').mockReturnValueOnce(0.99).mockReturnValue(0)

    expect(randomRange(3, 5)).toBe('AAAAA')
  })

  it('checks strict equality against any candidate source', () => {
    expect(equalsAny('2', 1, '2', 3)).toBe(true)
    expect(equalsAny(2, '2', 3)).toBe(false)
  })

  it('returns false when equalsAny receives no match candidates', () => {
    expect(equalsAny('target')).toBe(false)
  })

  it('returns true when includesAny finds at least one substring', () => {
    expect(includesAny('sales-dashboard', 'profit', 'dash')).toBe(true)
  })

  it('returns false when includesAny target is empty or nothing matches', () => {
    expect(includesAny('', 'dash')).toBe(false)
    expect(includesAny('sales-dashboard', 'profit', 'cost')).toBe(false)
  })

  it('replaces inline i18n tokens with their raw keys', () => {
    expect(replaceInlineI18n("Title: $t('chart.title'), axis: $t('chart.axis')")).toBe(
      'Title: chart.title, axis: chart.axis'
    )
  })

  it('replaces repeated inline i18n tokens everywhere they appear', () => {
    expect(replaceInlineI18n("$t('chart.title') / $t('chart.title')")).toBe(
      'chart.title / chart.title'
    )
  })

  it('returns an empty array when replaceInlineI18n receives a falsy value', () => {
    expect(replaceInlineI18n('')).toEqual([])
    expect(replaceInlineI18n(null)).toEqual([])
  })
})
