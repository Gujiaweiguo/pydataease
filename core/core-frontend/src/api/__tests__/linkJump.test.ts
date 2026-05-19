import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import {
  getTableFieldWithViewId,
  queryTargetVisualizationJumpInfo,
  queryVisualizationJumpInfo,
  queryWithViewId,
  removeJumpSet,
  updateJumpSet,
  updateJumpSetActive,
  viewTableDetailList
} from '../visualization/linkJump'

describe('API: linkJump', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('getTableFieldWithViewId gets table fields by view id', async () => {
    await getTableFieldWithViewId('view-1')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/linkJump/getTableFieldWithViewId/view-1'
    })
  })

  it('queryWithViewId gets jump info by dv id and view id', async () => {
    await queryWithViewId('dv-1', 'view-2')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/linkJump/queryWithViewId/dv-1/view-2'
    })
  })

  it('updateJumpSet posts jump settings with loading enabled', async () => {
    const payload = { jumpId: 'jump-1', targetId: 'dv-2' }

    await updateJumpSet(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/linkJump/updateJumpSet',
      data: payload,
      loading: true
    })
  })

  it('queryTargetVisualizationJumpInfo posts target jump lookup payloads with loading enabled', async () => {
    const payload = { sourceViewId: 'view-3' }

    await queryTargetVisualizationJumpInfo(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/linkJump/queryTargetVisualizationJumpInfo',
      data: payload,
      loading: true
    })
  })

  it('queryVisualizationJumpInfo uses the default snapshot resource table', async () => {
    await queryVisualizationJumpInfo('dv-3')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/linkJump/queryVisualizationJumpInfo/dv-3/snapshot',
      loading: false
    })
  })

  it('queryVisualizationJumpInfo accepts a custom resource table', async () => {
    await queryVisualizationJumpInfo('dv-4', 'template')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/linkJump/queryVisualizationJumpInfo/dv-4/template',
      loading: false
    })
  })

  it('viewTableDetailList gets detail tables with loading disabled', async () => {
    await viewTableDetailList('dv-5')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/linkJump/viewTableDetailList/dv-5',
      loading: false
    })
  })

  it('updateJumpSetActive posts active-state changes with loading enabled', async () => {
    const payload = { jumpId: 'jump-2', active: true }

    await updateJumpSetActive(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/linkJump/updateJumpSetActive',
      data: payload,
      loading: true
    })
  })

  it('removeJumpSet posts deletion payloads with loading enabled', async () => {
    const payload = { jumpId: 'jump-3' }

    await removeJumpSet(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/linkJump/removeJumpSet',
      data: payload,
      loading: true
    })
  })
})
