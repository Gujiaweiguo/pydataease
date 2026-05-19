import { describe, expect, expectTypeOf, it } from 'vitest'

import type { SettingRecord, ToolTipRecord } from '../SettingTemplate'

describe('SettingTemplate types', () => {
  it('creates a valid SettingRecord object with all required fields', () => {
    const record: SettingRecord = {
      pkey: 'site_name',
      pval: 'DataEase',
      type: 'string',
      sort: 1
    }

    expect(record.pkey).toBe('site_name')
    expect(record.sort).toBe(1)
    expectTypeOf(record).toMatchTypeOf<SettingRecord>()
  })

  it('supports SettingRecord collections and numeric sorting fields', () => {
    const records: SettingRecord[] = [
      { pkey: 'b', pval: '2', type: 'string', sort: 2 },
      { pkey: 'a', pval: '1', type: 'string', sort: 1 }
    ]

    expect(records.map(record => record.sort)).toEqual([2, 1])
  })

  it('creates a valid ToolTipRecord object', () => {
    const tooltip: ToolTipRecord = {
      key: 'username',
      val: 'Shown on the profile page'
    }

    expect(tooltip.key).toBe('username')
    expect(tooltip.val).toContain('profile')
    expectTypeOf(tooltip).toMatchTypeOf<ToolTipRecord>()
  })

  it('supports indexing ToolTipRecord values by key', () => {
    const tooltips: ToolTipRecord[] = [
      { key: 'username', val: 'Shown on the profile page' },
      { key: 'email', val: 'Used for notifications' }
    ]

    const tooltipMap = Object.fromEntries(tooltips.map(item => [item.key, item.val]))

    expect(tooltipMap.email).toBe('Used for notifications')
  })
})
