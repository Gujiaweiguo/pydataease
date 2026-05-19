import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import { getDefaultSettings, getRoleRouters } from '../common'

describe('API: common', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
  })

  it('getRoleRouters gets menu routes and unwraps the response data', async () => {
    const response = { data: [{ path: '/dashboard' }] }
    mockRequest.get.mockResolvedValueOnce(response)

    const result = await getRoleRouters()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/menu/query'
    })
    expect(result).toEqual(response.data)
  })

  it('getDefaultSettings gets the default system settings and unwraps the response data', async () => {
    const response = { data: { theme: 'dark' } }
    mockRequest.get.mockResolvedValueOnce(response)

    const result = await getDefaultSettings()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/sysParameter/defaultSettings'
    })
    expect(result).toEqual(response.data)
  })
})
