## Context

The frontend WebSocket module at `src/websocket/index.ts` is a Vue plugin installed at app boot. It uses `sockjs-client@1.6.1` + `stompjs@2.3.3` (both deprecated) to connect to the backend's STOMP-over-WebSocket endpoint. The backend supports two transport paths:

1. **SockJS transport**: `/websocket/{server}/{session}/websocket` — requires SockJS framing (`o`, `a[...]`)
2. **Direct WebSocket**: `/websocket` — accepts raw STOMP 1.2 frames terminated by `\x00`

The direct path already exists and is fully functional. The frontend currently uses path 1, but path 2 is simpler and eliminates the SockJS dependency.

The current implementation has a critical flaw: `initialize()` starts a `setInterval(callback, 5000)` that polls connection status and auto-reconnects. This interval is **never cleared** — no `clearInterval`, no `destroy()` method. In dev mode where the Vite proxy drops long-lived WebSocket connections every ~30s, this produces constant `console.error('连接失败')` and `console.info('断开连接')` noise.

The module subscribes to two STOMP destinations:
- `/user/{userId}/task-export-topic` → emits `task-export-topic-call` via mitt event bus
- `/user/{userId}/report-notice` → emits `report-notice-call` via mitt event bus

Current consumers: `ExportExcel.vue` listens for `task-export-topic-call`. No confirmed consumer for `report-notice-call`.

## Goals / Non-Goals

**Goals:**
- Replace SockJS + stompjs with native WebSocket + manual STOMP 1.2 frame handling
- Add exponential backoff reconnection (5s → 10s → 20s → 60s cap)
- Add proper lifecycle: `destroy()` method that clears all timers and closes the socket
- Add STOMP heartbeat to keep connections alive
- Silent operation: zero console output in production code
- Maintain identical external interface (Vue plugin `{ install() }`, same event names)

**Non-Goals:**
- Changing the backend STOMP protocol or endpoint
- Adding new STOMP features (transactions, acknowledgments)
- Changing event names or subscription destinations
- Removing the `sockjs-client` / `stompjs` packages from `package.json` (separate follow-up)
- Adding authentication beyond the existing `userId` query parameter

## Decisions

### D1: Native WebSocket over SockJS

**Choice**: Use `new WebSocket(url)` directly.
**Alternative**: Upgrade to `@stomp/stompjs` v7 (still maintained, has SockJS support).
**Rationale**: The backend's direct `/websocket` endpoint already accepts raw STOMP frames. Adding `@stomp/stompjs` would introduce a new dependency when we can implement the ~50 lines of STOMP frame serialization ourselves. The STOMP subset needed is tiny: CONNECT, SUBSCRIBE, DISCONNECT, and MESSAGE parsing. No transactions, no ACK/NACK, no reliable receipt handling.

### D2: Manual STOMP frame parsing over a library

**Choice**: Hand-roll `buildFrame()` and `parseFrames()`.
**Alternative**: Use `@stomp/stompjs` for frame parsing.
**Rationale**: The STOMP frame format is trivially parseable (`COMMAND\nheader:value\n\nbody\x00`). The backend's `parse_frame()` in `stomp_handler.py` is 24 lines. The frontend equivalent is equally small. No need for a 100KB library.

### D3: Exponential backoff with jitter

**Choice**: `delay = min(base * 2^attempt, maxDelay)`, capped at 60s. No jitter for simplicity.
**Rationale**: Without backoff, a down server gets hammered every 5s. The 60s cap prevents excessively long waits. Jitter is nice-to-have but adds complexity for little benefit in a single-client scenario.

### D4: Heartbeat via STOMP protocol negotiation

**Choice**: Send `heart-beat:30000,0` in the CONNECT frame, then send `\n` every 30s.
**Rationale**: The backend's `_start_heartbeat()` already handles server-side heartbeat negotiation. The client-side heartbeat keeps the TCP connection alive through proxies and load balancers. 30s is conservative enough for Vite dev proxy (which drops at ~30s idle) and production reverse proxies.

### D5: Module-level singleton with exported destroy

**Choice**: Keep the current singleton pattern (module-level variables), export a `destroy()` function alongside the Vue plugin.
**Alternative**: Convert to a class instance or composable.
**Rationale**: The current code is a singleton. Converting to a class would change the installation pattern for no functional benefit. Adding `export function destroy()` is the minimal change needed for cleanup.

### D6: URL construction preserved from current logic

**Choice**: Reuse the existing URL resolution logic (handle `window.DataEaseBi?.baseUrl`, dev mode proxy target, etc.), converting HTTP to WS protocol.
**Rationale**: The URL construction has edge cases (embedded mode, dev proxy). Rewriting it risks breaking existing deployments.

## Risks / Trade-offs

- **[Risk] STOMP parsing bugs** → The hand-rolled parser must handle edge cases (multi-frame messages, empty bodies, header values with colons). Mitigation: comprehensive unit tests with real STOMP frame samples from the backend.
- **[Risk] Dev proxy WebSocket limitations** → Vite's proxy may still drop WebSocket connections. Mitigation: the exponential backoff will handle reconnection gracefully without console noise.
- **[Risk] Legacy SockJS consumers** → If any external or embedded code uses the SockJS transport path, it's unaffected (backend keeps both endpoints). The frontend just stops using it.
- **[Trade-off] Not removing packages yet** → `sockjs-client` and `stompjs` remain in `package.json` until a separate cleanup PR. This avoids bundle size regression (tree-shaking won't include unused imports) but keeps the declaration. Low risk.
