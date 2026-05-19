import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest, guid, error } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  },
  guid: vi.fn(() => 'file-guid'),
  error: vi.fn()
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))
vi.mock('@/views/visualized/data/dataset/form/util.js', () => ({ guid }))
vi.mock('element-plus-secondary', () => ({ ElMessage: { error } }))

import {
  beforeUploadCheck,
  findResourceAsBase64,
  uploadFile,
  uploadFileResult
} from '../staticResource'

describe('API: staticResource', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('uploadFile posts multipart image uploads with loading enabled', async () => {
    const payload = new FormData()
    payload.append('file', new Blob(['demo']), 'demo.png')

    await uploadFile('123', payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/staticResource/upload/123',
      headersType: 'multipart/form-data',
      loading: true,
      data: payload
    })
  })

  it('beforeUploadCheck rejects non-image files and shows an error', () => {
    const result = beforeUploadCheck({ type: 'text/plain', size: 1024 })

    expect(result).toBe(false)
    expect(error).toHaveBeenCalledWith('请上传图片')
  })

  it('beforeUploadCheck rejects images larger than 15MB and shows an error', () => {
    const result = beforeUploadCheck({ type: 'image/png', size: 16 * 1024 * 1024 })

    expect(result).toBe(false)
    expect(error).toHaveBeenCalledWith('图片大小不能超过15M')
  })

  it('beforeUploadCheck accepts valid image files', () => {
    const result = beforeUploadCheck({ type: 'image/png', size: 5 * 1024 * 1024 })

    expect(result).toBe(true)
    expect(error).not.toHaveBeenCalled()
  })

  it('uploadFileResult uploads with a generated file id and returns the static url', async () => {
    const callback = vi.fn()
    const file = new File(['binary'], 'avatar.png', { type: 'image/png' })

    await uploadFileResult(file, callback)

    expect(guid).toHaveBeenCalled()
    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/staticResource/upload/file-guid',
      headersType: 'multipart/form-data',
      loading: true,
      data: expect.any(FormData)
    })
    expect(callback).toHaveBeenCalledWith('/static-resource/file-guid.png', null)
  })

  it('uploadFileResult forwards upload failures to the callback', async () => {
    const uploadError = new Error('network failed')
    const callback = vi.fn()
    const file = new File(['binary'], 'avatar.jpg', { type: 'image/jpeg' })
    mockRequest.post.mockRejectedValueOnce(uploadError)

    await uploadFileResult(file, callback)

    expect(callback).toHaveBeenCalledWith(null, uploadError)
  })

  it('findResourceAsBase64 posts the lookup payload', async () => {
    const payload = { url: '/static-resource/file-guid.png' }

    await findResourceAsBase64(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/staticResource/findResourceAsBase64',
      data: payload
    })
  })
})
