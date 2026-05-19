import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import { create, defaultFont, deleteById, list, uploadFontFile } from '../font'

describe('API: font', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('list requests the font list with GET', async () => {
    await list()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/typeface/listFont'
    })
  })

  it('create posts the new font payload', async () => {
    const payload = { name: 'Inter', fileName: 'inter.ttf' }

    await create(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/typeface/create',
      data: payload
    })
  })

  it('deleteById posts an empty body to the delete endpoint', async () => {
    await deleteById('font-1')

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/typeface/delete/font-1',
      data: {}
    })
  })

  it('defaultFont fetches the default font with GET', async () => {
    await defaultFont()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/typeface/defaultFont'
    })
  })

  it('uploadFontFile posts multipart uploads with loading enabled', async () => {
    const payload = new FormData()
    payload.append('file', new Blob(['font']), 'inter.ttf')

    await uploadFontFile(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/typeface/uploadFile',
      data: payload,
      loading: true,
      headersType: 'multipart/form-data;'
    })
  })
})
