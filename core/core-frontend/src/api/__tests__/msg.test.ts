import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import { msgCountApi } from '../msg'

describe('API: msg', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('msgCountApi posts an empty body to fetch unread counts', async () => {
    await msgCountApi()

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/msg-center/count',
      data: {}
    })
  })
})
