import { describe, expect, it, vi } from 'vitest'

vi.mock('tinymce/tinymce', () => ({
  default: {
    PluginManager: {
      get: vi.fn(() => undefined),
      add: vi.fn()
    },
    IconManager: {
      has: vi.fn(() => false),
      add: vi.fn()
    }
  }
}))
vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({
    emitter: {
      on: vi.fn(),
      off: vi.fn(),
      emit: vi.fn()
    }
  })
}))

describe('rich-text/plugins/vertical-content.ts', () => {
  it('exports a default object with name and plugin', async () => {
    const mod = await import('../vertical-content')
    const verticalContent = mod.default
    expect(verticalContent).toBeDefined()
    expect(verticalContent.name).toBe('vertical-content')
    expect(typeof verticalContent.plugin).toBe('function')
  })

  it('plugin function returns getMetadata', async () => {
    const mod = await import('../vertical-content')
    const verticalContent = mod.default
    const mockEditor = {
      targetElm: { id: 'test-editor' },
      settings: { vertical_align: 'top-align' },
      ui: {
        registry: {
          addToggleButton: vi.fn((_key, config) => {
            const mockApi = { isActive: vi.fn(() => false), setActive: vi.fn() }
            if (config.onSetup) {
              config.onSetup(mockApi)
            }
          })
        }
      }
    } as any
    const result = verticalContent.plugin(mockEditor)
    expect(result).toBeDefined()
    expect(result.getMetadata).toBeDefined()
    expect(typeof result.getMetadata).toBe('function')
  })

  it('getMetadata returns name and url', async () => {
    const mod = await import('../vertical-content')
    const verticalContent = mod.default
    const mockEditor = {
      targetElm: { id: 'test-editor' },
      settings: {},
      ui: {
        registry: {
          addToggleButton: vi.fn()
        }
      }
    } as any
    const result = verticalContent.plugin(mockEditor)
    const metadata = result.getMetadata()
    expect(metadata.name).toBe('Vertical align')
    expect(metadata.url).toBe('https://dataease.io')
  })

  it('registers three toggle buttons', async () => {
    const mod = await import('../vertical-content')
    const verticalContent = mod.default
    const addToggleButton = vi.fn()
    const mockEditor = {
      targetElm: { id: 'test-editor' },
      settings: {},
      ui: {
        registry: {
          addToggleButton
        }
      }
    } as any
    verticalContent.plugin(mockEditor)
    expect(addToggleButton).toHaveBeenCalledTimes(3)
    expect(addToggleButton).toHaveBeenCalledWith('top-align', expect.any(Object))
    expect(addToggleButton).toHaveBeenCalledWith('center-align', expect.any(Object))
    expect(addToggleButton).toHaveBeenCalledWith('bottom-align', expect.any(Object))
  })
})
