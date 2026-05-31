import { describe, it, expect, vi, beforeEach } from 'vitest'

const fullCapabilities = {
  canView: true,
  canUse: true,
  canExport: true,
  canManage: true,
  canAuthorize: false
}

const emptyCapabilities = {
  canView: false,
  canUse: false,
  canExport: false,
  canManage: false,
  canAuthorize: false
}

const buildPermission = (overrides?: {
  menuAuth?: boolean
  anyManage?: boolean
  capabilities?: Partial<typeof fullCapabilities>
}) => {
  const { capabilities, ...rest } = overrides || {}
  return {
    menuAuth: true,
    anyManage: true,
    ...rest,
    capabilities: {
      ...fullCapabilities,
      ...capabilities
    }
  }
}

const createBinding = (value?: unknown) => ({ value })

const mockGetData = vi.fn(() => [
  buildPermission(),
  buildPermission(),
  buildPermission(),
  buildPermission()
])

vi.mock('@/store/modules/interactive', () => ({
  interactiveStoreWithOut: () => ({
    get getData() {
      return mockGetData()
    },
    getResourceCapabilities(resourceType?: string | null) {
      const resourceTypeToIndex: Record<string, number> = {
        panel: 0,
        screen: 1,
        dataset: 2,
        datasource: 3
      }
      const data = mockGetData()
      const index = resourceType ? resourceTypeToIndex[resourceType] : -1
      return data[index]?.capabilities || {}
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
      checkPermission(mockEl, createBinding('not-array'))
    }).toThrow('使用方式： v-permission="[\'panel\']"')
  })

  it('should throw error if value is undefined', () => {
    expect(() => {
      checkPermission(mockEl, createBinding(undefined))
    }).toThrow()
  })

  it('should not remove element when all permissions are satisfied', () => {
    checkPermission(mockEl, createBinding(['panel']))
    expect(mockEl.parentNode.removeChild).not.toHaveBeenCalled()
  })

  it('should allow capability-based permission checks', () => {
    checkPermission(mockEl, createBinding(['dataset:export']))
    expect(mockEl.parentNode.removeChild).not.toHaveBeenCalled()
  })

  it('should remove element when capability is missing', () => {
    mockGetData.mockReturnValue([
      buildPermission(),
      buildPermission(),
      buildPermission({
        anyManage: false,
        capabilities: { canExport: false, canManage: false }
      }),
      buildPermission()
    ])
    checkPermission(mockEl, createBinding(['dataset:export']))
    expect(mockEl.parentNode.removeChild).toHaveBeenCalled()
  })

  it('should remove element when permission is not satisfied', () => {
    mockGetData.mockReturnValue([
      buildPermission({ menuAuth: false, anyManage: false, capabilities: emptyCapabilities }),
      buildPermission({ menuAuth: false, anyManage: false, capabilities: emptyCapabilities }),
      buildPermission({ menuAuth: false, anyManage: false, capabilities: emptyCapabilities }),
      buildPermission({ menuAuth: false, anyManage: false, capabilities: emptyCapabilities })
    ])
    checkPermission(mockEl, createBinding(['panel']))
    expect(mockEl.parentNode.removeChild).toHaveBeenCalled()
  })

  it('should check all permissions in array (every, not some)', () => {
    mockGetData.mockReturnValue([
      buildPermission(),
      buildPermission({ menuAuth: false, anyManage: false, capabilities: emptyCapabilities }),
      buildPermission(),
      buildPermission()
    ])
    checkPermission(mockEl, createBinding(['panel', 'screen']))
    expect(mockEl.parentNode.removeChild).toHaveBeenCalled()
  })

  it('should accept dashboard and dataV aliases in permission bindings', () => {
    mockGetData.mockReturnValue([
      buildPermission(),
      buildPermission(),
      buildPermission({ menuAuth: false, anyManage: false, capabilities: emptyCapabilities }),
      buildPermission({ menuAuth: false, anyManage: false, capabilities: emptyCapabilities })
    ])
    checkPermission(mockEl, createBinding(['dashboard', 'dataV']))
    expect(mockEl.parentNode.removeChild).not.toHaveBeenCalled()
  })

  it('should not throw when element has no parentNode', () => {
    mockEl.parentNode = null
    mockGetData.mockReturnValue([
      buildPermission({ menuAuth: false, anyManage: false, capabilities: emptyCapabilities }),
      buildPermission({ menuAuth: false, anyManage: false, capabilities: emptyCapabilities }),
      buildPermission({ menuAuth: false, anyManage: false, capabilities: emptyCapabilities }),
      buildPermission({ menuAuth: false, anyManage: false, capabilities: emptyCapabilities })
    ])
    expect(() => {
      checkPermission(mockEl, createBinding(['panel']))
    }).not.toThrow()
  })
})
