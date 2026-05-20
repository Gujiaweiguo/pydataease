import { describe, it, expect, vi } from 'vitest'

const { mockPost } = vi.hoisted(() => ({
  mockPost: vi.fn(() => Promise.resolve({ data: {} }))
}))

vi.mock('@/config/axios', () => ({
  default: { post: mockPost }
}))

import {
  getDatasourceRelationship,
  getDatasetRelationship,
  getPanelRelationship,
  resourceCheckPermission
} from '../index'

describe('relation API', () => {
  it('getDatasourceRelationship should call request.post with datasource url', () => {
    getDatasourceRelationship('123')
    expect(mockPost).toHaveBeenCalledWith({ url: '/relation/datasource/123' })
  })

  it('getDatasetRelationship should call request.post with dataset url', () => {
    getDatasetRelationship('456')
    expect(mockPost).toHaveBeenCalledWith({ url: '/relation/dataset/456' })
  })

  it('getPanelRelationship should call request.post with dv url', () => {
    getPanelRelationship('789')
    expect(mockPost).toHaveBeenCalledWith({ url: '/relation/dv/789' })
  })

  it('resourceCheckPermission should call request.post with checkPermission url', () => {
    resourceCheckPermission('abc')
    expect(mockPost).toHaveBeenCalledWith({ url: '/resource/checkPermission/abc' })
  })
})
