## Capability: stomp-websocket

STOMP 1.2 protocol over WebSocket with frame parsing, session management, subscriptions, and heartbeat.

### Requirements

#### Requirement: STOMP frames SHALL follow the text-based format
Frames SHALL use the format: `COMMAND\nheader:value\n\nbody\x00` where `\x00` is the null terminator.

##### Scenario: Parsing a valid frame
- **WHEN** a frame `"SUBSCRIBE\nid:sub-1\ndestination:/topic/data\n\n\x00"` is received
- **THEN** the parser SHALL produce a frame with command `SUBSCRIBE`, headers `{"id": "sub-1", "destination": "/topic/data"}`, and empty body

#### Requirement: CONNECT SHALL produce a CONNECTED response
Upon receiving a `CONNECT` frame, the server SHALL respond with a `CONNECTED` frame containing the negotiated STOMP version and session ID.

##### Scenario: Client connects with accept-version
- **WHEN** a client sends `CONNECT` with header `accept-version:1.2,1.1`
- **THEN** the server SHALL respond with `CONNECTED` containing `version:1.2` (first version from the list)

#### Requirement: SUBSCRIBE and UNSUBSCRIBE SHALL manage subscriptions
`SUBSCRIBE` registers a subscription by id and destination. `UNSUBSCRIBE` removes it. Both send `RECEIPT` if the `receipt` header is present.

##### Scenario: Client subscribes then unsubscribes
- **WHEN** a client sends `SUBSCRIBE` with `id:sub-0` and `destination:/topic/alerts`
- **THEN** the session SHALL store the subscription and send `RECEIPT` with `receipt-id` matching the request

##### Scenario: SUBSCRIBE missing required headers
- **WHEN** a client sends `SUBSCRIBE` without `id` or `destination`
- **THEN** the server SHALL send an `ERROR` frame with message "SUBSCRIBE requires id and destination headers"

#### Requirement: SEND SHALL deliver MESSAGE to matching subscriptions
When a `SEND` frame arrives with a destination, the server SHALL send `MESSAGE` frames to all subscriptions matching that destination.

##### Scenario: Send to a subscribed destination
- **WHEN** a client has subscribed with `id:sub-0` to `destination:/topic/alerts` and sends `SEND` to `destination:/topic/alerts` with body `"hello"`
- **THEN** the server SHALL send a `MESSAGE` frame with `subscription:sub-0`, `destination:/topic/alerts`, a generated `message-id`, and body `"hello"`

##### Scenario: Send with no matching subscription
- **WHEN** a client sends `SEND` to a destination with no active subscriptions
- **THEN** no `MESSAGE` frame SHALL be sent (only `RECEIPT` if requested)

#### Requirement: DISCONNECT SHALL send RECEIPT and close the connection
`DISCONNECT` SHALL send a `RECEIPT` frame if the `receipt` header is present, then close the WebSocket connection.

##### Scenario: Graceful disconnect with receipt
- **WHEN** a client sends `DISCONNECT` with `receipt:rcpt-1`
- **THEN** the server SHALL send `RECEIPT` with `receipt-id:rcpt-1`, cancel any heartbeat task, and close the WebSocket

#### Requirement: Heartbeat SHALL send newline pings at negotiated intervals
When the client requests heartbeat via the `heart-beat` header (`cx,cy` format), the server SHALL send `\n` at `max(cx, cy)` millisecond intervals.

##### Scenario: Heartbeat negotiation
- **WHEN** a client sends `CONNECT` with `heart-beat:10000,5000`
- **THEN** the server SHALL send newline pings every 10000ms and include `heart-beat:10000,10000` in the `CONNECTED` response

#### Requirement: Non-STOMP text SHALL receive echo response
For backward compatibility, plain text that doesn't match STOMP frame structure SHALL be echoed back.

##### Scenario: Plain text message
- **WHEN** a client sends `"hello world"` (no null terminator, not a STOMP command)
- **THEN** the server SHALL respond with `"echo: hello world"`

#### Requirement: Unsupported STOMP commands SHALL produce ERROR frames
Any STOMP command not in the supported set SHALL generate an `ERROR` response.

##### Scenario: Unknown command
- **WHEN** a client sends a frame with command `ACK`
- **THEN** the server SHALL send an `ERROR` frame with message "Unsupported command: ACK"
