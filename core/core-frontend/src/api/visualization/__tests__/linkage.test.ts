import { describe, expect, it, vi, beforeEach } from 'vitest'

const { requestMock } = vi.hoisted(() => ({
  requestMock: {
    get: vi.fn().mockResolvedValue({ data: {} }),
    post: vi.fn().mockResolvedValue({ data: {} })
  }
}))

vi.mock('@/config/axios', () => ({ default: requestMock }))

import {
  getViewLinkageGather,
  getViewLinkageGatherArray,
  saveLinkage,
  getPanelAllLinkageInfo,
  updateLinkageActive,
  removeLinkage
} from '../linkage'

describe('linkage API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('getViewLinkageGather calls request.post with correct url and data', async () => {
    const data = { dvId: 'dv1', viewIds: ['v1'] }
    await getViewLinkageGather(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/linkage/getViewLinkageGather',
      data
    })
  })

  it('getViewLinkageGatherArray calls request.post with correct url and data', async () => {
    const data = { dvId: 'dv1', viewIds: ['v1', 'v2'] }
    await getViewLinkageGatherArray(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/linkage/getViewLinkageGatherArray',
      data
    })
  })

  it('saveLinkage calls request.post with correct url and data', async () => {
    const data = { linkageInfo: 'test' }
    await saveLinkage(data)
    expect(requestMock.post).toHaveBeenCalledWith({ url: '/linkage/saveLinkage', data })
  })

  it('getPanelAllLinkageInfo calls request.get with default resourceTable', async () => {
    await getPanelAllLinkageInfo('dv1')
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/linkage/getVisualizationAllLinkageInfo/dv1/snapshot'
    })
  })

  it('getPanelAllLinkageInfo calls request.get with custom resourceTable', async () => {
    await getPanelAllLinkageInfo('dv1', 'core')
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/linkage/getVisualizationAllLinkageInfo/dv1/core'
    })
  })

  it('updateLinkageActive calls request.post with correct url and data', async () => {
    const data = { id: 1, active: true }
    await updateLinkageActive(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/linkage/updateLinkageActive',
      data
    })
  })

  it('removeLinkage calls request.post with correct url and data', async () => {
    const data = { id: 1 }
    await removeLinkage(data)
    expect(requestMock.post).toHaveBeenCalledWith({ url: '/linkage/removeLinkage', data })
  })
})
