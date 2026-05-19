import { beforeEach, describe, expect, it, vi } from 'vitest'

const { loadScriptMock, setTitleMock, warningMock, wsCacheDeleteMock, wsCacheGetMock } = vi.hoisted(
  () => ({
    loadScriptMock: vi.fn(),
    setTitleMock: vi.fn(),
    warningMock: vi.fn(),
    wsCacheDeleteMock: vi.fn(),
    wsCacheGetMock: vi.fn()
  })
)

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: {
      delete: wsCacheDeleteMock,
      get: wsCacheGetMock
    }
  })
}))

vi.mock('@/utils/RemoteJs', () => ({
  loadScript: loadScriptMock
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: {
    warning: warningMock
  }
}))

vi.mock('dingtalk-jsapi', () => ({
  biz: {
    navigation: {
      setTitle: setTitleMock
    }
  },
  ready: vi.fn(callback => callback())
}))

import {
  checkAddHttp,
  deepCopy,
  exportPermission,
  formatExt,
  getActiveCategories,
  isNull,
  isPreventDrop,
  swap
} from '../utils'

describe('utils', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('deep copies nested objects without preserving references', () => {
    const original = { a: 1, b: { c: 2 } }
    const copied = deepCopy(original)

    expect(copied).toEqual(original)
    expect(copied).not.toBe(original)
    expect(copied.b).not.toBe(original.b)

    copied.b.c = 3
    expect(original.b.c).toBe(2)
  })

  it('deep copies arrays and nested array members', () => {
    const original = [1, { value: 2 }, [3]]
    const copied = deepCopy(original)

    expect(copied).toEqual(original)
    expect(copied).not.toBe(original)
    expect(copied[1]).not.toBe(original[1])
    expect(copied[2]).not.toBe(original[2])
  })

  it('returns null unchanged from deepCopy', () => {
    expect(deepCopy(null)).toBeNull()
  })

  it('returns undefined unchanged from deepCopy', () => {
    expect(deepCopy(undefined)).toBeUndefined()
  })

  it('preserves nested Date values as distinct Date instances', () => {
    const createdAt = new Date('2024-01-01T00:00:00.000Z')
    const copied = deepCopy({ createdAt })

    expect(copied.createdAt).toEqual(createdAt)
    expect(copied.createdAt).toBeInstanceOf(Date)
    expect(copied.createdAt).not.toBe(createdAt)
  })

  it('swaps array elements in place', () => {
    const target = [1, 2, 3]

    swap(target, 0, 2)

    expect(target).toEqual([3, 2, 1])
  })

  it.each([
    ['VText', false],
    ['RectShape', false],
    ['CircleShape', false],
    ['SVGStar', false],
    ['UserView', true]
  ])('isPreventDrop(%s) returns %s', (component, expected) => {
    expect(isPreventDrop(component)).toBe(expected)
  })

  it.each([
    ['example.com', 'http://example.com'],
    ['https://example.com', 'https://example.com'],
    ['HTTP://EXAMPLE.COM', 'HTTP://EXAMPLE.COM'],
    [null, null]
  ])('checkAddHttp(%s) returns %s', (value, expected) => {
    expect(checkAddHttp(value)).toBe(expected)
  })

  it.each([
    [undefined, true],
    [null, true],
    ['null', true],
    ['', false],
    ['hello', false]
  ])('isNull(%s) returns %s', (value, expected) => {
    expect(isNull(value)).toBe(expected)
  })

  it('returns no export permissions for weight 1', () => {
    expect(exportPermission(1, 0)).toEqual([0, 0, 0])
  })

  it('returns full export permissions for weight 9', () => {
    expect(exportPermission(9, 0)).toEqual([1, 1, 1])
  })

  it('maps ext digits into export permission slots for other weights', () => {
    expect(exportPermission(2, 321)).toEqual([1, 2, 3])
    expect(exportPermission(2, 0)).toEqual([0, 0, 0])
  })

  it('formats ext values by reversing their digits', () => {
    expect(formatExt(321)).toEqual([1, 2, 3])
    expect(formatExt(100)).toEqual([0, 0, 1])
  })

  it('returns null when formatExt receives a falsy number', () => {
    expect(formatExt(0)).toBeNull()
  })

  it('returns only 最近使用 when no active categories are provided', () => {
    expect(Array.from(getActiveCategories(null))).toEqual(['最近使用'])
  })

  it('collects categories only from visible items and deduplicates them via Set', () => {
    const categories = getActiveCategories([
      {
        showFlag: true,
        categories: [{ name: '销售' }, { name: '地区' }]
      },
      {
        showFlag: false,
        categories: [{ name: '隐藏分类' }]
      },
      {
        showFlag: true,
        categories: [{ name: '销售' }, { name: '利润' }]
      }
    ])

    expect(Array.from(categories)).toEqual(['最近使用', '销售', '地区', '利润'])
  })
})
