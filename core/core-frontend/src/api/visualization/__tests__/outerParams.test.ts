import { describe, expect, it, vi, beforeEach } from 'vitest'

const { requestMock } = vi.hoisted(() => ({
  requestMock: {
    get: vi.fn().mockResolvedValue({ data: {} }),
    post: vi.fn().mockResolvedValue({ data: {} })
  }
}))

vi.mock('@/config/axios', () => ({ default: requestMock }))

import { queryWithVisualizationId, updateOuterParamsSet, getOuterParamsInfo } from '../outerParams'

describe('outerParams API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('queryWithVisualizationId calls request.get with correct url', async () => {
    await queryWithVisualizationId('dv1')
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/outerParams/queryWithVisualizationId/dv1'
    })
  })

  it('updateOuterParamsSet calls request.post with data and loading', async () => {
    const data = { paramsInfo: 'test' }
    await updateOuterParamsSet(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/outerParams/updateOuterParamsSet',
      data,
      loading: true
    })
  })

  it('getOuterParamsInfo calls request.get with correct url and flags', async () => {
    await getOuterParamsInfo('dv1')
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/outerParams/getOuterParamsInfo/dv1',
      method: 'get',
      loading: false
    })
  })
})
