## Why

The initial FastAPI backend delivery left several items as stubs or deferrals. Cleanup tasks logged actions but didn't delete rows from the database. Export tasks tracked state but never generated files or served downloads. SQL preview returned canned data instead of executing real queries. WebSocket accepted connections but only echoed plain text. Contract tests were skeletal `raise NotImplementedError` stubs.

This change resolves all of those deferrals with working implementations.

## What Changes

- **Cleanup tasks**: `cleanup_expired_shares` and `cleanup_old_export_tasks` now execute real `DELETE` queries against `xpack_share` and `core_export_task`. New repository methods (`ShareRepository.delete_expired`, `ExportTaskRepository.delete_old_completed`) handle the bulk deletes. Retention is configurable via `DE_EXPORT_RETENTION_MS` (default 7 days).

- **Export file generation + download**: A new `file_generator` module produces `.xlsx` files using openpyxl. The export worker calls it during task execution, writing to `DE_EXPORT_DIR` (default `/tmp/de-exports`). The download endpoint validates file existence on disk and returns a `FileResponse`. Task records get updated with `file_name`, `file_size`, and `file_size_unit`.

- **SQL preview execution**: A new `SQLExecutor` service runs real `SELECT` queries. It validates that only `SELECT`/`WITH` statements are allowed, strips comments and quoted strings before checking for forbidden keywords (`INSERT`, `DROP`, etc.), and auto-appends `LIMIT 1000` when no `LIMIT` clause is present. Returns `{sql, data, fields, total}`.

- **WebSocket STOMP protocol**: A full STOMP frame parser/builder and session handler in `stomp_handler.py`. Handles `CONNECT`, `SUBSCRIBE`, `UNSUBSCRIBE`, `SEND`, and `DISCONNECT` commands with proper `CONNECTED`, `RECEIPT`, `MESSAGE`, and `ERROR` responses. Includes heartbeat support (server-side newline ping at negotiated interval). The WebSocket endpoint maintains backward compatibility with plain text echo for non-STOMP clients.

- **Contract tests**: All 59 contract test stubs converted from `raise NotImplementedError` to real API tests using `AsyncClient` with `ASGITransport`. Updated `conftest.py` with JWT-based auth fixtures and dependency override helpers. 42 tests pass, 17 skipped (endpoints not yet implemented).

## Capabilities

### New Capabilities

- **`sql-execution-engine`**: SQL validation and read-only execution with auto-LIMIT safety. Validates query shape, rejects DDL/DML, strips comments before keyword checks, and returns typed field metadata.

- **`stomp-websocket`**: STOMP 1.2 protocol over WebSocket. Frame parsing and serialization, session-scoped subscriptions, heartbeat negotiation, and graceful disconnect. Backward compatible with plain text echo.

- **`export-file-generation`**: Excel file generation via openpyxl, storage to configurable directory, file serving via `FileResponse`, and task metadata updates (name, size, unit).

### Modified Capabilities

- **`backend-contract-compatibility`** (delta): Contract tests now use real `AsyncClient` against the ASGI app. ResultMessage wrapper validation, auth failure coverage (401 for missing/invalid tokens), and proper dependency overrides. 42 passing, 17 skipped for unimplemented endpoints.

- **`runtime-deployment-cutover`** (delta): Cleanup tasks now execute real `DELETE` queries instead of logging stubs. Configurable retention period via `DE_EXPORT_RETENTION_MS`. Share expiry based on epoch millis comparison with `exp IS NOT NULL` guard.

## Impact

### Files

- `app/tasks/cleanup.py` (modified)
- `app/tasks/file_generator.py` (new)
- `app/tasks/export_worker.py` (modified)
- `app/services/sql_executor.py` (new)
- `app/services/stomp_handler.py` (new)
- `app/services/export_service.py` (modified)
- `app/services/dataset_service.py` (modified)
- `app/routers/export.py` (modified)
- `app/routers/websocket.py` (modified)
- `app/repositories/share_repo.py` (modified)
- `app/repositories/export_repo.py` (modified)
- `tests/contracts/` (all stubs converted)
- `tests/contracts/conftest.py` (new fixtures)

### Dependencies

- `openpyxl` added for Excel file generation
