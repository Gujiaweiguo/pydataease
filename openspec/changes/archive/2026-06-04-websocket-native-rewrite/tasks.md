## 1. STOMP Frame Utilities

- [x] 1.1 Implement `buildFrame(command, headers, body)` — serialize STOMP frame to string with `\x00` terminator
- [x] 1.2 Implement `parseFrames(data)` — split received WebSocket data on `\x00`, parse each into `{ command, headers, body }` objects
- [x] 1.3 Unit tests for frame utilities: valid frames, multi-frame messages, empty body, headers with colons in values

## 2. WebSocket Connection Lifecycle

- [x] 2.1 Implement `buildWebSocketUrl()` — resolve WS URL from page origin, handling `window.DataEaseBi?.baseUrl` override and dev mode proxy target, converting `http(s)://` to `ws(s)://`
- [x] 2.2 Implement `connect()` — create `new WebSocket(url)`, attach `onopen`/`onmessage`/`onclose`/`onerror` handlers
- [x] 2.3 Implement `onOpen` handler — send STOMP `CONNECT` frame with `accept-version:1.2` and `heart-beat:30000,0`
- [x] 2.4 Implement `onMessage` handler — parse incoming STOMP frames, handle `CONNECTED` (trigger subscriptions), `MESSAGE` (emit events via mitt), `RECEIPT`, and `ERROR` frames
- [x] 2.5 Implement `onClose` handler — schedule reconnection with exponential backoff if not destroyed
- [x] 2.6 Implement `onError` handler — silent, delegate to `onClose` for reconnect scheduling

## 3. Subscriptions

- [x] 3.1 Define channel config (same two channels: `/task-export-topic` → `task-export-topic-call`, `/report-notice` → `report-notice-call`)
- [x] 3.2 Implement `subscribeAll()` — send STOMP `SUBSCRIBE` frames for all channels after receiving `CONNECTED`

## 4. Heartbeat

- [x] 4.1 Implement `startHeartbeat()` — send `\n` every 30 seconds while connected
- [x] 4.2 Implement `stopHeartbeat()` — clear heartbeat timer

## 5. Reconnection with Exponential Backoff

- [x] 5.1 Implement backoff constants: `BASE_DELAY=5000`, `MAX_DELAY=60000`, `MULTIPLIER=2`
- [x] 5.2 Implement `scheduleReconnect()` — `setTimeout` with current delay, double on each failure, cap at `MAX_DELAY`
- [x] 5.3 Implement `resetReconnectDelay()` — reset to `BASE_DELAY` on successful `CONNECTED` frame

## 6. Lifecycle Management

- [x] 6.1 Implement `disconnect()` — send STOMP `DISCONNECT` frame with receipt, close WebSocket, stop heartbeat
- [x] 6.2 Implement `destroy()` — set `destroyed=true`, clear reconnect timer, stop heartbeat, disconnect, prevent all future reconnection
- [x] 6.3 Export `destroy` function alongside the Vue plugin default export
- [x] 6.4 Implement login status check (`isLoginStatus()`) — same logic as current: check `app.desktop` or `user.token` + `user.uid` in cache

## 7. Vue Plugin Interface

- [x] 7.1 Implement `install()` method — call `connect()` if logged in, preserving the same plugin interface
- [x] 7.2 Verify no import of `sockjs-client` or `stompjs` in the new module

## 8. Unit Tests

- [x] 8.1 Test: `buildFrame` produces correct STOMP frame string
- [x] 8.2 Test: `parseFrames` splits multi-frame data and parses headers/body
- [x] 8.3 Test: `connect` creates WebSocket with correct URL and sends CONNECT on open
- [x] 8.4 Test: `CONNECTED` response triggers SUBSCRIBE frames for all channels
- [x] 8.5 Test: `MESSAGE` frames emit events via useEmitt with correct event names
- [x] 8.6 Test: `disconnect` sends STOMP DISCONNECT frame and closes WebSocket
- [x] 8.7 Test: `destroy` clears all timers and prevents future reconnection
- [x] 8.8 Test: exponential backoff increases delay on consecutive failures, resets on success
- [x] 8.9 Test: heartbeat sends `\n` at 30-second intervals, stops on disconnect
- [x] 8.10 Test: `isLoginStatus` returns false when no token/uid in cache

## 9. Verification

- [x] 9.1 Run `npm run ts:check` — zero new errors
- [x] 9.2 Run `npm run lint` — zero new errors on changed files
- [x] 9.3 Run `npx vitest run src/websocket/__tests__/` — all tests pass
- [x] 9.4 Manual QA: start dev frontend + backend, open browser console, confirm zero WebSocket-related console noise
