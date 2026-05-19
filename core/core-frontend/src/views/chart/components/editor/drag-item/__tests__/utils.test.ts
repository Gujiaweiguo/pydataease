import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const { getCSSVariableMock } = vi.hoisted(() => ({
  getCSSVariableMock: vi.fn()
}))

vi.mock('@/utils/color', () => ({
  getCSSVariable: getCSSVariableMock
}))

import { getItemType, getOriginFieldName, resetValueFormatter } from '../utils'

describe('drag-item utils', () => {
  beforeEach(() => {
    getCSSVariableMock.mockReturnValue('#3370FF')
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('returns the css variable color in template mode with no dimensions or quotas', () => {
    expect(getItemType([], [], { groupType: 'd' })).toBe('#3370FF')
    expect(getCSSVariableMock).toHaveBeenCalledTimes(1)
  })

  it('returns the css variable color for a matching dimension item without chartId', () => {
    const item = { id: 1, originName: 'city', deType: 2, groupType: 'd' }

    expect(getItemType([item], [], item)).toBe('#3370FF')
  })

  it('matches chart fields by originName, dataeaseName, type, and groupType when chartId exists', () => {
    const item = {
      id: 99,
      chartId: 'chart-1',
      originName: 'province',
      dataeaseName: 'province_alias',
      deType: 1,
      groupType: 'd'
    }

    const dimension = {
      id: 1,
      originName: 'province',
      dataeaseName: 'province_alias',
      deType: 1,
      groupType: 'd'
    }

    expect(getItemType([dimension], [], item)).toBe('#3370FF')
  })

  it('returns an error color for a mismatched dimension item', () => {
    const item = { id: 1, originName: 'city', deType: 2, groupType: 'd' }

    expect(getItemType([{ ...item, deType: 3 }], [], item)).toBe('#F54A45')
  })

  it('returns the quota success color for a matching quota item', () => {
    const item = { id: 2, originName: 'amount', deType: 1, groupType: 'q' }

    expect(getItemType([], [item], item)).toBe('#04b49c')
  })

  it('returns an error color for a mismatched quota item', () => {
    const item = { id: 2, originName: 'amount', deType: 1, groupType: 'q' }

    expect(getItemType([], [{ ...item, originName: 'profit' }], item)).toBe('#F54A45')
  })

  it('finds the origin field name from the dimension list', () => {
    expect(
      getOriginFieldName([{ id: 1, name: 'Region' }], [{ id: 2, name: 'Sales' }], { id: 1 })
    ).toBe('Region')
  })

  it('prefers a later quota match when both lists contain the same field id', () => {
    expect(
      getOriginFieldName([{ id: 1, name: 'Region' }], [{ id: 1, name: 'Quota Region' }], { id: 1 })
    ).toBe('Quota Region')
  })

  it('returns an empty string when getOriginFieldName finds no match', () => {
    expect(getOriginFieldName([{ id: 1, name: 'Region' }], [{ id: 2, name: 'Sales' }], { id: 3 })).toBe(
      ''
    )
  })

  it('resets formatter configuration to the default values', () => {
    const item = {
      formatterCfg: {
        type: 'percent',
        unit: 100,
        suffix: '%',
        decimalCount: 0,
        thousandSeparator: false
      }
    }

    resetValueFormatter(item)

    expect(item.formatterCfg).toEqual({
      type: 'auto',
      unit: 1,
      suffix: '',
      decimalCount: 2,
      thousandSeparator: true
    })
  })

  it('does nothing when resetValueFormatter receives an empty item', () => {
    expect(resetValueFormatter(undefined)).toBeUndefined()
  })
})
