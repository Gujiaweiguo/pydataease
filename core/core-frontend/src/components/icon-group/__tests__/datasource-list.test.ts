import { describe, it, expect, vi } from 'vitest'

vi.mock('@/assets/svg/mysql-ds.svg', () => ({ default: 'mysql-ds.svg' }))
vi.mock('@/assets/svg/pg-ds.svg', () => ({ default: 'pg-ds.svg' }))
vi.mock('@/assets/svg/icon_excel.svg', () => ({ default: 'icon_excel.svg' }))

import * as mod from '../datasource-list'

describe('datasource-list', () => {
  it('exports iconDatasourceMap', () => {
    expect(mod.iconDatasourceMap).toBeDefined()
    expect(typeof mod.iconDatasourceMap).toBe('object')
  })

  it('contains expected datasource type keys', () => {
    expect(mod.iconDatasourceMap).toHaveProperty('Excel')
    expect(mod.iconDatasourceMap).toHaveProperty('ExcelRemote')
    expect(mod.iconDatasourceMap).toHaveProperty('mysql')
    expect(mod.iconDatasourceMap).toHaveProperty('pg')
  })

  it('has exactly 4 entries', () => {
    expect(Object.keys(mod.iconDatasourceMap)).toHaveLength(4)
  })

  it('Excel and ExcelRemote share the same icon', () => {
    expect(mod.iconDatasourceMap.Excel).toBe(mod.iconDatasourceMap.ExcelRemote)
  })

  it('each entry maps to a string value', () => {
    Object.values(mod.iconDatasourceMap).forEach(val => {
      expect(typeof val).toBe('string')
    })
  })
})
