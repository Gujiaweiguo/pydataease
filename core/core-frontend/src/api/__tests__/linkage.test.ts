import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import {
  getPanelAllLinkageInfo,
  getViewLinkageGather,
  getViewLinkageGatherArray,
  removeLinkage,
  saveLinkage,
  updateLinkageActive
} from '../visualization/linkage'

describe('API: linkage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('getViewLinkageGather posts the linkage gather payload', async () => {
    const payload = { viewId: 'view-1' }

    await getViewLinkageGather(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/linkage/getViewLinkageGather',
      data: payload
    })
  })

  it('getViewLinkageGatherArray posts the linkage gather array payload', async () => {
    const payload = { viewIds: ['view-1', 'view-2'] }

    await getViewLinkageGatherArray(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/linkage/getViewLinkageGatherArray',
      data: payload
    })
  })

  it('saveLinkage posts linkage definitions', async () => {
    const payload = { panelId: 'dv-1', links: [] }

    await saveLinkage(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/linkage/saveLinkage',
      data: payload
    })
  })

  it('getPanelAllLinkageInfo uses the default snapshot resource table', async () => {
    await getPanelAllLinkageInfo('dv-2')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/linkage/getVisualizationAllLinkageInfo/dv-2/snapshot'
    })
  })

  it('getPanelAllLinkageInfo accepts a custom resource table', async () => {
    await getPanelAllLinkageInfo('dv-3', 'template')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/linkage/getVisualizationAllLinkageInfo/dv-3/template'
    })
  })

  it('updateLinkageActive posts active-state changes', async () => {
    const payload = { linkageId: 'link-1', active: false }

    await updateLinkageActive(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/linkage/updateLinkageActive',
      data: payload
    })
  })

  it('removeLinkage posts linkage removal payloads', async () => {
    const payload = { linkageId: 'link-2' }

    await removeLinkage(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/linkage/removeLinkage',
      data: payload
    })
  })
})
