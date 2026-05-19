import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import {
  batchDelApi,
  deleteByIdApi,
  getByIdApi,
  getFieldListApi,
  getSchemaApi,
  latestUseApi,
  saveApi,
  sourceDsPageApi,
  targetDsPageApi,
  updateApi,
  validateApi,
  validateByIdApi
} from '../syncDatasource'

describe('API: syncDatasource', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('sourceDsPageApi posts the source datasource pager payload', async () => {
    const payload = { keyword: 'mysql' }

    await sourceDsPageApi(2, 20, payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/datasource/source/pager/2/20',
      data: payload
    })
  })

  it('targetDsPageApi posts the target datasource pager payload', async () => {
    const payload = { keyword: 'pg' }

    await targetDsPageApi(1, 10, payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/datasource/target/pager/1/10',
      data: payload
    })
  })

  it('latestUseApi posts an empty body for the requested source type', async () => {
    await latestUseApi('MYSQL')

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/datasource/latestUse/MYSQL',
      data: {}
    })
  })

  it('validateApi posts datasource validation payloads', async () => {
    const payload = { host: '127.0.0.1' }

    await validateApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/datasource/validate',
      data: payload
    })
  })

  it('getSchemaApi posts datasource schema lookup payloads', async () => {
    const payload = { datasourceId: 'ds-1' }

    await getSchemaApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/datasource/getSchema',
      data: payload
    })
  })

  it('saveApi posts new datasource payloads', async () => {
    const payload = { name: 'target-ds' }

    await saveApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/datasource/save',
      data: payload
    })
  })

  it('getByIdApi gets datasource details by id', async () => {
    await getByIdApi('ds-2')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/sync/datasource/get/ds-2'
    })
  })

  it('updateApi posts datasource update payloads', async () => {
    const payload = { id: 'ds-3', name: 'updated' }

    await updateApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/datasource/update',
      data: payload
    })
  })

  it('deleteByIdApi posts the datasource delete endpoint', async () => {
    await deleteByIdApi('ds-4')

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/datasource/delete/ds-4'
    })
  })

  it('batchDelApi posts the datasource id list', async () => {
    const ids = ['ds-5', 'ds-6']

    await batchDelApi(ids)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/datasource/batchDel',
      data: ids
    })
  })

  it('getFieldListApi posts the source field lookup payload', async () => {
    const payload = { sourceId: 'src-1', targetId: 'tgt-1' }

    await getFieldListApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/datasource/fields',
      data: payload
    })
  })

  it('validateByIdApi gets datasource validation results by id', async () => {
    await validateByIdApi('ds-7')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/sync/datasource/validate/ds-7'
    })
  })
})
