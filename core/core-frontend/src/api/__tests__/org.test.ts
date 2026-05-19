import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import { deleteApi, resourceExistApi, saveApi, searchApi, updateApi } from '../org'

describe('API: org', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('searchApi posts tree paging filters', async () => {
    const payload = { keyword: '研发' }

    await searchApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/org/page/tree',
      data: payload
    })
  })

  it('saveApi posts create payloads to the org create endpoint', async () => {
    const payload = { name: '华东大区' }

    await saveApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/org/page/create',
      data: payload
    })
  })

  it('updateApi posts edited organization payloads', async () => {
    const payload = { id: 'org-1', name: '华北大区' }

    await updateApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/org/page/edit',
      data: payload
    })
  })

  it('resourceExistApi checks org resources with GET', async () => {
    await resourceExistApi('org-2')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/org/resourceExist/org-2'
    })
  })

  it('deleteApi posts to the org delete endpoint', async () => {
    await deleteApi('org-3')

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/org/page/delete/org-3'
    })
  })
})
