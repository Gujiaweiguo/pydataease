import { describe, expect, it, vi } from 'vitest'

const { importXpackToolMock } = vi.hoisted(() => ({
  importXpackToolMock: vi.fn()
}))
vi.mock('@/components/plugin/src/ImportXpackTool', () => ({
  importXpackTool: importXpackToolMock
}))

import { securityConfig } from '../hmac'

describe('hmac securityConfig', () => {
  it('returns early for whitelisted path /xpackModel', async () => {
    const result = await securityConfig({}, '/xpackModel')
    expect(importXpackToolMock).not.toHaveBeenCalled()
    expect(result).toBeUndefined()
  })

  it('returns early for path containing /xpackModel substring', async () => {
    const result = await securityConfig({}, '/api/xpackModel/something')
    expect(importXpackToolMock).not.toHaveBeenCalled()
    expect(result).toBeUndefined()
  })

  it('calls importXpackTool for non-whitelisted paths', async () => {
    const mockMethod = vi.fn().mockResolvedValue('secured')
    importXpackToolMock.mockResolvedValue(mockMethod)
    const result = await securityConfig({ header: 'value' }, '/api/data')
    expect(importXpackToolMock).toHaveBeenCalledWith('securityConfig')
    expect(mockMethod).toHaveBeenCalledWith({ header: 'value' }, '/api/data')
    expect(result).toBe('secured')
  })

  it('returns undefined when importXpackTool returns null', async () => {
    importXpackToolMock.mockResolvedValue(null)
    const result = await securityConfig({}, '/api/test')
    expect(result).toBeUndefined()
  })

  it('returns undefined when importXpackTool throws', async () => {
    importXpackToolMock.mockRejectedValue(new Error('xpack not available'))
    const result = await securityConfig({}, '/api/test')
    expect(result).toBeUndefined()
  })
})
