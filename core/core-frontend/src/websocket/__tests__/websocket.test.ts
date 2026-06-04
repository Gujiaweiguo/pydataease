import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const cacheState = new Map<string, unknown>()
const emit = vi.fn()
const wsInstances: MockWebSocket[] = []

class MockWebSocket {
  static readonly CLOSED = 3
  static readonly CLOSING = 2
  static readonly CONNECTING = 0
  static readonly OPEN = 1

  readyState = MockWebSocket.CONNECTING
  onopen: (() => void) | null = null
  onmessage: ((ev: MessageEvent) => void) | null = null
  onclose: (() => void) | null = null
  onerror: (() => void) | null = null
  sent: string[] = []

  constructor(public url: string) {
    wsInstances.push(this)
  }

  send(data: string) {
    this.sent.push(data)
  }

  close() {
    this.readyState = MockWebSocket.CLOSED
  }

  simulateOpen() {
    this.readyState = MockWebSocket.OPEN
    this.onopen?.()
  }

  simulateMessage(data: string) {
    this.onmessage?.({ data } as MessageEvent)
  }

  simulateClose() {
    this.readyState = MockWebSocket.CLOSED
    this.onclose?.()
  }

  simulateError() {
    this.onerror?.()
  }
}

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: {
      get: vi.fn((key: string) => cacheState.get(key))
    }
  })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({
    emitter: {
      emit
    }
  })
}))

const connectedFrame = 'CONNECTED\nversion:1.2\nsession:test-session\n\n\x00'

async function loadModule() {
  return import('../index')
}

