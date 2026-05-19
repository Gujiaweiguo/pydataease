import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import {
  deleteCustomGeoArea,
  deleteCustomGeoSubArea,
  getCustomGeoArea,
  getGeoJson,
  getWorldTree,
  listCustomGeoArea,
  listSubAreaOptions,
  saveCustomGeoArea,
  saveCustomGeoSubArea
} from '../map'

describe('API: map', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
    mockRequest.delete.mockResolvedValue({ data: {} })
  })

  it('getWorldTree gets the world map tree', async () => {
    await getWorldTree()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/map/worldTree'
    })
  })

  it('getGeoJson uses the map prefix for built-in china areas', async () => {
    await getGeoJson('156100')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/map/156/156100.json'
    })
  })

  it('getGeoJson uses the geo prefix for non-china custom geo areas', async () => {
    await getGeoJson('geo_840001')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/geo/840/840001.json'
    })
  })

  it('getGeoJson keeps custom china geo areas on the map prefix', async () => {
    await getGeoJson('geo_156999')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/map/156/156999.json'
    })
  })

  it('listCustomGeoArea gets all custom geo areas', async () => {
    await listCustomGeoArea()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/customGeo/geoArea/list'
    })
  })

  it('getCustomGeoArea gets a specific geo area by id', async () => {
    await getCustomGeoArea('area-1')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/customGeo/geoArea/area-1'
    })
  })

  it('deleteCustomGeoArea deletes a custom geo area by id', async () => {
    await deleteCustomGeoArea('area-2')

    expect(mockRequest.delete).toHaveBeenCalledWith({
      url: '/customGeo/geoArea/area-2'
    })
  })

  it('saveCustomGeoArea posts the geo area payload', async () => {
    const payload = { id: 'area-3', name: 'North Region' }

    await saveCustomGeoArea(payload as any)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/customGeo/geoArea/save',
      data: payload
    })
  })

  it('deleteCustomGeoSubArea deletes a custom geo sub-area by id', async () => {
    await deleteCustomGeoSubArea('sub-1')

    expect(mockRequest.delete).toHaveBeenCalledWith({
      url: '/customGeo/geoSubArea/sub-1'
    })
  })

  it('saveCustomGeoSubArea posts the sub-area payload', async () => {
    const payload = { id: 'sub-2', name: 'East Segment' }

    await saveCustomGeoSubArea(payload as any)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/customGeo/geoSubArea/save',
      data: payload
    })
  })

  it('listSubAreaOptions gets geo sub-area options', async () => {
    await listSubAreaOptions()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/customGeo/geoSubArea/options'
    })
  })
})
