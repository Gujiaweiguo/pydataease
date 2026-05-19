import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import { watermarkFind, watermarkSave } from '../watermark'

describe('API: watermark', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('watermarkSave posts watermark settings', async () => {
    const payload = { enabled: true, text: 'internal' }

    await watermarkSave(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/watermark/save',
      data: payload
    })
  })

  it('watermarkFind gets the current watermark config', async () => {
    await watermarkFind()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: 'watermark/find'
    })
  })
})
