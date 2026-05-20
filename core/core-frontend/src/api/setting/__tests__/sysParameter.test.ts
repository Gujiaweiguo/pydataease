import { describe, it, expect, vi } from 'vitest'

const { mockGet, mockPost } = vi.hoisted(() => ({
  mockGet: vi.fn(() => Promise.resolve({ data: {} })),
  mockPost: vi.fn(() => Promise.resolve({ data: {} }))
}))

vi.mock('@/config/axios', () => ({
  default: { get: mockGet, post: mockPost }
}))

import * as api from '../sysParameter'

describe('sysParameter API', () => {
  it('queryMapKeyApi should call request.get with correct url', () => {
    api.queryMapKeyApi()
    expect(mockGet).toHaveBeenCalledWith({ url: '/sysParameter/queryOnlineMap' })
  })

  it('queryMapKeyApiByType should call request.get with type parameter', () => {
    api.queryMapKeyApiByType('gaode')
    expect(mockGet).toHaveBeenCalledWith({ url: '/sysParameter/queryOnlineMap/gaode' })
  })

  it('saveMapKeyApi should call request.post with data', () => {
    const data = { key: 'value' }
    api.saveMapKeyApi(data)
    expect(mockPost).toHaveBeenCalledWith({ url: '/sysParameter/saveOnlineMap', data })
  })
})
