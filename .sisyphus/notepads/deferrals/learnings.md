## 2026-05-10 SQL preview execution
- `SQLExecutor` can safely gate preview SQL by stripping comments/quoted literals, requiring `SELECT`/`WITH`, rejecting semicolons and DDL/DML keywords, then appending `LIMIT 1000` when no explicit limit is present.
- For lightweight async tests without `aiosqlite`, a small fake async engine around `sqlite3` is enough to exercise `AsyncEngine.connect()/execute()`-style SQL preview behavior and cursor metadata extraction.

## 2026-05-10 STOMP websocket
- Minimal SockJS/STOMP compatibility can coexist with legacy echo behavior by buffering websocket text until a NULL terminator and only parsing frames once complete.
- A lightweight in-process STOMP session is enough for frontend notifications: CONNECT negotiates heart-beat, SUBSCRIBE/UNSUBSCRIBE track destination mappings, SEND can echo MESSAGE frames to matching local subscriptions, and RECEIPT/ERROR handling keeps protocol interactions predictable.

## 2026-05-10 Contract tests
- Contract coverage can be upgraded in-place by reusing `Fake*Service` classes from implementation tests and installing them with `app.dependency_overrides` per test module.
- `tests/contracts/conftest.py` should own token fixtures plus `httpx.AsyncClient(ASGITransport(app=app))` so contract tests exercise the real FastAPI app and middleware stack.
- Some legacy contract paths still have no Python equivalent; keeping those tests with `@pytest.mark.skip(reason="Endpoint not yet implemented")` preserves inventory coverage without reintroducing failing stubs.
## 2026-05-10 L1 core_user auth schema slice

- New FastAPI auth persistence can follow the existing lightweight repository composition pattern: keep a dedicated `UserRepository` that wraps `AsyncBaseRepository` for CRUD and only hand-roll targeted lookup methods like `get_by_account`.
- When no live PostgreSQL instance is available, a manual Alembic revision chained off the current head plus `uv run alembic upgrade head --sql` is enough to validate a new table migration for the FastAPI backend.
