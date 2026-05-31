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
  createColumnPermissionApi,
  createPermissionWhitelistApi,
  createRowPermissionApi,
  deleteColumnPermissionApi,
  deletePermissionWhitelistApi,
  deleteRowPermissionApi,
  listColumnPermissionApi,
  listPermissionWhitelistApi,
  listRowPermissionApi,
  busiTargetPerSaveApi,
  menuTargetPerApi,
  queryUserApi,
  queryUserOptionsApi,
  resourceTreeApi
} from '../auth'

describe('API: auth', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('queryUserApi posts the current org filter payload', async () => {
    const payload = { keyword: 'alice' }
    const response = { data: { rows: [{ id: 1 }] } }
    mockRequest.post.mockResolvedValueOnce(response)

    const result = await queryUserApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/user/byCurOrg',
      data: payload
    })
    expect(result).toBe(response)
  })

  it('queryUserOptionsApi requests the org option list', async () => {
    await queryUserOptionsApi()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/user/org/option'
    })
  })

  it('resourceTreeApi appends the flag to the business resource path', async () => {
    await resourceTreeApi('dataset')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/auth/busiResource/dataset'
    })
  })

  it('menuTargetPerApi posts menu target permissions', async () => {
    const payload = { roleId: 8, authIds: ['menu-1'] }

    await menuTargetPerApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/auth/menuTargetPermission',
      data: payload
    })
  })

  it('busiTargetPerSaveApi posts saved business target permissions', async () => {
    const payload = { targetId: 3, permissions: ['read'] }

    await busiTargetPerSaveApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/auth/saveBusiTargetPer',
      data: payload
    })
  })

  it('row permission apis post the expected payloads', async () => {
    const createPayload = {
      datasetId: 9,
      targetType: 'user',
      targetId: 3,
      filterSql: "region = 'east'",
      enabled: true
    }

    await listRowPermissionApi({ datasetId: 9 })
    await createRowPermissionApi(createPayload)
    await deleteRowPermissionApi(15)

    expect(mockRequest.post).toHaveBeenNthCalledWith(1, {
      url: '/rowPermission/list',
      data: { datasetId: 9 }
    })
    expect(mockRequest.post).toHaveBeenNthCalledWith(2, {
      url: '/rowPermission/create',
      data: createPayload
    })
    expect(mockRequest.post).toHaveBeenNthCalledWith(3, {
      url: '/rowPermission/delete/15',
      data: {}
    })
  })

  it('column permission apis post the expected payloads', async () => {
    const createPayload = {
      datasetId: 9,
      fieldId: 11,
      targetType: 'role',
      targetId: 5,
      action: 'mask',
      maskStart: 3,
      maskEnd: 7,
      enabled: false
    }

    await listColumnPermissionApi({ datasetId: 9 })
    await createColumnPermissionApi(createPayload)
    await deleteColumnPermissionApi(16)

    expect(mockRequest.post).toHaveBeenNthCalledWith(1, {
      url: '/columnPermission/list',
      data: { datasetId: 9 }
    })
    expect(mockRequest.post).toHaveBeenNthCalledWith(2, {
      url: '/columnPermission/create',
      data: createPayload
    })
    expect(mockRequest.post).toHaveBeenNthCalledWith(3, {
      url: '/columnPermission/delete/16',
      data: {}
    })
  })

  it('permission whitelist apis post the expected payloads', async () => {
    const payload = { userId: 8, datasetId: 9, scope: 'both' }

    await listPermissionWhitelistApi()
    await createPermissionWhitelistApi(payload)
    await deletePermissionWhitelistApi(22)

    expect(mockRequest.post).toHaveBeenNthCalledWith(1, {
      url: '/permissionWhitelist/list',
      data: {}
    })
    expect(mockRequest.post).toHaveBeenNthCalledWith(2, {
      url: '/permissionWhitelist/create',
      data: payload
    })
    expect(mockRequest.post).toHaveBeenNthCalledWith(3, {
      url: '/permissionWhitelist/delete/22',
      data: {}
    })
  })
})
