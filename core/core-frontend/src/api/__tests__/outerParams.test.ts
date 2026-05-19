import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import {
  getOuterParamsInfo,
  queryWithVisualizationId,
  updateOuterParamsSet
} from '../visualization/outerParams'

describe('API: outerParams', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('queryWithVisualizationId gets outer params by visualization id', async () => {
    await queryWithVisualizationId('dv-1')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/outerParams/queryWithVisualizationId/dv-1'
    })
  })

  it('updateOuterParamsSet posts the request payload with loading enabled', async () => {
    const payload = { dvId: 'dv-2', params: [{ key: 'region' }] }

    await updateOuterParamsSet(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/outerParams/updateOuterParamsSet',
      data: payload,
      loading: true
    })
  })

  it('getOuterParamsInfo gets outer params info with explicit request options', async () => {
    await getOuterParamsInfo('dv-3')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/outerParams/getOuterParamsInfo/dv-3',
      method: 'get',
      loading: false
    })
  })
})
