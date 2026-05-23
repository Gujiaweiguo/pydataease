import { describe, expect, it } from 'vitest'

import { applyCalculatedPreviewFields } from '../previewCalculatedFields'

describe('applyCalculatedPreviewFields', () => {
  it('appends calculated metric fields and computes values', () => {
    const previewFields = [
      {
        id: '1',
        dataeaseName: '营业收入',
        name: '营业收入',
        originName: '营业收入',
        deType: 3,
        type: 'DOUBLE',
        extField: 0
      },
      {
        id: '2',
        dataeaseName: '毛利润',
        name: '毛利润',
        originName: '毛利润',
        deType: 3,
        type: 'DOUBLE',
        extField: 0
      }
    ]
    const previewRows = [{ 营业收入: 100, 毛利润: 20 }]
    const allFields = [
      ...previewFields,
      {
        id: '3',
        dataeaseName: null,
        fieldShortName: null,
        name: '毛利率',
        originName: '([1]-[2])/[2]',
        deType: 3,
        type: 'VARCHAR',
        extField: 2,
        checked: true,
        params: []
      }
    ]

    const result = applyCalculatedPreviewFields(previewFields, previewRows, allFields)

    expect(result.fields.map(field => field.name)).toEqual(['营业收入', '毛利润', '毛利率'])
    expect(result.rows[0].毛利率).toBe(4)
  })

  it('supports copied fields that reference a single source field', () => {
    const previewFields = [
      {
        id: '1',
        dataeaseName: '客户名称',
        name: '客户名称',
        originName: '客户名称',
        deType: 0,
        type: 'TEXT',
        extField: 0
      }
    ]
    const previewRows = [{ 客户名称: '邱升' }]
    const allFields = [
      ...previewFields,
      {
        id: '2',
        name: '客户名称副本',
        originName: '[1]',
        deType: 0,
        type: 'TEXT',
        extField: 2,
        checked: true,
        params: []
      }
    ]

    const result = applyCalculatedPreviewFields(previewFields, previewRows, allFields)

    expect(result.fields.map(field => field.name)).toEqual(['客户名称', '客户名称副本'])
    expect(result.rows[0].客户名称副本).toBe('邱升')
  })

  it('trims whitespace inside formula references', () => {
    const previewFields = [
      {
        id: '1',
        dataeaseName: '营业收入',
        name: '营业收入',
        originName: '营业收入',
        deType: 3,
        type: 'DOUBLE',
        extField: 0
      },
      {
        id: '2',
        dataeaseName: '毛利润',
        name: '毛利润',
        originName: '毛利润',
        deType: 3,
        type: 'DOUBLE',
        extField: 0
      }
    ]
    const previewRows = [{ 营业收入: 23268, 毛利润: 11172 }]
    const allFields = [
      ...previewFields,
      {
        id: '3',
        name: '毛利率',
        originName: ' [1]/[2]',
        deType: 3,
        type: 'VARCHAR',
        extField: 2,
        checked: true,
        params: []
      }
    ]

    const result = applyCalculatedPreviewFields(previewFields, previewRows, allFields)

    expect(result.rows[0].毛利率).toBeCloseTo(23268 / 11172)
  })

  it('falls back when formula references stale original field ids but columns still match by order', () => {
    const previewFields = [
      {
        id: 'new-income',
        dataeaseName: '营业收入',
        name: '营业收入',
        originName: '营业收入',
        deType: 3,
        type: 'DOUBLE',
        extField: 0,
        columnIndex: 15
      },
      {
        id: 'new-profit',
        dataeaseName: '毛利润',
        name: '毛利润',
        originName: '毛利润',
        deType: 3,
        type: 'DOUBLE',
        extField: 0,
        columnIndex: 16
      }
    ]
    const previewRows = [{ 营业收入: 23268, 毛利润: 11172 }]
    const allFields = [
      ...previewFields,
      {
        id: 'calc-1',
        name: '毛利率',
        originName: '[1779531984063289604]/[1779531984061021132]',
        deType: 3,
        type: 'VARCHAR',
        extField: 2,
        checked: true,
        params: []
      }
    ]

    const result = applyCalculatedPreviewFields(previewFields, previewRows, allFields)

    expect(result.rows[0].毛利率).toBeCloseTo(23268 / 11172)
  })
})
