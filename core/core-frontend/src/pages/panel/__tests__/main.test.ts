import { describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('@/config/axios', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: {} }),
    post: vi.fn().mockResolvedValue({ data: {} })
  }
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn()
}))

vi.mock('@/utils/propTypes', () => ({
  propTypes: {
    string: {
      def: vi.fn().mockReturnValue({ type: String, default: 'Iframe' })
    }
  }
}))

// Import the module under test — main.ts has side effects (sets window.DataEaseBi)
import '../main'

describe('panel/main.ts', () => {
  it('exposes DataEaseBi on window object', () => {
    expect((window as any).DataEaseBi).toBeDefined()
  })

  it('DataEaseBi is a constructor function', () => {
    const DataEaseBi = (window as any).DataEaseBi
    expect(typeof DataEaseBi).toBe('function')
  })

  it('DataEaseBi instance has expected properties', () => {
    const DataEaseBi = (window as any).DataEaseBi
    const instance = new DataEaseBi('Dashboard', {
      token: 'test-token',
      busiFlag: 'dashboard',
      outerParams: '',
      suffixId: 's1',
      baseUrl: 'http://localhost',
      dvId: 'dv1',
      pid: 'p1',
      chartId: 'c1',
      resourceId: 'r1',
      dfId: 'df1'
    })
    expect(instance.type).toBe('Dashboard')
    expect(instance.token).toBe('test-token')
    expect(instance.busiFlag).toBe('dashboard')
    expect(instance.baseUrl).toBe('http://localhost')
    expect(instance.dvId).toBe('dv1')
    expect(instance.pid).toBe('p1')
    expect(instance.chartId).toBe('c1')
    expect(instance.resourceId).toBe('r1')
    expect(instance.dfId).toBe('df1')
  })

  it('DataEaseBi has initialize method', () => {
    const DataEaseBi = (window as any).DataEaseBi
    const instance = new DataEaseBi('Dashboard', {
      token: 't',
      busiFlag: 'dashboard',
      outerParams: '',
      suffixId: '',
      baseUrl: '',
      dvId: '',
      pid: '',
      chartId: '',
      resourceId: '',
      dfId: ''
    })
    expect(typeof instance.initialize).toBe('function')
  })

  it('DataEaseBi has destroy method', () => {
    const DataEaseBi = (window as any).DataEaseBi
    const instance = new DataEaseBi('Dashboard', {
      token: 't',
      busiFlag: 'dashboard',
      outerParams: '',
      suffixId: '',
      baseUrl: '',
      dvId: '',
      pid: '',
      chartId: '',
      resourceId: '',
      dfId: ''
    })
    expect(typeof instance.destroy).toBe('function')
  })
})
