import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import { load, loadDistributed, loadPluginApi, xpackModelApi } from '../plugin'

describe('API: plugin', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
  })

  it('load gets xpack component content by key', async () => {
    await load('component-key')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/xpackComponent/content/component-key'
    })
  })

  it('loadPluginApi gets plugin content by key', async () => {
    await loadPluginApi('plugin-key')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/xpackComponent/contentPlugin/plugin-key'
    })
  })

  it('loadDistributed gets the distributed xpack bundle', async () => {
    await loadDistributed()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/DEXPack.umd.js'
    })
  })

  it('xpackModelApi gets the xpack model descriptor', async () => {
    await xpackModelApi()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/xpackModel'
    })
  })
})
