import { describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store', () => ({ store: {} }))

vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  storeToRefs: vi.fn(() => ({})),
  createPinia: vi.fn()
}))

import { withInstall, SFCWithInstall } from '@/pages/lib/install'

describe('install.ts', () => {
  it('withInstall adds install method', () => {
    const mockComponent = { name: 'TestComponent' } as any
    const result = withInstall(mockComponent)
    expect(typeof result.install).toBe('function')
  })

  it('withInstall preserves component name', () => {
    const mockComponent = { name: 'TestComponent' } as any
    const result = withInstall(mockComponent)
    expect(result.name).toBe('TestComponent')
  })

  it('withInstall handles extra components', () => {
    const mockComponent = { name: 'Main' } as any
    const extra = { SubComp: { name: 'SubComp' } }
    const result = withInstall(mockComponent, extra)
    expect((result as any).SubComp).toBeDefined()
  })

  it('install function registers components', () => {
    const mockComponent = { name: 'TestComponent' } as any
    const result = withInstall(mockComponent)
    const mockApp = { component: vi.fn() }
    result.install(mockApp as any)
    expect(mockApp.component).toHaveBeenCalledWith('TestComponent', mockComponent)
  })
})
