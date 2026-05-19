import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({
  default: mockRequest
}))

import {
  batchUpdate,
  findCategories,
  findOne,
  save,
  templateDelete
} from '../template'

describe('API: template', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('save posts template data with loading enabled', async () => {
    const payload = { name: 'Sales board', categoryId: 5 }

    await save(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/templateManage/save',
      data: payload,
      loading: true
    })
  })

  it('templateDelete builds the delete path from template and category ids', async () => {
    await templateDelete(9, 12)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/templateManage/delete/9/12'
    })
  })

  it('findOne fetches a template by id', async () => {
    await findOne(1001)

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/templateManage/findOne/1001'
    })
  })

  it('findCategories posts category filters with loading enabled', async () => {
    const payload = { keyword: 'marketing' }

    await findCategories(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/templateManage/findCategories',
      data: payload,
      loading: true
    })
  })

  it('batchUpdate posts batch update payloads to the batch endpoint', async () => {
    const payload = { templateIds: [1, 2], categoryId: 99 }

    await batchUpdate(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/templateManage/batchUpdate',
      data: payload
    })
  })
})
