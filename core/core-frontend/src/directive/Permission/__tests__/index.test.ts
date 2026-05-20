import { describe, it, expect, vi, beforeEach } from 'vitest'

const mockGetData = vi.fn(() => [
  { menuAuth: true, anyManage: true },
  { menuAuth: true, anyManage: true },
  { menuAuth: true, anyManage: true },
  { menuAuth: true, anyManage: true }
])

vi.mock('@/store/modules/interactive', () => ({
  interactiveStoreWithOut: () => ({
    get getData() {
      return mockGetData()
    }
  })
}))

import { checkPermission } from '../index'

describe('checkPermission directive', () => {
  let mockEl: any

  beforeEach(() => {
    mockEl = {
      parentNode: {
        removeChild: vi.fn()
      }
    }
    vi.clearAllMocks()
  })

  it('should throw error if value is not an array', () => {
    expect(() => {
      checkPermission(mockEl, { value: 'not-array' })
    }).toThrow('使用方式： v-permission="[\'panel\']"')
  })

  it('should throw error if value is undefined', () => {
    expect(() => {
      checkPermission(mockEl, { value: undefined })
    }).toThrow()
  })

  it('should not remove element when all permissions are satisfied', () => {
    checkPermission(mockEl, { value: ['panel'] })
    expect(mockEl.parentNode.removeChild).not.toHaveBeenCalled()
  })

  it('should remove element when permission is not satisfied', () => {
    mockGetData.mockReturnValue([
      { menuAuth: false, anyManage: false },
      { menuAuth: false, anyManage: false },
      { menuAuth: false, anyManage: false },
      { menuAuth: false, anyManage: false }
    ])
    checkPermission(mockEl, { value: ['panel'] })
    expect(mockEl.parentNode.removeChild).toHaveBeenCalled()
  })

  it('should check all permissions in array (every, not some)', () => {
    mockGetData.mockReturnValue([
      { menuAuth: true, anyManage: true },
      { menuAuth: false, anyManage: false },
      { menuAuth: true, anyManage: true },
      { menuAuth: true, anyManage: true }
    ])
    checkPermission(mockEl, { value: ['panel', 'screen'] })
    expect(mockEl.parentNode.removeChild).toHaveBeenCalled()
  })

  it('should not throw when element has no parentNode', () => {
    mockEl.parentNode = null
    mockGetData.mockReturnValue([
      { menuAuth: false, anyManage: false },
      { menuAuth: false, anyManage: false },
      { menuAuth: false, anyManage: false },
      { menuAuth: false, anyManage: false }
    ])
    expect(() => {
      checkPermission(mockEl, { value: ['panel'] })
    }).not.toThrow()
  })
})