describe('WebSocket module', () => {
  beforeEach(() => {
    vi.resetModules()
    vi.clearAllMocks()
    vi.useRealTimers()
    vi.stubGlobal('WebSocket', MockWebSocket)
    vi.stubEnv('MODE', 'dev')
    vi.stubEnv('VITE_API_BASEPATH', '/api')
    wsInstances.length = 0
    cacheState.clear()
    cacheState.set('app.desktop', false)
    cacheState.set('user.token', 'test-token')
    cacheState.set('user.uid', 'test-uid')
    emit.mockReset()
    window.DataEaseBi = undefined
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
    vi.unstubAllEnvs()
  })

  it('buildFrame produces a STOMP frame', async () => {
    const { buildFrame } = await loadModule()

    expect(
      buildFrame('CONNECT', {
        'accept-version': '1.2',
        'heart-beat': '30000,0'
      })
    ).toBe('CONNECT\naccept-version:1.2\nheart-beat:30000,0\n\n\x00')
  })

  it('parseFrames handles multiple frames, empty bodies, and header values with colons', async () => {
    const { parseFrames } = await loadModule()
    const frames = parseFrames(
      'MESSAGE\ndestination:/user/test-uid/task-export-topic\ncontent-type:text/plain\n\npayload\x00' +
        'RECEIPT\nreceipt-id:disconnect:0\n\n\x00' +
        'CONNECTED\nversion:1.2\nsession:test:session\n\n\x00'
    )

    expect(frames).toEqual([
      {
        command: 'MESSAGE',
        headers: {
          destination: '/user/test-uid/task-export-topic',
          'content-type': 'text/plain'
        },
        body: 'payload'
      },
      {
        command: 'RECEIPT',
        headers: {
          'receipt-id': 'disconnect:0'
        },
        body: ''
      },
      {
        command: 'CONNECTED',
        headers: {
          version: '1.2',
          session: 'test:session'
        },
        body: ''
      }
    ])
  })

  it('install creates WebSocket with the dev proxy URL and sends CONNECT on open', async () => {
    const websocketModule = await loadModule()

    websocketModule.default.install()

    expect(wsInstances).toHaveLength(1)
    expect(wsInstances[0]?.url).toBe('ws://localhost:8100/websocket?userId=test-uid')

    wsInstances[0]?.simulateOpen()

    expect(wsInstances[0]?.sent).toEqual([
      'CONNECT\naccept-version:1.2\nheart-beat:30000,0\n\n\x00'
    ])
  })

  it('CONNECTED response triggers subscriptions for both channels', async () => {
    const websocketModule = await loadModule()

    websocketModule.default.install()
    wsInstances[0]?.simulateOpen()
    wsInstances[0]?.simulateMessage(connectedFrame)

    expect(wsInstances[0]?.sent).toEqual([
      'CONNECT\naccept-version:1.2\nheart-beat:30000,0\n\n\x00',
      'SUBSCRIBE\nid:sub-0\ndestination:/user/test-uid/task-export-topic\n\n\x00',
      'SUBSCRIBE\nid:sub-1\ndestination:/user/test-uid/report-notice\n\n\x00'
    ])
  })

  it('MESSAGE frames emit task export events', async () => {
    const websocketModule = await loadModule()

    websocketModule.default.install()
    wsInstances[0]?.simulateMessage(
      'MESSAGE\ndestination:/user/test-uid/task-export-topic\ncontent-type:application/json\n\n{"status":"done"}\x00'
    )

    expect(emit).toHaveBeenCalledWith('task-export-topic-call', '{"status":"done"}')
  })

  it('MESSAGE frames emit report notice events', async () => {
    const websocketModule = await loadModule()

    websocketModule.default.install()
    wsInstances[0]?.simulateMessage(
      'MESSAGE\ndestination:/user/test-uid/report-notice\n\nnotice\x00'
    )

    expect(emit).toHaveBeenCalledWith('report-notice-call', 'notice')
  })

  it('destroy sends DISCONNECT and closes the socket', async () => {
    const websocketModule = await loadModule()

    websocketModule.default.install()
    wsInstances[0]?.simulateOpen()
    websocketModule.destroy()

    expect(wsInstances[0]?.sent.at(-1)).toBe('DISCONNECT\nreceipt:disconnect-0\n\n\x00')
    expect(wsInstances[0]?.readyState).toBe(MockWebSocket.CLOSED)
  })

  it('destroy clears timers and prevents future reconnection', async () => {
    vi.useFakeTimers()
    const websocketModule = await loadModule()

    websocketModule.default.install()
    wsInstances[0]?.simulateOpen()
    wsInstances[0]?.simulateMessage(connectedFrame)
    wsInstances[0]?.simulateClose()

    websocketModule.destroy()
    vi.advanceTimersByTime(120000)

    expect(wsInstances).toHaveLength(1)
    expect(wsInstances[0]?.sent.includes('\n')).toBe(false)
  })

  it('uses exponential backoff and resets after a successful CONNECTED frame', async () => {
    vi.useFakeTimers()
    const websocketModule = await loadModule()

    websocketModule.default.install()
    wsInstances[0]?.simulateClose()

    vi.advanceTimersByTime(4999)
    expect(wsInstances).toHaveLength(1)

    vi.advanceTimersByTime(1)
    expect(wsInstances).toHaveLength(2)

    wsInstances[1]?.simulateClose()

    vi.advanceTimersByTime(9999)
    expect(wsInstances).toHaveLength(2)

    vi.advanceTimersByTime(1)
    expect(wsInstances).toHaveLength(3)

    wsInstances[2]?.simulateOpen()
    wsInstances[2]?.simulateMessage(connectedFrame)
    wsInstances[2]?.simulateClose()

    vi.advanceTimersByTime(4999)
    expect(wsInstances).toHaveLength(3)

    vi.advanceTimersByTime(1)
    expect(wsInstances).toHaveLength(4)
  })

  it('starts heartbeat after CONNECTED and stops it on close', async () => {
    vi.useFakeTimers()
    const websocketModule = await loadModule()

    websocketModule.default.install()
    wsInstances[0]?.simulateOpen()
    wsInstances[0]?.simulateMessage(connectedFrame)

    vi.advanceTimersByTime(30000)
    vi.advanceTimersByTime(30000)

    expect(wsInstances[0]?.sent.filter(message => message === '\n')).toHaveLength(2)

    wsInstances[0]?.simulateClose()
    vi.advanceTimersByTime(60000)

    expect(wsInstances[0]?.sent.filter(message => message === '\n')).toHaveLength(2)
  })

  it('does not connect when login status is false', async () => {
    cacheState.set('user.token', undefined)
    cacheState.set('user.uid', undefined)

    const websocketModule = await loadModule()
    websocketModule.default.install()

    expect(wsInstances).toHaveLength(0)
  })
})
