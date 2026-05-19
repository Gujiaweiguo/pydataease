import { beforeEach, describe, expect, it, vi } from 'vitest'

const { baseRoutes, generatedRoutes, generateRoutesFn2 } = vi.hoisted(() => ({
  baseRoutes: [
    {
      path: '/dashboard',
      name: 'dashboard',
      hidden: false
    },
    {
      path: '/data',
      name: 'data',
      hidden: false,
      children: [
        {
          path: 'dataset',
          name: 'dataset',
          hidden: false
        },
        {
          path: 'secret',
          name: 'secret',
          hidden: true
        }
      ]
    },
    {
      path: '/hidden',
      name: 'hidden',
      hidden: true
    }
  ],
  generatedRoutes: [
    {
      path: '/system',
      name: 'system',
      hidden: false,
      children: [
        {
          path: 'user',
          name: 'user',
          hidden: false
        }
      ]
    }
  ],
  generateRoutesFn2: vi.fn()
}))

vi.mock('@/router', () => ({
  routes: baseRoutes
}))

vi.mock('@/router/establish', () => ({
  generateRoutesFn2
}))

vi.mock('@/views/404/index.vue', () => ({
  default: {
    name: 'NotFoundPage'
  }
}))

import { getFirstAuthMenu, pathValid, usePermissionStoreWithOut } from '../permission'

describe('permission store', () => {
  beforeEach(() => {
    const store = usePermissionStoreWithOut()
    generateRoutesFn2.mockReset()
    generateRoutesFn2.mockReturnValue(structuredClone(generatedRoutes))
    store.$reset()
  })

  it('starts with the expected initial state', () => {
    const store = usePermissionStoreWithOut()

    expect(store.routers).toEqual([])
    expect(store.addRouters).toEqual([])
    expect(store.isAddRouters).toBe(false)
    expect(store.currentPath).toBe('')
  })

  it('clear restores base routes and resets flags', () => {
    const store = usePermissionStoreWithOut()
    store.routers = [{ path: '/temp', hidden: false } as any]
    store.addRouters = [{ path: '/added', hidden: false } as any]
    store.isAddRouters = true
    store.currentPath = '/added'

    store.clear()

    expect(store.routers).toEqual(baseRoutes)
    expect(store.addRouters).toEqual([])
    expect(store.isAddRouters).toBe(false)
    expect(store.currentPath).toBe('')
  })

  it('generateRoutes appends generated routes and a catch-all route', async () => {
    const store = usePermissionStoreWithOut()

    await store.generateRoutes([{ path: '/system', name: 'system' }] as any)

    expect(generateRoutesFn2).toHaveBeenCalledWith([{ path: '/system', name: 'system' }])
    expect(store.routers).toEqual([...baseRoutes, ...generatedRoutes])
    expect(store.addRouters).toHaveLength(2)
    expect(store.addRouters[0]).toEqual(generatedRoutes[0])
    expect(store.addRouters[1]).toMatchObject({
      path: '/:catchAll(.*)',
      meta: { hidden: true }
    })
  })

  it('filters hidden routes and clones addRouters in getters', async () => {
    const store = usePermissionStoreWithOut()
    store.clear()
    await store.generateRoutes([{ path: '/system', name: 'system' }] as any)

    expect(store.getRoutersNotHidden.map(route => route.path)).toEqual([
      '/dashboard',
      '/data',
      '/system'
    ])

    const addRouters = store.getAddRouters
    addRouters[0].path = '/mutated'

    expect(store.addRouters[0].path).toBe('/system')
  })

  it('validates paths against nested routes and dataset-form aliases', () => {
    const store = usePermissionStoreWithOut()
    store.clear()

    expect(pathValid('/dashboard')).toBe(true)
    expect(pathValid('/data/dataset')).toBe(true)
    expect(pathValid('/dataset-form/123')).toBe(true)
    expect(pathValid('/missing/path')).toBe(false)
  })

  it('returns the first visible authorized menu path', () => {
    const store = usePermissionStoreWithOut()
    store.routers = [
      {
        path: '/hidden-root',
        hidden: true,
        children: [{ path: 'child', hidden: false }]
      },
      {
        path: '/data',
        hidden: false,
        children: [
          { path: 'hidden-child', hidden: true },
          { path: 'dataset', hidden: false }
        ]
      },
      {
        path: '/dashboard',
        hidden: false
      }
    ] as any

    expect(getFirstAuthMenu()).toBe('/hidden-root/child')
  })

  it('tracks currentPath and route initialization state', () => {
    const store = usePermissionStoreWithOut()

    store.setCurrentPath('/data/dataset')
    store.setIsAddRouters(true)

    expect(store.getCurrentPath).toBe('/data/dataset')
    expect(store.getIsAddRouters).toBe(true)
  })
})
