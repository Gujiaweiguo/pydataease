# Testing Guide — pydataease-backend

Everything you need to write, run, and understand the test suite.

## Quick Start

```bash
# Run all unit + route tests (no database needed)
uv run pytest tests/ -v --ignore=tests/test_e2e_*.py

# Run with integration tests (requires running PostgreSQL)
DE_E2E=1 uv run pytest tests/ -v

# Lint check (runs before tests in CI)
uv run ruff check .
```

All commands run from `core/pydataease-backend/`.

## Test Categories

| Category | Dependencies | Marker | Speed |
|----------|-------------|--------|-------|
| Unit tests | None | `pytest.mark.asyncio` | Fast (<1s each) |
| Route tests | httpx AsyncClient | `pytest.mark.asyncio` | Fast |
| Integration tests | PostgreSQL 16 | `DE_E2E=1` env var | Medium |
| E2E tests | Full stack | `DE_E2E=1` env var | Slow |

### Unit tests

No external services. Direct service instantiation. Use `pytest.mark.asyncio`
for async functions.

### Route tests

Use httpx `AsyncClient` against the FastAPI app. Services are swapped with
fakes via `app.dependency_overrides`. No database required.

### Integration tests

Real PostgreSQL. Gated by the `DE_E2E=1` environment variable. Tests that
require a live database check this variable and `pytest.skip()` when absent.

### E2E tests

Full user-journey tests (`test_e2e_creation_flow.py`, `test_e2e_dashboard_full.py`).
Run separately in CI after the main test job passes.

## Shared Fixtures (`tests/fixtures/`)

### `auth_fixtures.py`

```python
from tests.fixtures.auth_fixtures import _build_token

# Build a JWT token with arbitrary claims
token = _build_token(uid=1, oid=1)
headers = {"X-DE-TOKEN": token}
```

`_build_token(**claims)` creates a signed JWT using the app's secret key.
Pass keyword args like `uid`, `oid`, `exp` to set claims.

### `dataset_fixtures.py`

```python
from tests.fixtures.dataset_fixtures import FakeDatasetService

fake = FakeDatasetService()

# Wire into route tests via dependency_overrides
app.dependency_overrides[get_dataset_service] = lambda: fake
```

`FakeDatasetService` stubs every dataset service method (`tree`, `create`,
`save`, `rename`, `move`, `delete`, `per_delete`, `get_bar_info`,
`get_details`, `get_fields`, `preview_sql`, `export_dataset`) and records
calls in public lists (`created`, `saved`, `renamed`, `moved`, `deleted_ids`).

### `db_fixtures.py`

```python
# In conftest.py or test file
pytest_plugins = ["tests.fixtures.db_fixtures"]

async def test_something(db_session):
    result = await db_session.execute(text("SELECT 1"))
```

`db_session` is an async `AsyncSession` fixture. It connects to the database
specified by `DE_DATABASE_URL` (defaults to `localhost:5432/dataease`).

### `test_factories.py`

```python
from tests.fixtures.test_factories import stamp, timestamp_ms, cleanup_groups

oid = stamp()            # unique BigInteger ID via time.time_ns()
ts = timestamp_ms()      # current epoch milliseconds

# Cleanup after integration test
await cleanup_groups(session, [group_id_1, group_id_2])
```

- `stamp()` generates a unique BigInteger ID using `time.time_ns()`.
- `timestamp_ms()` returns current time in milliseconds.
- `cleanup_groups(session, ids)` deletes dataset groups in reverse order.

## Writing New Tests

### Route test pattern

```python
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.dataset_service import get_dataset_service
from tests.fixtures.auth_fixtures import _build_token
from tests.fixtures.dataset_fixtures import FakeDatasetService


@pytest.fixture
def fake_service():
    return FakeDatasetService()


@pytest.mark.asyncio
async def test_create_dataset(fake_service):
    app.dependency_overrides[get_dataset_service] = lambda: fake_service
    try:
        headers = {"X-DE-TOKEN": _build_token(uid=1, oid=1)}
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            resp = await client.post("/de2api/dataset/create", json={...}, headers=headers)
        assert resp.status_code == 200
        assert len(fake_service.created) == 1
    finally:
        app.dependency_overrides.clear()
```

### Integration test pattern

```python
import pytest
import os

from tests.fixtures.test_factories import stamp, cleanup_groups

skip_no_db = pytest.mark.skipif(
    not os.getenv("DE_E2E"),
    reason="Set DE_E2E=1 to run integration tests",
)


@skip_no_db
@pytest.mark.asyncio
async def test_dataset_create_db(db_session):
    gid = stamp()
    try:
        # ... create records via repository ...
        await db_session.commit()
    finally:
        await cleanup_groups(db_session, [gid])
```

### Unit test pattern

```python
import pytest
from app.services.some_service import SomeService


@pytest.mark.asyncio
async def test_business_logic():
    svc = SomeService()
    result = await svc.do_thing(input_data)
    assert result.status == "ok"
```

## Coverage

```bash
# Terminal report with missing lines
uv run pytest tests/ --cov=app --cov-report=term-missing

# LCOV report (used in CI)
uv run pytest tests/ --cov=app --cov-report=lcov:coverage.lcov

# Fail if below threshold
uv run pytest tests/ --cov=app --cov-fail-under=50
```

Current coverage sits around 79% on the services layer.

## CI Gates

The backend CI pipeline (`.github/workflows/backend-ci.yml`) runs these checks:

1. **Ruff lint** on source and tests: `uv run ruff check .`
2. **Migration check**: `uv run alembic upgrade head`
3. **Tests with coverage**: `uv run pytest tests/ -v --cov=app --cov-fail-under=50`
4. **Integration tests**: `DE_E2E=1 uv run pytest tests/test_dataset_integration.py ...`
5. **E2E user journey**: separate CI job, runs after tests pass
6. **Docker build**: verifies image builds without errors

Coverage reports are uploaded as artifacts and retained for 7 days.

## Database Setup

PostgreSQL is the sole database for both system metadata and demo business data:

```bash
# PostgreSQL 16 (metadata + demo data in `demo` schema)
docker start postgres16
```

Connection details:

| Container | Port | User | Password | Database |
|-----------|------|------|----------|----------|
| `postgres16` | 5432 | `dataease` | `dataease` | `dataease` |

The `DE_DATABASE_URL` env var in `.env` points to the PostgreSQL container.
