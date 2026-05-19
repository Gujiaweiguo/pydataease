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
  batchDelApi,
  valueSelectedForVariableApi,
  variableCreateApi,
  variableDetailApi,
  variableValueDeletelApi,
  variableValueEditApi
} from '../variable'

describe('API: variable', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('variableCreateApi posts a new variable payload', async () => {
    const payload = { name: 'city', type: 'string' }

    await variableCreateApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sysVariable/create',
      data: payload
    })
  })

  it('variableDetailApi fetches a variable by id', async () => {
    await variableDetailApi(7)

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/sysVariable/detail/7'
    })
  })

  it('valueSelectedForVariableApi posts pagination params in the path', async () => {
    const payload = { keyword: '华东' }

    await valueSelectedForVariableApi(2, 20, payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sysVariable/value/selected/2/20',
      data: payload
    })
  })

  it('variableValueEditApi posts edited variable values', async () => {
    const payload = { id: 3, value: 'updated' }

    await variableValueEditApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sysVariable/value/edit',
      data: payload
    })
  })

  it('variableValueDeletelApi and batchDelApi target the value deletion endpoints', async () => {
    const batchPayload = { ids: [3, 4] }

    await variableValueDeletelApi(3)
    await batchDelApi(batchPayload)

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/sysVariable/value/delete/3'
    })
    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sysVariable/value/batchDel',
      data: batchPayload
    })
  })
})
