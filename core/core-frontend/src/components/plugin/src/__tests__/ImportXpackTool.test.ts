import { describe, it, expect, vi } from 'vitest'

vi.stubEnv('VITE_API_BASEPATH', './')

vi.mock('@/api/plugin', () => ({
  xpackModelApi: vi.fn(() => Promise.resolve({ data: null }))
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: {
      get: vi.fn(() => null),
      set: vi.fn()
    }
  })
}))

vi.mock('@/utils/utils', () => ({
  isNull: vi.fn((v: any) => v === null || v === undefined)
}))

vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({ baseUrl: '' })
}))

describe('ImportXpackTool', () => {
  it('importXpackTool returns null when distributed is null', async () => {
    const { importXpackTool } = await import('../ImportXpackTool')

    const result = await importXpackTool('testMethod')

    expect(result).toBeNull()
  })
})
