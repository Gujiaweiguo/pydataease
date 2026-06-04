## Why

The frontend WebSocket module (`src/websocket/index.ts`) uses deprecated `sockjs-client@1.6.1` and `stompjs@2.3.3` to connect to the backend STOMP-over-WebSocket endpoint. These packages are unmaintained, and the current implementation has a critical design flaw: a 5-second `setInterval` polling loop that is never cleared (`clearInterval` never called). In development mode where the Vite proxy drops long-lived WebSocket connections, this produces constant `console.error('连接失败')` and `console.info('断开连接')` noise — roughly one error per reconnection attempt every 5 seconds, flooding the browser console and masking real issues.

The backend already supports a direct STOMP-over-WebSocket endpoint at `/websocket` (no SockJS required), making the SockJS transport layer unnecessary.

## What Changes

- Replace `sockjs-client` + `stompjs` with native `WebSocket` and manual STOMP 1.2 frame serialization/deserialization
- Add exponential backoff reconnection (5s → 10s → 20s → 60s cap, reset on successful connect)
- Add `destroy()` lifecycle method that clears all timers and closes the socket — exportable for router/app-level cleanup
- Add STOMP heartbeat (`\n` ping) to keep connections alive through idle periods
- Remove all `console.error`, `console.info`, `console.warn` calls from the module (silent operation)
- Maintain identical plugin interface (`{ install() }`) and event names (`task-export-topic-call`, `report-notice-call`)
- Update unit tests for the new implementation

## Capabilities

### New Capabilities
- `native-websocket-client`: Frontend WebSocket client using native WebSocket API with STOMP 1.2 frame handling, exponential backoff reconnection, heartbeat, and clean lifecycle management.

### Modified Capabilities
- `stomp-websocket`: No requirement changes. The backend STOMP protocol spec remains unchanged; this change is purely frontend-side.

## Impact

**Frontend files:**
- `src/websocket/index.ts` — full rewrite (100 → ~200 lines)
- `src/websocket/__tests__/websocket.test.ts` — updated tests
- `src/pages/index/main.ts` — potentially add `destroy()` call on app unmount (optional)

**Dependencies removed (separate follow-up):**
- `sockjs-client@1.6.1`
- `stompjs@2.3.3`
- `@types/sockjs-client`
- `@types/stompjs`

**No backend changes** — the existing `/websocket` endpoint already handles direct STOMP-over-WebSocket.

**Gate layer:** L0 frontend (`npm run ts:check` + `npm run lint`). No routing or packaging changes, so no build gate required. The `stomp-websocket` spec already covers the backend contract we're connecting to.
