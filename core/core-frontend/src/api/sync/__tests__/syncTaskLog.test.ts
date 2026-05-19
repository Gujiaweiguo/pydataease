import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import {
  clear,
  getTaskLogDetailApi,
  getTaskLogListApi,
  removeApi,
  terminationTaskApi
} from '../syncTaskLog'

describe('API: syncTaskLog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('getTaskLogListApi posts pager filters for task logs', async () => {
    const payload = { taskName: 'nightly' }

    await getTaskLogListApi(4, 25, payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/task/log/pager/4/25',
      data: payload
    })
  })

  it('removeApi posts the delete endpoint for one log id', async () => {
    await removeApi('log-1')

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/task/log/delete/log-1'
    })
  })

  it('getTaskLogDetailApi gets log details from the requested line number', async () => {
    await getTaskLogDetailApi('log-2', 120)

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/sync/task/log/detail/log-2/120'
    })
  })

  it('clear posts the task log clear payload', async () => {
    const payload = { beforeDays: 30 }

    await clear(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/task/log/clear',
      data: payload
    })
  })

  it('terminationTaskApi posts an empty body when stopping a running task log', async () => {
    await terminationTaskApi('log-3')

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/task/log/terminationTask/log-3',
      data: {}
    })
  })
})
