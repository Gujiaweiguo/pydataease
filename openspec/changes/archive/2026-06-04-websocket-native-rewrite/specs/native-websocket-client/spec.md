## ADDED Requirements

### Requirement: WebSocket client SHALL connect via native WebSocket API
The client SHALL use the browser's native `WebSocket` constructor to establish a connection to the backend's direct STOMP endpoint at `/websocket?userId={userId}`. The URL SHALL be constructed from the current page origin, handling the `window.DataEaseBi?.baseUrl` override and dev mode proxy target.

#### Scenario: Standard production connection
- **WHEN** the plugin is installed and the user is logged in
- **THEN** the client SHALL create a `new WebSocket(wsUrl)` where `wsUrl` uses `wss://` if the page is HTTPS, otherwise `ws://`

#### Scenario: Dev mode connection through Vite proxy
- **WHEN** `import.meta.env.MODE === 'dev'`
- **THEN** the client SHALL use the proxy target URL from dev config as the WebSocket base, converting `http://` to `ws://`

### Requirement: Client SHALL send STOMP CONNECT frame on open
When the WebSocket connection opens, the client SHALL send a STOMP `CONNECT` frame with `accept-version:1.2` and `heart-beat:30000,0` headers.

#### Scenario: Connection established
- **WHEN** the WebSocket `onopen` event fires
- **THEN** the client SHALL send the frame `CONNECT\naccept-version:1.2\nheart-beat:30000,0\n\n\x00`

### Requirement: Client SHALL subscribe to configured channels after CONNECTED
Upon receiving a `CONNECTED` frame from the server, the client SHALL send `SUBSCRIBE` frames for each configured channel destination.

#### Scenario: Successful subscription
- **WHEN** the server responds with a `CONNECTED` frame
- **THEN** the client SHALL send `SUBSCRIBE\nid:sub-{index}\ndestination:/user/{userId}/{topic}\n\n\x00` for each configured channel

### Requirement: Client SHALL parse MESSAGE frames and emit events
When a `MESSAGE` frame is received, the client SHALL extract the body and emit it via the mitt event bus using the channel's configured event name.

#### Scenario: Export task notification received
- **WHEN** the server sends `MESSAGE\ndestination:/user/1/task-export-topic\ncontent-type:application/json\n\n{"status":"done"}\x00`
- **THEN** the client SHALL call `useEmitt().emitter.emit('task-export-topic-call', '{"status":"done"}')`

#### Scenario: Report notification received
- **WHEN** the server sends a MESSAGE frame with destination containing `/report-notice`
- **THEN** the client SHALL call `useEmitt().emitter.emit('report-notice-call', body)`

### Requirement: Client SHALL implement exponential backoff reconnection
When the WebSocket connection closes or errors, the client SHALL schedule a reconnection attempt with exponential backoff. The delay SHALL start at 5 seconds, double on each failure, and cap at 60 seconds. On successful connection, the delay SHALL reset to 5 seconds.

#### Scenario: First reconnection after disconnect
- **WHEN** the WebSocket closes unexpectedly
- **THEN** the client SHALL attempt to reconnect after 5 seconds

#### Scenario: Second consecutive reconnection failure
- **WHEN** the first reconnection attempt fails (WebSocket closes again)
- **THEN** the client SHALL wait 10 seconds before the next attempt

#### Scenario: Backoff caps at 60 seconds
- **WHEN** multiple consecutive failures have increased the delay beyond 60 seconds
- **THEN** the client SHALL use 60 seconds as the delay

#### Scenario: Delay resets on successful connection
- **WHEN** a reconnection succeeds (CONNECTED frame received)
- **THEN** the next reconnection delay SHALL reset to 5 seconds

### Requirement: Client SHALL send heartbeat keep-alive
After establishing a STOMP connection, the client SHALL send a `\n` (newline) heartbeat every 30 seconds to keep the connection alive through idle periods.

#### Scenario: Heartbeat during idle connection
- **WHEN** 30 seconds elapse with no STOMP frames sent or received
- **THEN** the client SHALL send `\n` over the WebSocket

#### Scenario: Heartbeat stops on disconnect
- **WHEN** the WebSocket closes
- **THEN** the heartbeat timer SHALL be cleared

### Requirement: Client SHALL provide destroy() for cleanup
The module SHALL export a `destroy()` function that clears all timers (reconnect, heartbeat), sends a STOMP DISCONNECT frame, closes the WebSocket, and marks the module as destroyed so no further reconnection attempts occur.

#### Scenario: Destroy during active connection
- **WHEN** `destroy()` is called while the WebSocket is connected
- **THEN** the client SHALL send `DISCONNECT\nreceipt:disconnect-0\n\n\x00`, close the WebSocket, clear all timers, and prevent future reconnection

#### Scenario: Destroy during reconnection wait
- **WHEN** `destroy()` is called while a reconnection is pending
- **THEN** the pending reconnect timer SHALL be cleared and no further reconnection SHALL occur

### Requirement: Client SHALL operate silently
The module SHALL NOT produce any `console.error`, `console.warn`, `console.info`, or `console.log` output during normal operation (connection, disconnection, reconnection, errors).

#### Scenario: Connection failure during reconnection
- **WHEN** a reconnection attempt fails
- **THEN** no console output SHALL be produced; the client SHALL silently schedule the next backoff attempt

### Requirement: Client SHALL respect login status
The client SHALL only attempt connection when the user is logged in (token and uid present in cache, or desktop mode). If the user logs out, the client SHALL disconnect and stop reconnecting.

#### Scenario: User not logged in
- **WHEN** `isLoginStatus()` returns false
- **THEN** the client SHALL NOT attempt to connect, and SHALL disconnect any active connection

#### Scenario: User logs out during active connection
- **WHEN** the user's token is removed from cache while the WebSocket is connected
- **THEN** the client SHALL disconnect on the next status check
