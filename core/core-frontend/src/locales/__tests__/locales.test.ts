import { describe, it, expect } from 'vitest'
import en from '../en'
import zhCN from '../zh-CN'
import tw from '../tw'

function collectKeys(obj: Record<string, any>, prefix = ''): string[] {
  const keys: string[] = []
  for (const key of Object.keys(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key
    if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
      keys.push(...collectKeys(obj[key], fullKey))
    } else {
      keys.push(fullKey)
    }
  }
  return keys
}

describe('Locales', () => {
  it('all three locale files export default objects', () => {
    expect(en).toBeDefined()
    expect(typeof en).toBe('object')
    expect(zhCN).toBeDefined()
    expect(typeof zhCN).toBe('object')
    expect(tw).toBeDefined()
    expect(typeof tw).toBe('object')
  })

  it('all locales have large key sets (4500+ keys)', () => {
    const enKeys = collectKeys(en as Record<string, any>)
    const zhCNKeys = collectKeys(zhCN as Record<string, any>)
    const twKeys = collectKeys(tw as Record<string, any>)
    expect(enKeys.length).toBeGreaterThan(4500)
    expect(zhCNKeys.length).toBeGreaterThan(4500)
    expect(twKeys.length).toBeGreaterThan(4500)
  })

  it('key counts are within 1% of each other', () => {
    const enKeys = collectKeys(en as Record<string, any>)
    const zhCNKeys = collectKeys(zhCN as Record<string, any>)
    const twKeys = collectKeys(tw as Record<string, any>)
    const maxDiff = Math.max(enKeys.length, zhCNKeys.length, twKeys.length) * 0.01
    expect(Math.abs(enKeys.length - zhCNKeys.length)).toBeLessThanOrEqual(maxDiff)
    expect(Math.abs(enKeys.length - twKeys.length)).toBeLessThanOrEqual(maxDiff)
    expect(Math.abs(zhCNKeys.length - twKeys.length)).toBeLessThanOrEqual(maxDiff)
  })

  it('common key exists in all locales', () => {
    expect(en).toHaveProperty('common')
    expect(zhCN).toHaveProperty('common')
    expect(tw).toHaveProperty('common')
  })

  it('common.component sub-object exists in all locales', () => {
    expect(en.common).toHaveProperty('component')
    expect(zhCN.common).toHaveProperty('component')
    expect(tw.common).toHaveProperty('component')
  })

  it('chart key exists in all locales', () => {
    expect(en).toHaveProperty('chart')
    expect(zhCN).toHaveProperty('chart')
    expect(tw).toHaveProperty('chart')
  })

  it('visualization key exists in all locales', () => {
    expect(en).toHaveProperty('visualization')
    expect(zhCN).toHaveProperty('visualization')
    expect(tw).toHaveProperty('visualization')
  })

  it('no locale values are undefined', () => {
    const enKeys = collectKeys(en as Record<string, any>)
    for (const key of enKeys) {
      const parts = key.split('.')
      let val: any = en
      for (const part of parts) {
        val = val[part]
      }
      expect(val).not.toBeUndefined()
    }
  })
})
