import { describe, it, expect, vi } from 'vitest'

const { mockXpackComponent } = vi.hoisted(() => {
  const mockXpackComponent = vi.fn(() => ({ template: '<div>xpack</div>' }))
  return { mockXpackComponent }
})

vi.mock('@/components/plugin', () => ({
  XpackComponent: mockXpackComponent
}))

vi.mock('@/utils/validate', () => ({
  isExternal: (path: string) => /^(https?:|mailto:|tel:)/.test(path)
}))

vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

import {
  generateRoutesFn2,
  formatRoute,
  resolvePath,
  decorate,
  Layout,
  LayoutTransition
} from '@/router/establish'

describe('router/establish', () => {
  describe('Layout exports', () => {
    it('exports Layout as a function', () => {
      expect(typeof Layout).toBe('function')
    })

    it('exports LayoutTransition as a function', () => {
      expect(typeof LayoutTransition).toBe('function')
    })
  })

  describe('generateRoutesFn2', () => {
    it('assigns Layout function when component is "Layout"', () => {
      const routes = [
        {
          path: '/workbranch',
          name: 'workbranch',
          hidden: false,
          component: 'Layout',
          meta: { title: 'Workbranch' }
        }
      ]
      const result = generateRoutesFn2(routes as AppCustomRouteRecordRaw[])
      expect(result[0].component).toBe(Layout)
    })

    it('assigns LayoutTransition function when component is "LayoutTransition"', () => {
      const routes = [
        {
          path: '/trans',
          name: 'trans',
          hidden: false,
          component: 'LayoutTransition',
          meta: { title: 'Trans' }
        }
      ]
      const result = generateRoutesFn2(routes as AppCustomRouteRecordRaw[])
      expect(result[0].component).toBe(LayoutTransition)
    })

    it('attempts to resolve view component via glob for non-Layout paths', () => {
      const routes = [
        {
          path: '/myview',
          name: 'myview',
          hidden: false,
          component: 'login/index',
          meta: { title: 'MyView' }
        }
      ]
      const result = generateRoutesFn2(routes as AppCustomRouteRecordRaw[])
      expect(result[0].path).toBe('/myview')
      expect(result[0].name).toBe('myview')
      expect(result[0].component).not.toBe(Layout)
      expect(result[0].component).not.toBe(LayoutTransition)
    })

    it('handles plugin routes by assigning XpackComponent and props', () => {
      const routes = [
        {
          path: '/xpack-plugin',
          name: 'xpack-plugin',
          hidden: false,
          plugin: true,
          component: 'myPlugin',
          inLayout: true,
          meta: { title: 'Plugin' }
        }
      ]
      const result = generateRoutesFn2(routes as AppCustomRouteRecordRaw[])
      expect(result[0].component).toBe(mockXpackComponent)
      expect(result[0].props).toEqual({ jsname: 'myPlugin', inLayout: true })
    })

    it('handles routes with top and inLayout by decorating them', () => {
      const routes = [
        {
          path: '/decorated',
          name: 'decorated',
          hidden: false,
          top: true,
          inLayout: true,
          component: 'myview/index',
          meta: { title: 'Decorated' }
        }
      ]
      const result = generateRoutesFn2(routes as AppCustomRouteRecordRaw[])
      expect(result[0].component).toBe(Layout)
      expect(result[0].children).toBeDefined()
      expect(result[0].children!.length).toBe(1)
      expect(result[0].children![0].path).toBe('index')
    })

    it('recursively processes children', () => {
      const routes = [
        {
          path: '/parent',
          name: 'parent',
          hidden: false,
          component: 'Layout',
          meta: {},
          children: [
            {
              path: 'child',
              name: 'child',
              hidden: false,
              component: 'login/index',
              meta: {}
            }
          ]
        }
      ]
      const result = generateRoutesFn2(routes as AppCustomRouteRecordRaw[])
      expect(result[0].component).toBe(Layout)
      expect(result[0].children).toBeDefined()
      expect(result[0].children!.length).toBe(1)
      expect(result[0].children![0].path).toBe('child')
    })

    it('handles routes without component gracefully', () => {
      const routes = [
        {
          path: '/nocomp',
          name: 'nocomp',
          hidden: false,
          meta: {}
        }
      ]
      const result = generateRoutesFn2(routes as AppCustomRouteRecordRaw[])
      expect(result[0].component).toBeUndefined()
    })
  })

  describe('formatRoute', () => {
    it('flattens route with 1 child by merging paths', () => {
      const arr = [
        {
          path: '/workbranch',
          name: 'workbranch',
          hidden: false,
          children: [
            {
              path: 'index',
              name: 'workbranch-index',
              hidden: false
            }
          ]
        }
      ]
      const result = formatRoute(arr as AppCustomRouteRecordRaw[])
      expect(result[0].path).toBe('/workbranch/index')
      expect(result[0].children).toEqual([])
    })

    it('does NOT flatten path "/data"', () => {
      const arr = [
        {
          path: '/data',
          name: 'data',
          hidden: false,
          children: [
            {
              path: 'index',
              name: 'data-index',
              hidden: false
            }
          ]
        }
      ]
      const result = formatRoute(arr as AppCustomRouteRecordRaw[])
      expect(result[0].path).toBe('/data')
      expect(result[0].children!.length).toBe(1)
    })

    it('does not flatten routes with multiple children', () => {
      const arr = [
        {
          path: '/multi',
          name: 'multi',
          hidden: false,
          children: [
            { path: 'a', name: 'a', hidden: false },
            { path: 'b', name: 'b', hidden: false }
          ]
        }
      ]
      const result = formatRoute(arr as AppCustomRouteRecordRaw[])
      expect(result[0].path).toBe('/multi')
      expect(result[0].children!.length).toBe(2)
    })

    it('does not flatten routes with zero children', () => {
      const arr = [
        {
          path: '/nochildren',
          name: 'nochildren',
          hidden: false,
          children: []
        }
      ]
      const result = formatRoute(arr as AppCustomRouteRecordRaw[])
      expect(result[0].path).toBe('/nochildren')
    })

    it('does not mutate the original array', () => {
      const arr = [
        {
          path: '/original',
          name: 'original',
          hidden: false,
          children: [{ path: 'sub', name: 'sub', hidden: false }]
        }
      ]
      formatRoute(arr as AppCustomRouteRecordRaw[])
      expect(arr[0].path).toBe('/original')
    })
  })

  describe('resolvePath', () => {
    it('returns redirect for root path "/"', () => {
      const item = {
        path: '/',
        redirect: '/workbranch/index',
        meta: {},
        hidden: true,
        name: 'index'
      }
      expect(resolvePath(item as AppRouteRecordRaw)).toBe('/workbranch/index')
    })

    it('returns child path for routes with children', () => {
      const item = {
        path: '/workbranch',
        meta: {},
        hidden: true,
        name: 'workbranch',
        children: [
          {
            path: 'index',
            meta: {},
            hidden: true,
            name: 'workbranch-index'
          }
        ]
      }
      expect(resolvePath(item as AppRouteRecordRaw)).toBe('/workbranch/index')
    })

    it('returns item path when no children', () => {
      const item = {
        path: '/login',
        meta: {},
        hidden: true,
        name: 'login'
      }
      expect(resolvePath(item as AppRouteRecordRaw)).toBe('/login')
    })

    it('resolves nested children recursively', () => {
      const item = {
        path: '/parent',
        meta: {},
        hidden: true,
        name: 'parent',
        children: [
          {
            path: 'child',
            meta: {},
            hidden: true,
            name: 'child',
            children: [
              {
                path: 'grandchild',
                meta: {},
                hidden: true,
                name: 'grandchild'
              }
            ]
          }
        ]
      }
      expect(resolvePath(item as AppRouteRecordRaw)).toBe('/parent/child/grandchild')
    })
  })

  describe('decorate', () => {
    it('wraps a route without children in a Layout parent with index child', () => {
      const route = {
        path: '/mypage',
        name: 'mypage',
        hidden: false,
        inLayout: true,
        meta: { title: 'MyPage' },
        component: 'views/mypage/index'
      }
      const result = decorate(route as AppCustomRouteRecordRaw)
      expect(result.component).toBe('Layout')
      expect(result.path).toBe('/mypage')
      expect(result.children).toBeDefined()
      expect(result.children!.length).toBe(1)
      expect(result.children![0].path).toBe('index')
      expect(result.children![0].inLayout).toBe(false)
    })

    it('preserves existing children without adding index', () => {
      const route = {
        path: '/existing',
        name: 'existing',
        hidden: false,
        inLayout: true,
        meta: {},
        children: [
          { path: 'sub1', name: 'sub1', hidden: false },
          { path: 'sub2', name: 'sub2', hidden: false }
        ]
      }
      const result = decorate(route as AppCustomRouteRecordRaw)
      expect(result.component).toBe('Layout')
      expect(result.children!.length).toBe(2)
    })
  })
})
