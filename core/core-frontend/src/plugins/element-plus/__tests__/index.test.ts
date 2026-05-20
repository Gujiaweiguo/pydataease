import { describe, it, expect, vi } from 'vitest'

vi.mock('element-plus-secondary', () => ({
  ElLoading: { install: vi.fn() },
  ElScrollbar: { name: 'ElScrollbar' },
  ElConfigProvider: { locale: null }
}))

vi.mock('@element-plus/icons-vue', () => ({
  Edit: { name: 'Edit' },
  Delete: { name: 'Delete' }
}))

vi.mock('element-plus-secondary/theme-chalk/el-radio-button.css', () => ({}))

import { setupElementPlus, setupElementPlusIcons, setElementPlusLocale } from '../index'

describe('element-plus plugin', () => {
  it('should export setupElementPlus as a function', () => {
    expect(typeof setupElementPlus).toBe('function')
  })

  it('should export setupElementPlusIcons as a function', () => {
    expect(typeof setupElementPlusIcons).toBe('function')
  })

  it('should export setElementPlusLocale as a function', () => {
    expect(typeof setElementPlusLocale).toBe('function')
  })

  it('setupElementPlus should register plugins and components on app', () => {
    const app = {
      use: vi.fn(),
      component: vi.fn()
    }
    setupElementPlus(app as any)
    expect(app.use).toHaveBeenCalledTimes(1)
    expect(app.component).toHaveBeenCalledTimes(1)
  })

  it('setupElementPlusIcons should register all icon components', () => {
    const app = {
      component: vi.fn()
    }
    setupElementPlusIcons(app as any)
    expect(app.component).toHaveBeenCalled()
  })

  it('setElementPlusLocale should set locale on ElConfigProvider', async () => {
    const localeObj = { name: 'en' }
    setElementPlusLocale(localeObj)
    const { ElConfigProvider } = await import('element-plus-secondary')
    expect(ElConfigProvider.locale).toBe(localeObj)
  })
})
