import { describe, expect, it } from 'vitest'
import {
  hasCreatePermission,
  hasTemplateCreatePermission,
  getInteractiveIndex,
  getVisualizationRoute,
  isScreenTemplateType,
  isDashboardLike,
  isScreenLike,
  matchesTemplateType,
  normalizeCanvasType,
  normalizePermissionType,
  normalizeShortcutRow,
  toStoreResourceType
} from '../visualizationResource'

describe('visualizationResource', () => {
  it('normalizes visualization aliases to canonical canvas types', () => {
    expect(normalizeCanvasType('panel')).toBe('dashboard')
    expect(normalizeCanvasType('dashboard')).toBe('dashboard')
    expect(normalizeCanvasType('screen')).toBe('dataV')
    expect(normalizeCanvasType('dataV')).toBe('dataV')
    expect(normalizeCanvasType('SCREEN')).toBe('dataV')
  })

  it('normalizes permission aliases for directives and store actions', () => {
    expect(normalizePermissionType('dashboard')).toBe('panel')
    expect(normalizePermissionType('panel')).toBe('panel')
    expect(normalizePermissionType('dataV')).toBe('screen')
    expect(normalizePermissionType('screen')).toBe('screen')
  })

  it('maps canonical visualization routes and interactive indices', () => {
    expect(getVisualizationRoute('dashboard')).toBe('/panel/index')
    expect(getVisualizationRoute('panel')).toBe('/panel/index')
    expect(getVisualizationRoute('dataV')).toBe('/screen/index')
    expect(getVisualizationRoute('screen')).toBe('/screen/index')
    expect(getInteractiveIndex('panel')).toBe(0)
    expect(getInteractiveIndex('screen')).toBe(1)
  })

  it('normalizes shortcut rows from mixed snake_case and old type aliases', () => {
    const row = normalizeShortcutRow({
      id: 9,
      type: 'screen',
      resource_id: 7,
      auto_pwd: true,
      ticket_require: false,
      create_by: 'alice',
      update_by: 'bob',
      update_time: 123,
      extra_flag: 1,
      extra_flag1: 0,
      storeFlag: true
    })

    expect(row.type).toBe('dataV')
    expect(row.resourceId).toBe(7)
    expect(row.autoPwd).toBe(true)
    expect(row.ticketRequire).toBe(false)
    expect(row.creator).toBe('alice')
    expect(row.lastEditor).toBe('bob')
    expect(row.lastEditTime).toBe(123)
    expect(row.extFlag).toBe(1)
    expect(row.extFlag1).toBe(0)
    expect(row.favorite).toBe(true)
  })

  it('converts visualization types to store resource types', () => {
    expect(toStoreResourceType('dashboard')).toBe('panel')
    expect(toStoreResourceType('panel')).toBe('panel')
    expect(toStoreResourceType('dataV')).toBe('screen')
    expect(toStoreResourceType('screen')).toBe('screen')
    expect(isDashboardLike('panel')).toBe(true)
    expect(isScreenLike('screen')).toBe(true)
  })

  it('derives create permission from menuAuth and rootManage', () => {
    expect(hasCreatePermission({ menuAuth: true, rootManage: true, anyManage: false })).toBe(true)
    expect(hasCreatePermission({ menuAuth: true, rootManage: false, anyManage: true })).toBe(false)
    expect(hasCreatePermission({ menuAuth: false, rootManage: true })).toBe(false)
  })

  it('matches template create auth for alias template types', () => {
    const createAuth = { PANEL: true, SCREEN: false }
    expect(hasTemplateCreatePermission(createAuth, 'dashboard')).toBe(true)
    expect(hasTemplateCreatePermission(createAuth, 'PANEL')).toBe(true)
    expect(hasTemplateCreatePermission(createAuth, 'dataV')).toBe(false)
    expect(hasTemplateCreatePermission(createAuth, 'SCREEN')).toBe(false)
  })

  it('matches template tab types across canonical and legacy aliases', () => {
    expect(matchesTemplateType('PANEL', 'dashboard')).toBe(true)
    expect(matchesTemplateType('SCREEN', 'dataV')).toBe(true)
    expect(matchesTemplateType('SCREEN', 'SCREEN')).toBe(true)
    expect(matchesTemplateType('PANEL', 'dataV')).toBe(false)
    expect(matchesTemplateType('all', 'dashboard')).toBe(true)
  })

  it('identifies screen template types through normalized aliases', () => {
    expect(isScreenTemplateType('SCREEN')).toBe(true)
    expect(isScreenTemplateType('dataV')).toBe(true)
    expect(isScreenTemplateType('dashboard')).toBe(false)
  })
})
