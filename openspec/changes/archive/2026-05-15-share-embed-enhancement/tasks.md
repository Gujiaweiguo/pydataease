## 1. Share Resolution Engine

- [x] 1.1 Implement `resolve(uuid, password=None)` in `ShareService` with expiration check (`exp`), password verification (constant-time), and share-not-found handling.
- [x] 1.2 Implement `validate_password(payload)` in `ShareService` — look up share by UUID from payload, verify password, return success/failure.
- [x] 1.3 Implement `get_status(resource_id)` in `ShareService` — return whether a share exists for the resource, including `uuid`, `exp`, `has_pwd`, and `auto_pwd` status.

## 2. Public Share Access Endpoint

- [x] 2.1 Add `GET /share/view/{uuid}` route (no auth required) that calls `resolve()` and returns the share metadata. Accept optional `password` query parameter.
- [x] 2.2 Add `/share/view/` to auth middleware whitelist so unauthenticated requests pass through.
- [x] 2.3 Wire share type routing: if share `type` indicates dashboard, fetch visualization data via `VisualizationService`; if chart, fetch via `ChartService`. Return the resource data in the response.

## 3. Embed Token Auth

- [x] 3.1 Add `generate_embed_token(uuid)` method to `ShareService` that creates a JWT with `resourceId`, `uuid`, `exp` claims, signed with `DE_SHARE_SECRET_KEY`. Token `exp` must not exceed the share's `exp`.
- [x] 3.2 Add `POST /share/embedToken` route (authenticated) that generates and returns an embed token for a given share UUID.
- [x] 3.3 Extend auth middleware's `X-EMBEDDED-TOKEN` handling: after decoding the JWT, look up the share by UUID and verify it still exists and is not expired. Set `request.state.share_resource_id` on success.

## 4. Share Audit

- [x] 4.1 Update `ShareTicketRepository` to support `update_access_time(ticket_id)` — set `access_time` to current timestamp.
- [x] 4.2 Add `record_access(uuid, client_ip)` method to `ShareService` that logs share access events (UUID, timestamp, IP) via Python logging. Ensure audit failures do not block share resolution.
- [x] 4.3 Wire `record_access` into the `resolve()` method so every successful share resolution triggers audit logging and ticket access_time update.

## 5. Tests

- [x] 5.1 Add tests for `resolve()`: expired share rejected, password-protected share rejects wrong password, password-protected share accepts correct password, share without password resolves directly.
- [x] 5.2 Add tests for embed token generation and validation: token contains correct claims, expired token rejected, token for deleted share rejected.
- [x] 5.3 Add tests for public `/share/view/{uuid}` endpoint: unauthenticated access works, password prompt returned when needed, expired share returns error.
- [x] 5.4 `cd core/pydataease-backend && uv run ruff check .` — zero errors.
- [x] 5.5 `cd core/pydataease-backend && uv run pytest tests/ -v --ignore=tests/test_e2e_creation_flow.py` — all pass.
