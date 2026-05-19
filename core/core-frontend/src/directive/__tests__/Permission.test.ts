import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock the axios dependencies (imported transitively by store modules)
vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

// Mock the interactive store with lazy getter so module-level instantiation works
const { mockGetData } = vi.hoisted(() => ({
  mockGetData: vi.fn<() => Array<{ menuAuth?: boolean; anyManage?: boolean }>>()
}))
vi.mock('@/store/modules/interactive', () => ({
  interactiveStoreWithOut: () => ({
    get getData() {
      return mockGetData()
    }
  })
}))

// Import after mocks are set up
import { checkPermission } from '../Permission'

describe('checkPermission', () => {
  beforeEach(() => {
    mockGetData.mockReset()
  })

  it('should keep element when all required permissions have menuAuth and anyManage', () => {
    mockGetData.mockReturnValue([
      { menuAuth: true, anyManage: true },
      { menuAuth: true, anyManage: true },
      { menuAuth: true, anyManage: true },
      { menuAuth: true, anyManage: true }
    ])
    const removeChild = vi.fn()
    const el = { parentNode: { removeChild } }
    checkPermission(el, { value: ['panel'] })
    expect(removeChild).not.toHaveBeenCalled()
  })

  it('should remove element from DOM when permission lacks menuAuth or anyManage', () => {
    mockGetData.mockReturnValue([
      { menuAuth: true, anyManage: false }, // panel - missing anyManage
      { menuAuth: true, anyManage: true },
      { menuAuth: true, anyManage: true },
      { menuAuth: true, anyManage: true }
    ])
    const removeChild = vi.fn()
    const el = { parentNode: { removeChild } }
    checkPermission(el, { value: ['panel'] })
    expect(removeChild).toHaveBeenCalledWith(el)
  })

  it('should require ALL permissions to pass (every, not some)', () => {
    mockGetData.mockReturnValue([
      { menuAuth: true, anyManage: true }, // panel
      { menuAuth: true, anyManage: false }, // screen - fails
      { menuAuth: true, anyManage: true }, // dataset
      { menuAuth: true, anyManage: true } // datasource
    ])
    const removeChild = vi.fn()
    const el = { parentNode: { removeChild } }
    // Both panel and screen required; screen fails → element removed
    checkPermission(el, { value: ['panel', 'screen'] })
    expect(removeChild).toHaveBeenCalledWith(el)
  })

  it('should throw Error when value is not an array', () => {
    mockGetData.mockReturnValue([{}, {}, {}, {}])
    const el = { parentNode: { removeChild: vi.fn() } }
    expect(() => checkPermission(el, { value: 'panel' })).toThrow(
      Error(`使用方式： v-permission="['panel']"`)
    )
  })

  it('should throw Error when value is undefined', () => {
    mockGetData.mockReturnValue([{}, {}, {}, {}])
    const el = { parentNode: { removeChild: vi.fn() } }
    expect(() => checkPermission(el, { value: undefined })).toThrow(
      Error(`使用方式： v-permission="['panel']"`)
    )
  })

  it('should map permission flags to correct array indices: panel(0), screen(1), dataset(2), datasource(3)', () => {
    mockGetData.mockReturnValue([
      { menuAuth: false, anyManage: false }, // panel(0)
      { menuAuth: false, anyManage: false }, // screen(1)
      { menuAuth: true, anyManage: true }, // dataset(2)
      { menuAuth: false, anyManage: false } // datasource(3)
    ])
    const removeChild = vi.fn()
    const el = { parentNode: { removeChild } }
    // Only dataset has permission
    checkPermission(el, { value: ['dataset'] })
    expect(removeChild).not.toHaveBeenCalled()

    // But panel should fail
    removeChild.mockClear()
    checkPermission(el, { value: ['panel'] })
    expect(removeChild).toHaveBeenCalledWith(el)
  })

  it('should not remove element if parentNode is null', () => {
    mockGetData.mockReturnValue([
      { menuAuth: false, anyManage: false },
      { menuAuth: true, anyManage: true },
      { menuAuth: true, anyManage: true },
      { menuAuth: true, anyManage: true }
    ])
    const el = { parentNode: null }
    // Should not throw even though permission fails
    expect(() => checkPermission(el, { value: ['panel'] })).not.toThrow()
  })
})
