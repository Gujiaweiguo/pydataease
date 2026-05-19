import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('element-plus-secondary', () => ({
  ElLoading: { install: vi.fn(), name: 'ElLoading' },
  ElScrollbar: { name: 'ElScrollbar' },
  ElConfigProvider: { locale: null }
}))

vi.mock('@element-plus/icons-vue', () => ({
  Edit: { name: 'Edit' },
  Delete: { name: 'Delete' }
}))

describe('element-plus plugin', () => {
  let app: { use: ReturnType<typeof vi.fn>; component: ReturnType<typeof vi.fn> }

  beforeEach(() => {
    app = { use: vi.fn(), component: vi.fn() }
  })

  it('setupElementPlus should register plugins via app.use', async () => {
    const { setupElementPlus } = await import('../element-plus/index')
    setupElementPlus(app as any)
    expect(app.use).toHaveBeenCalledTimes(1)
  })

  it('setupElementPlus should register components via app.component', async () => {
    const { setupElementPlus } = await import('../element-plus/index')
    setupElementPlus(app as any)
    expect(app.component).toHaveBeenCalledWith('ElScrollbar', expect.anything())
  })

  it('setupElementPlusIcons should register all icons via app.component', async () => {
    const { setupElementPlusIcons } = await import('../element-plus/index')
    setupElementPlusIcons(app as any)
    expect(app.component).toHaveBeenCalledWith('Edit', expect.anything())
    expect(app.component).toHaveBeenCalledWith('Delete', expect.anything())
    expect(app.component).toHaveBeenCalledTimes(2)
  })

  it('setElementPlusLocale should set ElConfigProvider.locale', async () => {
    const { setElementPlusLocale } = await import('../element-plus/index')
    const mockModule = await import('element-plus-secondary')
    const localeObj = { el: { placeholder: 'Please select' } }
    setElementPlusLocale(localeObj)
    expect(mockModule.ElConfigProvider.locale).toBe(localeObj)
  })
})
