import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import { getJobLogLienChartInfo, getResourceCount } from '../syncSummary'

describe('API: syncSummary', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('getResourceCount gets the summary endpoint and unwraps response data', async () => {
    const response = {
      data: {
        jobCount: 4,
        datasourceCount: 2,
        jobLogCount: 9
      }
    }
    mockRequest.get.mockResolvedValueOnce(response)

    const result = await getResourceCount()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: 'sync/summary/resourceCount',
      method: 'get'
    })
    expect(result).toEqual(response.data)
  })

  it('getJobLogLienChartInfo posts an empty string payload to the chart endpoint', async () => {
    await getJobLogLienChartInfo()

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/summary/logChartData',
      method: 'post',
      data: ''
    })
  })
})
