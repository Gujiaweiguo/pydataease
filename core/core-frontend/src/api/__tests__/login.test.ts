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

import { loginApi, logoutApi, platformLoginApi, queryDekey, refreshApi, uiLoadApi } from '../login'

describe('API: login', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('loginApi posts login credentials to the local login endpoint', async () => {
    const payload = { username: 'demo', password: 'secret' }

    await loginApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/login/localLogin',
      data: payload
    })
  })

  it('queryDekey requests the dekey endpoint with GET', async () => {
    await queryDekey()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: 'dekey'
    })
  })

  it('platformLoginApi posts to the platform origin endpoint', async () => {
    await platformLoginApi('wecom')

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/login/platformLogin/wecom'
    })
  })

  it('refreshApi forwards the refresh time as query params', async () => {
    await refreshApi(1717321024)

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/login/refresh',
      params: { time: 1717321024 }
    })
  })

  it('logoutApi and uiLoadApi hit their GET endpoints', async () => {
    await logoutApi()
    await uiLoadApi()

    expect(mockRequest.get).toHaveBeenNthCalledWith(1, {
      url: '/logout'
    })
    expect(mockRequest.get).toHaveBeenNthCalledWith(2, {
      url: '/sysParameter/ui'
    })
  })
})
