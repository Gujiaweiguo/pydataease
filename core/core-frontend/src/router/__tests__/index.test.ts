import { describe, it, expect, vi } from 'vitest'

const {
  mockRemoveRoute,
  mockHasRoute,
  mockGetRoutes,
  mockRouter,
  mockCreateWebHashHistory,
  mockCreateRouter
} = vi.hoisted(() => {
  const mockRemoveRoute = vi.fn()
  const mockHasRoute = vi.fn().mockReturnValue(true)
  const mockGetRoutes = vi.fn()
  const mockRouter = {
    getRoutes: mockGetRoutes,
    hasRoute: mockHasRoute,
    removeRoute: mockRemoveRoute
  }
  const mockCreateWebHashHistory = vi.fn().mockReturnValue('hash-history')
  const mockCreateRouter = vi.fn().mockReturnValue(mockRouter)
  return {
    mockRemoveRoute,
    mockHasRoute,
    mockGetRoutes,
    mockRouter,
    mockCreateWebHashHistory,
    mockCreateRouter
  }
})

vi.mock('vue-router_2', () => ({
  createRouter: mockCreateRouter,
  createWebHashHistory: mockCreateWebHashHistory
}))

vi.mock('@/layout/index.vue', () => ({ default: { name: 'LayoutStub' } }))
vi.mock('@/views/login/index.vue', () => ({ default: { name: 'LoginStub' } }))
vi.mock('@/views/401/index.vue', () => ({ default: { name: '401Stub' } }))
vi.mock('@/views/workbranch/index.vue', () => ({ default: { name: 'WorkbranchStub' } }))
vi.mock('@/views/sqlbot/index.vue', () => ({ default: { name: 'SqlbotStub' } }))
vi.mock('@/views/data-visualization/index.vue', () => ({ default: { name: 'DvCanvasStub' } }))
vi.mock('@/views/dashboard/index.vue', () => ({ default: { name: 'DashboardStub' } }))
vi.mock('@/views/dashboard/DashboardPreviewShow.vue', () => ({
  default: { name: 'DashboardPreviewStub' }
}))
vi.mock('@/views/system/modify-pwd/index.vue', () => ({ default: { name: 'ModifyPwdStub' } }))
vi.mock('@/views/chart/ChartView.vue', () => ({ default: { name: 'ChartViewStub' } }))
vi.mock('@/views/template/indexInject.vue', () => ({ default: { name: 'TemplateManageStub' } }))
vi.mock('@/custom-component/rich-text/DeRichTextView.vue', () => ({
  default: { name: 'RichTextStub' }
}))
vi.mock('@/views/chart/index.vue', () => ({ default: { name: 'ChartStub' } }))
vi.mock('@/views/data-visualization/PreviewShow.vue', () => ({
  default: { name: 'PreviewShowStub' }
}))
vi.mock('@/views/common/DeResourceTree.vue', () => ({ default: { name: 'DeResourceTreeStub' } }))
vi.mock('@/views/visualized/data/dataset/index.vue', () => ({
  default: { name: 'DatasetEmbeddedStub' }
}))
vi.mock('@/views/visualized/data/dataset/form/index.vue', () => ({
  default: { name: 'DatasetEmbeddedFormStub' }
}))
vi.mock('@/views/data-visualization/PreviewCanvas.vue', () => ({
  default: { name: 'PreviewCanvasStub' }
}))
vi.mock('@/views/data-visualization/LinkContainer.vue', () => ({
  default: { name: 'LinkContainerStub' }
}))

vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

import router, { routes, setupRouter, resetRouter } from '@/router/index'

describe('router/index', () => {
  it('creates router with hash history', () => {
    expect(mockCreateWebHashHistory).toHaveBeenCalled()
    expect(mockCreateRouter).toHaveBeenCalled()
    const createCall = mockCreateRouter.mock.calls[0][0]
    expect(createCall.history).toBe('hash-history')
  })

  it('exports a router instance', () => {
    expect(router).toBeDefined()
    expect(router).toBe(mockRouter)
  })

  it('registers expected static route paths', () => {
    const registeredPaths = routes.map(r => r.path)
    const expectedPaths = [
      '/',
      '/login',
      '/admin-login',
      '/401',
      '/sqlbot',
      '/dvCanvas',
      '/dashboard',
      '/dashboardPreview',
      '/modify-pwd',
      '/chart-view',
      '/template-manage',
      '/rich-text',
      '/chart',
      '/previewShow',
      '/preview',
      '/de-link/:uuid',
      '/dataset-embedded',
      '/dataset-embedded-form',
      '/DeResourceTree'
    ]
    for (const p of expectedPaths) {
      expect(registeredPaths).toContain(p)
    }
  })

  it('/login route has name "login"', () => {
    const loginRoute = routes.find(r => r.path === '/login')
    expect(loginRoute).toBeDefined()
    expect(loginRoute!.name).toBe('login')
  })

  it('setupRouter calls app.use with the router', () => {
    const mockApp = { use: vi.fn() } as any
    setupRouter(mockApp)
    expect(mockApp.use).toHaveBeenCalledWith(router)
  })

  it('resetRouter removes all routes except Login', () => {
    mockGetRoutes.mockReturnValue([
      { name: 'Login' },
      { name: 'workbranch' },
      { name: 'dashboard' },
      { name: 'chart' }
    ])
    mockHasRoute.mockReturnValue(true)
    resetRouter()
    expect(mockRemoveRoute).not.toHaveBeenCalledWith('Login')
    expect(mockRemoveRoute).toHaveBeenCalledWith('workbranch')
    expect(mockRemoveRoute).toHaveBeenCalledWith('dashboard')
    expect(mockRemoveRoute).toHaveBeenCalledWith('chart')
  })
})
