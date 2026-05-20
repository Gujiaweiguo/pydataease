## 1. Sync router scaffolding

- [x] 1.1 Create `app/routers/sync.py` with all 30 authenticated `/sync/**` stub endpoints grouped by datasource, task, task log, and summary responsibilities.
- [x] 1.2 Register the sync router from `app/main.py` under the existing `/de2api` API prefix.

## 2. Contract-focused tests

- [x] 2.1 Add `tests/test_sync_routes.py` to verify all 30 sync routes are registered on the FastAPI app.
- [x] 2.2 Add representative route tests to verify sync endpoints require `X-DE-TOKEN` and return the documented stub payloads when authenticated.

## 3. Verification

- [x] 3.1 Run `uv run ruff check .` from `core/pydataease-backend/`.
- [x] 3.2 Run `uv run pytest tests/test_sync_routes.py -v` from `core/pydataease-backend/`.
- [x] 3.3 Run `uv run python -c "from app.main import app; print(app.title)"` from `core/pydataease-backend/`.
