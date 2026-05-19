import { describe, it, expect, vi } from 'vitest'

const { mockRouter } = vi.hoisted(() => {
  const mockRouter = {
    beforeEach: vi.fn(),
    afterEach: vi.fn(),
    push: vi.fn(),
    getRoutes: vi.fn().mockReturnValue([])
  }
  return { mockRouter }
})

vi.mock('@/router', () => ({
  default: mockRouter
}))

vi.mock('@/store/modules/user', () => ({
  useUserStoreWithOut: () => ({
    getUid: '',
    setUser: vi.fn()
  })
}))

vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({
    setAppModel: vi.fn(),
    getDesktop: false,
    getIsIframe: false
  })
}))

vi.mock('@/store/modules/permission', () => ({
  usePermissionStoreWithOut: () => ({
    setCurrentPath: vi.fn(),
    getIsAddRouters: false,
    getAddRouters: [],
    generateRoutes: vi.fn(),
    setIsAddRouters: vi.fn()
  }),
  pathValid: () => true,
  getFirstAuthMenu: () => '/workbranch/index'
}))

vi.mock('@/store/modules/interactive', () => ({
  interactiveStoreWithOut: () => ({
    initInteractive: vi.fn()
  })
}))

vi.mock('@/store/modules/appearance', () => ({
  useAppearanceStoreWithOut: () => ({
    setAppearance: vi.fn(),
    setFontList: vi.fn()
  })
}))

vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({
    getToken: ''
  })
}))

vi.mock('@/api/common', () => ({
  getDefaultSettings: () => Promise.resolve({}),
  getRoleRouters: () => Promise.resolve([])
}))

vi.mock('@/hooks/web/useNProgress', () => ({
  useNProgress: () => ({ start: vi.fn(), done: vi.fn() })
}))

vi.mock('@/hooks/web/usePageLoading', () => ({
  usePageLoading: () => ({ loadStart: vi.fn(), loadDone: vi.fn() })
}))

vi.mock('@/hooks/web/useLoading', () => ({
  useLoading: () => ({ open: vi.fn() })
}))

vi.mock('@/utils/utils', () => ({
  isMobile: () => false,
  checkPlatform: () => false,
  isLarkPlatform: () => false,
  isPlatformClient: () => false
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: {
      get: vi.fn().mockReturnValue(null),
      set: vi.fn()
    }
  })
}))

vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('element-plus-secondary', () => ({
  ElMessageBox: {
    confirm: vi.fn().mockResolvedValue(undefined),
    close: vi.fn()
  }
}))

import '@/permission'

describe('permission/index', () => {
  it('registers a beforeEach navigation guard on the router', () => {
    expect(mockRouter.beforeEach).toHaveBeenCalled()
  })

  it('registers an afterEach navigation guard on the router', () => {
    expect(mockRouter.afterEach).toHaveBeenCalled()
  })

  it('registers exactly one beforeEach and one afterEach guard', () => {
    expect(mockRouter.beforeEach).toHaveBeenCalledTimes(1)
    expect(mockRouter.afterEach).toHaveBeenCalledTimes(1)
  })

  it('the beforeEach callback is a function', () => {
    const guardFn = mockRouter.beforeEach.mock.calls[0][0]
    expect(typeof guardFn).toBe('function')
  })

  it('the afterEach callback is a function', () => {
    const guardFn = mockRouter.afterEach.mock.calls[0][0]
    expect(typeof guardFn).toBe('function')
  })
})
