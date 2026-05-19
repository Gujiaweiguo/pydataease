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
  clearErrorApi,
  downErrorRecordApi,
  downExcelTemplateApi,
  importUserApi,
  mountedOrg,
  switchOrg
} from '../user'

describe('API: user', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('mountedOrg posts the keyword inside the request body', async () => {
    await mountedOrg('finance')

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/org/mounted',
      data: { keyword: 'finance' }
    })
  })

  it('switchOrg posts to the selected organization endpoint', async () => {
    await switchOrg(42)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/user/switch/42'
    })
  })

  it('downExcelTemplateApi requests the import template as a blob', async () => {
    await downExcelTemplateApi()

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/user/excelTemplate',
      responseType: 'blob'
    })
  })

  it('importUserApi posts multipart form data to batch import', async () => {
    const payload = new FormData()
    payload.append('file', new Blob(['csv-data']), 'users.csv')

    await importUserApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/user/batchImport',
      headersType: 'multipart/form-data',
      data: payload
    })
  })

  it('downErrorRecordApi fetches the import error record as a blob', async () => {
    await downErrorRecordApi('job-1')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/user/errorRecord/job-1',
      responseType: 'blob'
    })
  })

  it('clearErrorApi triggers the clear endpoint without returning a promise', () => {
    const result = clearErrorApi('job-1')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/user/clearErrorRecord/job-1'
    })
    expect(result).toBeUndefined()
  })
})
