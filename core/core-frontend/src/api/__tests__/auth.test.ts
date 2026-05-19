import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({
  default: mockRequest
}))

import {
  busiTargetPerSaveApi,
  menuTargetPerApi,
  queryUserApi,
  queryUserOptionsApi,
  resourceTreeApi
} from '../auth'

describe('API: auth', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('queryUserApi posts the current org filter payload', async () => {
    const payload = { keyword: 'alice' }
    const response = { data: { rows: [{ id: 1 }] } }
    mockRequest.post.mockResolvedValueOnce(response)

    const result = await queryUserApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/user/byCurOrg',
      data: payload
    })
    expect(result).toBe(response)
  })

  it('queryUserOptionsApi requests the org option list', async () => {
    await queryUserOptionsApi()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/user/org/option'
    })
  })

  it('resourceTreeApi appends the flag to the business resource path', async () => {
    await resourceTreeApi('dataset')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/auth/busiResource/dataset'
    })
  })

  it('menuTargetPerApi posts menu target permissions', async () => {
    const payload = { roleId: 8, authIds: ['menu-1'] }

    await menuTargetPerApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/auth/menuTargetPermission',
      data: payload
    })
  })

  it('busiTargetPerSaveApi posts saved business target permissions', async () => {
    const payload = { targetId: 3, permissions: ['read'] }

    await busiTargetPerSaveApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/auth/saveBusiTargetPer',
      data: payload
    })
  })
})
