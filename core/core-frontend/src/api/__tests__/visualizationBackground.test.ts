import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import { queryVisualizationBackground } from '../visualization/visualizationBackground'

describe('API: visualizationBackground', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
  })

  it('queryVisualizationBackground gets all visualization backgrounds', async () => {
    await queryVisualizationBackground()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/visualizationBackground/findAll'
    })
  })
})
