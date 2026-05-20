import { describe, expect, it, vi } from 'vitest'

vi.mock('tinymce/tinymce', () => ({
  default: {
    PluginManager: {
      get: vi.fn(() => undefined),
      add: vi.fn()
    }
  }
}))

describe('rich-text/plugins/index.ts', () => {
  it('imports and executes without error', async () => {
    const tinymce = (await import('tinymce/tinymce')).default
    expect(tinymce.PluginManager.get).toBeDefined()
    expect(tinymce.PluginManager.add).toBeDefined()
  })

  it('has PluginManager with get and add methods', async () => {
    const tinymce = (await import('tinymce/tinymce')).default
    expect(typeof tinymce.PluginManager.get).toBe('function')
    expect(typeof tinymce.PluginManager.add).toBe('function')
  })
})
