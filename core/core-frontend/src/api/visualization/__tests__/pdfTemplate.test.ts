import { describe, expect, it, vi, beforeEach } from 'vitest'

const { requestMock } = vi.hoisted(() => ({
  requestMock: {
    get: vi.fn().mockResolvedValue({ data: [] })
  }
}))

vi.mock('@/config/axios', () => ({ default: requestMock }))

import { queryAll } from '../pdfTemplate'

describe('pdfTemplate API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('queryAll calls request.get with correct url and loading false', async () => {
    await queryAll()
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/pdf-template/queryAll',
      loading: false
    })
  })
})
