## Design

### D1: Cleanup Tasks

**Approach**: Reuse the existing `async_session` factory from `app.dependencies.database`. Add bulk-delete methods to the relevant repositories rather than iterating and deleting one at a time.

**ShareRepository.delete_expired(exp_before: int)**: Executes `DELETE FROM xpack_share WHERE exp IS NOT NULL AND exp < :exp_before`. The `IS NOT NULL` guard avoids deleting shares with no expiration. Returns row count for logging.

**ExportTaskRepository.delete_old_completed(before_ms: int)**: Executes `DELETE FROM core_export_task WHERE export_status IN ('SUCCESS', 'FAILED') AND export_time < :before_ms`. Only cleans up completed or failed tasks, never touches `INITIATED` or `RUNNING` tasks.

**Configurability**: `DE_EXPORT_RETENTION_MS` env var controls how old completed tasks must be before cleanup. Defaults to 7 days (604,800,000 ms). Parsed via a small `_env_int` helper that falls back to the default on missing or malformed values.

**Scheduling**: Both cleanup functions are plain async callables suitable for APScheduler. Each creates its own session via `async_session()` context manager.

### D2: Export File Generation + Download

**File generation**: `generate_export_file()` in `app/tasks/file_generator.py` is a pure function. Takes `task_id`, `file_name`, `params`, and `export_dir`. Creates the directory if needed, sanitizes the filename (strips path components, appends `.xlsx`), writes data rows via openpyxl's `worksheet.append()`. Returns `(file_path, file_size)`.

**Row normalization**: `_normalize_row()` handles dict rows (takes values), list/tuple rows (casts to list), and scalar values (wraps in list). This lets the params dict contain data in multiple formats.

**Export worker integration**: `ExportTaskWorker._execute_with_retry()` calls `generate_export_file()` after marking the task `RUNNING`. Updates the task record with `file_name` (basename only), `file_size` (float), and `file_size_unit` ("B"). Then marks `SUCCESS`.

**Download flow**: `ExportService.download()` fetches the task, checks status is `SUCCESS`, resolves the file path relative to `DE_EXPORT_DIR`, verifies the file exists on disk. Returns a dict with path info. The router converts this to a `FileResponse` with `application/octet-stream` media type.

**Error states**: Download returns structured status objects (not exceptions) when the task isn't ready, file metadata is missing, or the file isn't on disk.

### D3: SQL Preview Execution

**Architecture**: `SQLExecutor` is a standalone service with no FastAPI dependency injection. Takes an optional `AsyncEngine` (defaults to the global `engine`). Single public method: `execute_select(sql, limit=1000)`.

**Validation pipeline** (`_normalize_sql`):
1. Strip whitespace and trailing semicolons
2. Check query starts with `SELECT` or `WITH` (case-insensitive, regex)
3. Sanitize: strip line comments (`--`), block comments (`/* */`), single-quoted strings, double-quoted identifiers
4. Reject if semicolons remain after sanitization (multi-statement attempt)
5. Reject if forbidden keywords found: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `TRUNCATE`, `GRANT`, `REVOKE`, `MERGE`, `CALL`, `COPY`, `VACUUM`, `ANALYZE`, `COMMENT`, `EXECUTE`

**Auto-LIMIT**: `_apply_limit()` checks (against sanitized SQL) whether a `LIMIT` clause exists. If not, appends `LIMIT {limit}`. The default is 1000. Rejects limit <= 0.

**Field type inference**: `_build_fields()` tries cursor description first, falls back to Python type inference from actual row values. Maps Python types to SQL-ish names: `int` -> `integer`, `str` -> `varchar`, `Decimal` -> `numeric`, `datetime` -> `timestamp`, etc.

**Integration**: `DatasetService.preview_sql()` delegates directly to `SQLExecutor.execute_select()`. No additional service layer wrapping.

### D4: WebSocket STOMP Protocol

**Frame format**: Text-based protocol. `COMMAND\nheader1:value1\nheader2:value2\n\nbody\x00`. `parse_frame()` splits on `\x00` (null terminator), normalizes `\r\n` to `\n`, extracts command from first line, parses headers until blank line, treats remainder as body.

**Session model**: `StompSession` holds per-connection state: session ID (auto-incremented), subscriptions map (`{sub_id: destination}`), connected flag, heartbeat interval, and heartbeat task reference.

**Command handling**:
- `CONNECT` -> negotiate version from `accept-version` header (take first comma-separated value), negotiate heartbeat from `heart-beat` header (`cx,cy` format), send `CONNECTED` frame, optionally start heartbeat task
- `SUBSCRIBE` -> requires `id` and `destination` headers, stores in subscriptions map, sends `RECEIPT` if requested
- `UNSUBSCRIBE` -> requires `id` header, removes from subscriptions map, sends `RECEIPT` if requested
- `SEND` -> requires `destination` header, iterates subscriptions to find matching destinations, sends `MESSAGE` frames to each match, sends `RECEIPT` if requested
- `DISCONNECT` -> sends `RECEIPT` if requested, cancels heartbeat, closes websocket

**Error handling**: Unsupported commands get `ERROR` frames. Missing required headers get `ERROR` frames with descriptive messages.

**Heartbeat**: Negotiated from client's `heart-beat` header. Takes `max(cx, cy)` where `cx` is client outgoing and `cy` is client incoming. Server sends `\n` (newline ping) at the negotiated interval. Implemented as an `asyncio.Task` that sleeps and sends.

**WebSocket endpoint**: The router creates a `StompSession` per connection. Uses a text buffer for partial frames. Non-STOMP text (no null terminator, doesn't start with a STOMP command) gets echoed back as `echo: {text}` for backward compatibility. The welcome JSON message is sent immediately on connection accept.

**Protocol abstraction**: `StompWebSocket` protocol defines `send_text` and `close`. This decouples the session logic from FastAPI's `WebSocket` class, making it testable without a live connection.

### D5: Contract Tests

**Test infrastructure**: `conftest.py` provides:
- `async_client` fixture using `httpx.AsyncClient` with `ASGITransport(app=app)`
- `auth_headers` fixture that creates a valid JWT and returns `{"X-DE-TOKEN": token}`
- `override_dependencies` fixture that swaps real services for fakes during tests
- `FakeService` pattern: lightweight stubs that return predictable data without hitting the database

**Test patterns**: Each test makes a real HTTP request through the ASGI stack. Response validation checks:
- Status code matches expectation
- Response body has `ResultMessage` wrapper structure (`code`, `data`, `msg`)
- Auth-protected endpoints return 401 for missing or invalid tokens
- Data shape matches the Pydantic response schema

**Skipped tests**: 17 tests are marked `skip` for endpoints that exist in the frontend contract but aren't implemented in the Python backend yet (e.g., advanced visualization operations, embedded token management).
