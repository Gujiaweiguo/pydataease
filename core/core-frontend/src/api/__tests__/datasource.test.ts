import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest, nameTrim } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  },
  nameTrim: vi.fn()
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))
vi.mock('@/utils/utils', () => ({ nameTrim }))

import { createFolder, getDatasetTree, listDatasources, save, uploadFile } from '../datasource'

describe('API: datasource', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('listDatasources always adds the datasource business flag', async () => {
    await listDatasources({ keyword: 'mysql' })

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/datasource/tree',
      data: { keyword: 'mysql', busiFlag: 'datasource' }
    })
  })

  it('save trims the payload before posting to the save endpoint', async () => {
    const payload = { name: '  Demo DS  ', type: 'mysql' }

    await save(payload)

    expect(nameTrim).toHaveBeenCalledWith(payload)
    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/datasource/save',
      data: payload
    })
  })

  it('createFolder trims the folder name before posting', async () => {
    const payload = { name: '  Folder  ' }

    await createFolder(payload)

    expect(nameTrim).toHaveBeenCalledWith(payload)
    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/datasource/createFolder',
      data: payload
    })
  })

  it('getDatasetTree posts dataset tree filters with a forced dataset flag', async () => {
    await getDatasetTree({ pid: 'root' })

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/datasetTree/tree',
      data: { pid: 'root', busiFlag: 'dataset' }
    })
  })

  it('uploadFile posts multipart form uploads with loading enabled', async () => {
    const payload = new FormData()
    payload.append('file', new Blob(['demo']), 'demo.xlsx')

    await uploadFile(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/datasource/uploadFile',
      data: payload,
      loading: true,
      headersType: 'multipart/form-data;'
    })
  })
})
