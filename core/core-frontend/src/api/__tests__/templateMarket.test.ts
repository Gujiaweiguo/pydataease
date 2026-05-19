import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import {
  getCategories,
  getCategoriesObject,
  searchMarket,
  searchMarketPreview,
  searchMarketRecommend
} from '../templateMarket'

describe('API: templateMarket', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
  })

  it('searchMarket gets template market results', async () => {
    await searchMarket()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/templateMarket/search'
    })
  })

  it('searchMarketRecommend gets recommended templates', async () => {
    await searchMarketRecommend()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/templateMarket/searchRecommend'
    })
  })

  it('searchMarketPreview gets preview templates', async () => {
    await searchMarketPreview()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/templateMarket/searchPreview'
    })
  })

  it('getCategories gets template market categories', async () => {
    await getCategories()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/templateMarket/categories'
    })
  })

  it('getCategoriesObject gets the category object map', async () => {
    await getCategoriesObject()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/templateMarket/categoriesObject'
    })
  })
})
