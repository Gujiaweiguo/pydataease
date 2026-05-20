import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: {
      get: vi.fn((key: string) => {
        if (key === 'app.desktop') return false
        if (key === 'user.token') return 'test-token'
        if (key === 'user.uid') return 'test-uid'
        return undefined
      })
    }
  })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({
    emitter: {
      emit: vi.fn()
    }
  })
}))

vi.mock('sockjs-client/dist/sockjs.min.js', () => ({
  default: vi.fn(function () {
    return {}
  })
}))

vi.mock('stompjs', () => ({
  default: {
    over: vi.fn(() => ({
      connect: vi.fn(),
      connected: false,
      disconnect: vi.fn(),
      subscribe: vi.fn()
    }))
  }
}))

describe('WebSocket module', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('exports default object with install method', async () => {
    const ws = await import('../index')
    expect(ws.default).toBeDefined()
    expect(typeof ws.default.install).toBe('function')
  })

  it('install does not throw', async () => {
    const ws = await import('../index')
    expect(() => ws.default.install()).not.toThrow()
  })
})
