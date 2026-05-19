import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import { queryAll } from '../visualization/pdfTemplate'

describe('API: pdfTemplate', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
  })

  it('queryAll gets all pdf templates with loading disabled', async () => {
    await queryAll()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/pdf-template/queryAll',
      loading: false
    })
  })
})
