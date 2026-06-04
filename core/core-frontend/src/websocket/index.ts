import { useCache } from '@/hooks/web/useCache'
import { useEmitt } from '@/hooks/web/useEmitt'
import dev from '../../config/dev'

const { wsCache } = useCache()
const env = import.meta.env
const basePath = env.VITE_API_BASEPATH

const RECONNECT_BASE_DELAY = 5000
const RECONNECT_MAX_DELAY = 60000
const RECONNECT_MULTIPLIER = 2
const HEARTBEAT_INTERVAL = 30000

interface Channel {
  topic: string
  event: string
}

interface StompFrame {
  command: string
  headers: Record<string, string>
  body: string
}

const channels: Channel[] = [
  { topic: '/task-export-topic', event: 'task-export-topic-call' },
  { topic: '/report-notice', event: 'report-notice-call' }
]

let ws: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let heartbeatTimer: ReturnType<typeof setInterval> | null = null
let reconnectDelay = RECONNECT_BASE_DELAY
let destroyed = false

export function buildFrame(command: string, headers: Record<string, string>, body = ''): string {
  const lines = [command]

  for (const [key, value] of Object.entries(headers)) {
    lines.push(`${key}:${value}`)
  }

  lines.push('')
  lines.push(body)

  return lines.join('\n') + '\x00'
}

export function parseFrames(data: string): StompFrame[] {
  const results: StompFrame[] = []
  const rawFrames = data.split('\x00')

  for (const rawFrame of rawFrames) {
    const normalized = rawFrame.replace(/\r\n/g, '\n').replace(/^\n+/, '')

    if (!normalized.trim()) {
      continue
    }

    const lines = normalized.split('\n')
    const command = lines[0]?.trim()

    if (!command) {
      continue
    }

    const headers: Record<string, string> = {}
    let bodyIndex = lines.length

    for (let i = 1; i < lines.length; i++) {
      if (lines[i] === '') {
        bodyIndex = i + 1
        break
      }

      const colonIdx = lines[i].indexOf(':')
      if (colonIdx === -1) {
        continue
      }

      headers[lines[i].substring(0, colonIdx).trim()] = lines[i].substring(colonIdx + 1).trim()
    }

    const body = bodyIndex < lines.length ? lines.slice(bodyIndex).join('\n') : ''
    results.push({ command, headers, body })
  }

  return results
}

function buildWebSocketUrl(): string {
  let prefix: string

  if (window.DataEaseBi?.baseUrl) {
    prefix = window.DataEaseBi.baseUrl
  } else {
    prefix = location.origin + location.pathname

    if (env.MODE === 'dev') {
      prefix = dev.server.proxy[basePath as keyof typeof dev.server.proxy].target + '/'
    }
  }

  if (!prefix.endsWith('/')) {
    prefix += '/'
  }

  const wsUrl = prefix.replace(/^http/, 'ws')
  const userId = wsCache.get('app.desktop') ? 1 : wsCache.get('user.uid')

  return `${wsUrl}websocket?userId=${userId}`
}

function isLoginStatus(): boolean {
  if (wsCache.get('app.desktop')) {
    return true
  }

  return !!(wsCache.get('user.token') && wsCache.get('user.uid'))
}

function startHeartbeat(): void {
  stopHeartbeat()
  heartbeatTimer = setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send('\n')
    }
  }, HEARTBEAT_INTERVAL)
}

function stopHeartbeat(): void {
  if (heartbeatTimer !== null) {
    clearInterval(heartbeatTimer)
    heartbeatTimer = null
  }
}

function scheduleReconnect(): void {
  if (destroyed || !isLoginStatus() || reconnectTimer !== null) {
    return
  }

  reconnectTimer = setTimeout(() => {
    reconnectTimer = null
    connect()
  }, reconnectDelay)

  reconnectDelay = Math.min(reconnectDelay * RECONNECT_MULTIPLIER, RECONNECT_MAX_DELAY)
}

function resetReconnectDelay(): void {
  reconnectDelay = RECONNECT_BASE_DELAY
}

function subscribeAll(): void {
  const userId = wsCache.get('app.desktop') ? 1 : wsCache.get('user.uid')

  channels.forEach((channel, index) => {
    const frame = buildFrame('SUBSCRIBE', {
      id: `sub-${index}`,
      destination: `/user/${userId}${channel.topic}`
    })

    ws?.send(frame)
  })
}

function onOpen(): void {
  const connectFrame = buildFrame('CONNECT', {
    'accept-version': '1.2',
    'heart-beat': '30000,0'
  })

  ws?.send(connectFrame)
}

function onMessage(event: MessageEvent): void {
  const data = typeof event.data === 'string' ? event.data : ''

  if (!data || data.trim() === '') {
    return
  }

  const frames = parseFrames(data)

  for (const frame of frames) {
    switch (frame.command) {
      case 'CONNECTED':
        resetReconnectDelay()
        subscribeAll()
        startHeartbeat()
        break
      case 'MESSAGE': {
        const emitter = useEmitt().emitter
        const destination = frame.headers.destination || ''

        for (const channel of channels) {
          if (destination.endsWith(channel.topic)) {
            emitter.emit(channel.event, frame.body)
            break
          }
        }
        break
      }
      case 'RECEIPT':
      case 'ERROR':
        break
      default:
        break
    }
  }
}

function onClose(): void {
  stopHeartbeat()
  ws = null
  scheduleReconnect()
}

function onError(): void {
  return
}

function connect(): void {
  if (destroyed || !isLoginStatus()) {
    return
  }

  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return
  }

  ws = new WebSocket(buildWebSocketUrl())
  ws.onopen = onOpen
  ws.onmessage = onMessage
  ws.onclose = onClose
  ws.onerror = onError
}

function disconnect(): void {
  if (ws && ws.readyState === WebSocket.OPEN) {
    try {
      ws.send(buildFrame('DISCONNECT', { receipt: 'disconnect-0' }))
    } catch {
      // ignore close race
    }
  }

  stopHeartbeat()

  if (ws) {
    ws.onclose = null
    ws.close()
    ws = null
  }
}

function destroy(): void {
  destroyed = true

  if (reconnectTimer !== null) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }

  disconnect()
}

export default {
  install() {
    destroyed = false
    connect()
  }
}

export { destroy }
