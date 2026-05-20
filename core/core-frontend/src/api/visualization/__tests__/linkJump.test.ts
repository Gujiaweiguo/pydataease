import { describe, expect, it, vi, beforeEach } from 'vitest'

const { requestMock } = vi.hoisted(() => ({
  requestMock: {
    get: vi.fn().mockResolvedValue({ data: {} }),
    post: vi.fn().mockResolvedValue({ data: {} })
  }
}))

vi.mock('@/config/axios', () => ({ default: requestMock }))

import {
  getTableFieldWithViewId,
  queryWithViewId,
  updateJumpSet,
  queryTargetVisualizationJumpInfo,
  queryVisualizationJumpInfo,
  viewTableDetailList,
  updateJumpSetActive,
  removeJumpSet
} from '../linkJump'

describe('linkJump API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('getTableFieldWithViewId calls request.get with correct url', async () => {
    await getTableFieldWithViewId('view123')
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/linkJump/getTableFieldWithViewId/view123'
    })
  })

  it('queryWithViewId calls request.get with correct url', async () => {
    await queryWithViewId('dv1', 'view1')
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/linkJump/queryWithViewId/dv1/view1'
    })
  })

  it('updateJumpSet calls request.post with data and loading', async () => {
    const data = { jumpInfo: 'test' }
    await updateJumpSet(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/linkJump/updateJumpSet',
      data,
      loading: true
    })
  })

  it('queryTargetVisualizationJumpInfo calls request.post with data and loading', async () => {
    const data = { dvId: 'dv1' }
    await queryTargetVisualizationJumpInfo(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/linkJump/queryTargetVisualizationJumpInfo',
      data,
      loading: true
    })
  })

  it('queryVisualizationJumpInfo calls request.get with default resourceTable', async () => {
    await queryVisualizationJumpInfo('dv1')
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/linkJump/queryVisualizationJumpInfo/dv1/snapshot',
      loading: false
    })
  })

  it('queryVisualizationJumpInfo calls request.get with custom resourceTable', async () => {
    await queryVisualizationJumpInfo('dv1', 'core')
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/linkJump/queryVisualizationJumpInfo/dv1/core',
      loading: false
    })
  })

  it('viewTableDetailList calls request.get with correct url', async () => {
    await viewTableDetailList('dv1')
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/linkJump/viewTableDetailList/dv1',
      loading: false
    })
  })

  it('updateJumpSetActive calls request.post with data and loading', async () => {
    const data = { id: 1, active: true }
    await updateJumpSetActive(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/linkJump/updateJumpSetActive',
      data,
      loading: true
    })
  })

  it('removeJumpSet calls request.post with data and loading', async () => {
    const data = { id: 1 }
    await removeJumpSet(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/linkJump/removeJumpSet',
      data,
      loading: true
    })
  })
})
