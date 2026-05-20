import { describe, expect, it, vi, beforeEach } from 'vitest'

const { requestMock } = vi.hoisted(() => ({
  requestMock: {
    get: vi.fn().mockResolvedValue({ data: [] })
  }
}))

vi.mock('@/config/axios', () => ({ default: requestMock }))

import { queryVisualizationBackground } from '../visualizationBackground'

describe('visualizationBackground API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('queryVisualizationBackground calls request.get with correct url', async () => {
    await queryVisualizationBackground()
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/visualizationBackground/findAll'
    })
  })
})
