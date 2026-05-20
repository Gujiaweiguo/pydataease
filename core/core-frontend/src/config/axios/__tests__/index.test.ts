import { describe, expect, it, vi, beforeEach } from 'vitest'

const { serviceMock } = vi.hoisted(() => ({
  serviceMock: vi.fn()
}))
vi.mock('../service', () => ({
  service: serviceMock
}))

import request from '../index'

describe('axios index request', () => {
  beforeEach(() => {
    serviceMock.mockReset()
  })

  it('get method calls service with method get', () => {
    serviceMock.mockResolvedValue({ data: 'ok' })
    request.get({ url: '/test' })
    expect(serviceMock).toHaveBeenCalledWith(
      expect.objectContaining({
        url: '/test',
        method: 'get'
      })
    )
  })

  it('post method calls service with method post', () => {
    serviceMock.mockResolvedValue({ data: 'ok' })
    request.post({ url: '/api/data', data: { key: 'value' } })
    expect(serviceMock).toHaveBeenCalledWith(
      expect.objectContaining({
        url: '/api/data',
        method: 'post',
        data: { key: 'value' }
      })
    )
  })

  it('delete method calls service with method delete', () => {
    serviceMock.mockResolvedValue({ data: 'ok' })
    request.delete({ url: '/api/item/1' })
    expect(serviceMock).toHaveBeenCalledWith(
      expect.objectContaining({
        url: '/api/item/1',
        method: 'delete'
      })
    )
  })

  it('put method calls service with method put', () => {
    serviceMock.mockResolvedValue({ data: 'ok' })
    request.put({ url: '/api/item/1', data: { name: 'updated' } })
    expect(serviceMock).toHaveBeenCalledWith(
      expect.objectContaining({
        url: '/api/item/1',
        method: 'put',
        data: { name: 'updated' }
      })
    )
  })

  it('uses default Content-Type header when headersType not provided', () => {
    serviceMock.mockResolvedValue({})
    request.get({ url: '/test' })
    expect(serviceMock).toHaveBeenCalledWith(
      expect.objectContaining({
        headers: { 'Content-Type': 'application/json' }
      })
    )
  })

  it('uses custom Content-Type header when headersType provided', () => {
    serviceMock.mockResolvedValue({})
    request.post({ url: '/upload', headersType: 'multipart/form-data' })
    expect(serviceMock).toHaveBeenCalledWith(
      expect.objectContaining({
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    )
  })
})
