import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import { buildVersionApi, revertApi, updateInfoApi, validateApi } from '../about'

describe('API: about', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('validateApi posts the license validation payload', async () => {
    const payload = { license: 'encoded-license' }

    await validateApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/license/validate',
      data: payload
    })
  })

  it('buildVersionApi gets the current license version', async () => {
    await buildVersionApi()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/license/version'
    })
  })

  it('updateInfoApi posts license update data', async () => {
    const payload = { version: '2.0.0', notes: 'patched' }

    await updateInfoApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/license/update',
      data: payload
    })
  })

  it('revertApi posts to the license revert endpoint', async () => {
    await revertApi()

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/license/revert'
    })
  })
})
