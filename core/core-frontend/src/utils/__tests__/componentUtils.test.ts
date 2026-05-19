import { beforeEach, describe, expect, it, vi } from 'vitest'

const { enumValueObjMock } = vi.hoisted(() => ({
  enumValueObjMock: vi.fn()
}))

vi.mock('@/api/dataset', () => ({
  enumValueObj: enumValueObjMock
}))

import {
  filterEnumMapSync,
  filterEnumParams,
  filterEnumParamsReduce,
  filterParamsOptions
} from '../componentUtils'

describe('componentUtils', () => {
  beforeEach(() => {
    enumValueObjMock.mockReset()
  })

  it('builds enum maps only for VQuery fields that pull option values remotely', async () => {
    enumValueObjMock.mockResolvedValue([
      { fieldKey: 'ID-1', label: '显示一' },
      { fieldKey: 'ID-2', label: '显示二' }
    ])

    await filterEnumMapSync([
      {
        component: 'VQuery',
        propValue: [
          { optionValueSource: 1, field: { id: 'fieldKey' }, displayId: 'label' },
          { optionValueSource: 0, field: { id: 'ignoredField' }, displayId: 'label' },
          { optionValueSource: 1, field: { id: '' }, displayId: 'label' }
        ]
      },
      { component: 'Text', propValue: [] }
    ])

    expect(enumValueObjMock).toHaveBeenCalledTimes(1)
    expect(enumValueObjMock).toHaveBeenCalledWith({
      queryId: 'fieldKey',
      displayId: 'label',
      searchText: ''
    })
    expect(filterEnumParams(['显示一', '未知值'], 'fieldKey')).toEqual(['ID-1', '未知值'])
  })

  it('reduces stored enum maps back to display values when needed', async () => {
    enumValueObjMock.mockResolvedValue([
      { cityId: 'hangzhou', cityName: '杭州' },
      { cityId: 'shanghai', cityName: '上海' }
    ])

    await filterEnumMapSync([
      {
        component: 'VQuery',
        propValue: [{ optionValueSource: 1, field: { id: 'cityId' }, displayId: 'cityName' }]
      }
    ])

    expect(filterEnumParamsReduce(['hangzhou', 'missing'], 'cityId')).toEqual(['杭州', 'missing'])
  })

  it('clears previously cached enum maps when syncing unrelated component data', async () => {
    enumValueObjMock.mockResolvedValue([{ deptId: 'd-1', deptName: '销售' }])

    await filterEnumMapSync([
      {
        component: 'VQuery',
        propValue: [{ optionValueSource: 1, field: { id: 'deptId' }, displayId: 'deptName' }]
      }
    ])
    await filterEnumMapSync([{ component: 'UserView', propValue: [] }])

    expect(filterEnumParams(['销售'], 'deptId')).toEqual(['销售'])
    expect(filterEnumParamsReduce(['d-1'], 'deptId')).toEqual(['d-1'])
  })

  it('returns null when params or options are empty', () => {
    expect(filterParamsOptions([], ['a'])).toBeNull()
    expect(filterParamsOptions(['a'], [])).toBeNull()
    expect(filterParamsOptions(null, ['a'])).toBeNull()
  })

  it('keeps hierarchical options when a parent or child path matches', () => {
    const options = ['香橙店-de-浓郁椰奶', '苹果店', '总店-de-一号分店']

    expect(filterParamsOptions('香橙店', options)).toBe('香橙店')
    expect(filterParamsOptions('香橙店-de-浓郁椰奶-de-大杯', options)).toBe(
      '香橙店-de-浓郁椰奶-de-大杯'
    )
    expect(filterParamsOptions(['苹果店', '不存在', 123 as never], options)).toEqual(['苹果店'])
    expect(filterParamsOptions(['无效值'], options)).toBeNull()
  })
})
