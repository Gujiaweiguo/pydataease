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
  mockGetData: vi.fn<
    () => Array<{
      menuAuth?: boolean
      anyManage?: boolean
      capabilities?: {
        canView?: boolean
        canUse?: boolean
        canExport?: boolean
        canManage?: boolean
        canAuthorize?: boolean
      }
    }>
  >()
}))
vi.mock('@/store/modules/interactive', () => ({
  interactiveStoreWithOut: () => ({
    get getData() {
      return mockGetData()
    },
    getResourceCapabilities(resourceType?: string | null) {
      const resourceTypeToIndex = {
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

// Import after mocks are set up
import { checkPermission } from '../Permission'

const createBinding = (value?: unknown) => ({ value })
const createElement = () => ({ parentNode: { removeChild: vi.fn() } })
const emptyCapabilities = {
  canView: false,
  canUse: false,
  canExport: false,
  canManage: false,
  canAuthorize: false
}

describe('checkPermission', () => {
  beforeEach(() => {
    mockGetData.mockReset()
  })

  const fullCapabilities = {
    canView: true,
    canUse: true,
    canExport: true,
    canManage: true,
    canAuthorize: false
  }

  it('should keep element when all required permissions have menuAuth and anyManage', () => {
    mockGetData.mockReturnValue([
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities },
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities },
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities },
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities }
    ])
    const el = createElement()
    checkPermission(el, createBinding(['panel']))
    expect(el.parentNode.removeChild).not.toHaveBeenCalled()
  })

  it('should keep element when capability permission is satisfied', () => {
    mockGetData.mockReturnValue([
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities },
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities },
      { menuAuth: true, anyManage: false, capabilities: { ...fullCapabilities, canManage: false } },
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities }
    ])
    const el = createElement()
    checkPermission(el, createBinding(['dataset:export']))
    expect(el.parentNode.removeChild).not.toHaveBeenCalled()
  })

  it('should remove element from DOM when permission lacks menuAuth or anyManage', () => {
    mockGetData.mockReturnValue([
      { menuAuth: true, anyManage: false, capabilities: { ...fullCapabilities, canManage: false } }, // panel - missing anyManage
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities },
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities },
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities }
    ])
    const el = createElement()
    checkPermission(el, createBinding(['panel']))
    expect(el.parentNode.removeChild).toHaveBeenCalledWith(el)
  })

  it('should remove element when capability permission is not satisfied', () => {
    mockGetData.mockReturnValue([
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities },
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities },
      {
        menuAuth: true,
        anyManage: false,
        capabilities: {
          canView: true,
          canUse: true,
          canExport: false,
          canManage: false,
          canAuthorize: false
        }
      },
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities }
    ])
    const el = createElement()
    checkPermission(el, createBinding(['dataset:export']))
    expect(el.parentNode.removeChild).toHaveBeenCalledWith(el)
  })

  it('should require ALL permissions to pass (every, not some)', () => {
    mockGetData.mockReturnValue([
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities }, // panel
      { menuAuth: true, anyManage: false, capabilities: { ...fullCapabilities, canManage: false } }, // screen - fails
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities }, // dataset
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities } // datasource
    ])
    const el = createElement()
    // Both panel and screen required; screen fails → element removed
    checkPermission(el, createBinding(['panel', 'screen']))
    expect(el.parentNode.removeChild).toHaveBeenCalledWith(el)
  })

  it('should throw Error when value is not an array', () => {
    mockGetData.mockReturnValue([{}, {}, {}, {}])
    const el = createElement()
    expect(() => checkPermission(el, createBinding('panel'))).toThrow(
      Error(`使用方式： v-permission="['panel']"`)
    )
  })

  it('should throw Error when value is undefined', () => {
    mockGetData.mockReturnValue([{}, {}, {}, {}])
    const el = createElement()
    expect(() => checkPermission(el, createBinding(undefined))).toThrow(
      Error(`使用方式： v-permission="['panel']"`)
    )
  })

  it('should map permission flags to correct array indices: panel(0), screen(1), dataset(2), datasource(3)', () => {
    mockGetData.mockReturnValue([
      { menuAuth: false, anyManage: false, capabilities: emptyCapabilities }, // panel(0)
      { menuAuth: false, anyManage: false, capabilities: emptyCapabilities }, // screen(1)
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities }, // dataset(2)
      { menuAuth: false, anyManage: false, capabilities: emptyCapabilities } // datasource(3)
    ])
    const el = createElement()
    // Only dataset has permission
    checkPermission(el, createBinding(['dataset']))
    expect(el.parentNode.removeChild).not.toHaveBeenCalled()

    // But panel should fail
    el.parentNode.removeChild.mockClear()
    checkPermission(el, createBinding(['panel']))
    expect(el.parentNode.removeChild).toHaveBeenCalledWith(el)
  })

  it('should not remove element if parentNode is null', () => {
    mockGetData.mockReturnValue([
      { menuAuth: false, anyManage: false, capabilities: emptyCapabilities },
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities },
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities },
      { menuAuth: true, anyManage: true, capabilities: fullCapabilities }
    ])
    const el = { parentNode: null }
    // Should not throw even though permission fails
    expect(() => checkPermission(el, createBinding(['panel']))).not.toThrow()
  })
})
