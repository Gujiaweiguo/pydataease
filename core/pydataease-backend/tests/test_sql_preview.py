from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from importlib import import_module
import sqlite3

import pytest
from fastapi import HTTPException
from httpx import AsyncClient
from jose import jwt

from app.main import app
from app.services.dataset_service import get_dataset_service
from app.settings.config import get_settings

SQLExecutor = import_module("app.services.sql_executor").SQLExecutor


def _build_token(**claims: int) -> str:
    settings = get_settings()
    payload = {**claims, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


class _FakeCursor:
    def __init__(self, description: list[tuple[object, object, object, object, object, object, object]]) -> None:
        self.description = description


class _FakeResult:
    def __init__(
        self,
        keys: list[str],
        rows: list[tuple[object, ...]],
        description: list[tuple[object, object, object, object, object, object, object]],
    ) -> None:
        self._keys = keys
        self._rows = rows
        self.cursor = _FakeCursor(description)

    def keys(self) -> list[str]:
        return self._keys

    def all(self) -> list[tuple[object, ...]]:
        return self._rows


class _FakeConnection:
    def __init__(self, result: _FakeResult) -> None:
        self.result = result
        self.executed_sql: str | None = None

    async def execute(self, statement: object) -> _FakeResult:
        self.executed_sql = str(statement)
        return self.result


class _FakeConnectContext:
    def __init__(self, connection: _FakeConnection) -> None:
        self.connection = connection

    async def __aenter__(self) -> _FakeConnection:
        return self.connection

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False


class _FakeEngine:
    def __init__(self, connection: _FakeConnection) -> None:
        self.connection = connection

    def connect(self) -> _FakeConnectContext:
        return _FakeConnectContext(self.connection)


class _SQLiteResult:
    def __init__(self, cursor: sqlite3.Cursor) -> None:
        self.cursor = cursor

    def keys(self) -> list[str]:
        description = self.cursor.description or []
        return [str(column[0]) for column in description]

    def all(self) -> list[tuple[object, ...]]:
        return [tuple(row) for row in self.cursor.fetchall()]


class _SQLiteConnection:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    async def execute(self, statement: object) -> _SQLiteResult:
        cursor = self._connection.execute(str(statement))
        return _SQLiteResult(cursor)


class _SQLiteConnectContext:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    async def __aenter__(self) -> _SQLiteConnection:
        return _SQLiteConnection(self._connection)

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False


class _SQLiteEngine:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def connect(self) -> _SQLiteConnectContext:
        return _SQLiteConnectContext(self._connection)


@pytest.mark.asyncio
async def test_sql_executor_rejects_non_select_queries() -> None:
    executor = SQLExecutor(_FakeEngine(_FakeConnection(_FakeResult([], [], []))))

    for sql in [
        "INSERT INTO preview_items VALUES (1)",
        "UPDATE preview_items SET name = 'x'",
        "DELETE FROM preview_items",
        "WITH doomed AS (DELETE FROM preview_items RETURNING id) SELECT * FROM doomed",
    ]:
        with pytest.raises(HTTPException) as exc_info:
            await executor.execute_select(sql)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Only SELECT queries are allowed"


@pytest.mark.asyncio
async def test_sql_executor_appends_default_limit() -> None:
    result = _FakeResult(
        keys=["id"],
        rows=[(1,)],
        description=[("id", "integer", None, None, None, None, None)],
    )
    connection = _FakeConnection(result)
    executor = SQLExecutor(_FakeEngine(connection))

    payload = await executor.execute_select("SELECT id FROM preview_items")

    assert connection.executed_sql == "SELECT id FROM preview_items LIMIT 1000"
    assert payload == {
        "sql": "SELECT id FROM preview_items LIMIT 1000",
        "data": [[1]],
        "fields": [{"name": "id", "type": "integer"}],
        "total": 1,
    }


@pytest.mark.asyncio
async def test_sql_executor_executes_real_sql_with_sqlite() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("CREATE TABLE preview_items (id INTEGER PRIMARY KEY, name TEXT)")
    connection.execute("INSERT INTO preview_items (id, name) VALUES (1, 'alpha'), (2, 'beta')")
    connection.commit()

    try:
        executor = SQLExecutor(_SQLiteEngine(connection))
        payload = await executor.execute_select("SELECT id, name FROM preview_items ORDER BY id")
    finally:
        connection.close()

    assert payload["sql"] == "SELECT id, name FROM preview_items ORDER BY id LIMIT 1000"
    assert payload["data"] == [[1, "alpha"], [2, "beta"]]
    assert payload["fields"] == [
        {"name": "id", "type": "integer"},
        {"name": "name", "type": "varchar"},
    ]
    assert payload["total"] == 2


@pytest.mark.asyncio
async def test_sql_executor_returns_400_for_invalid_sql() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE preview_items (id INTEGER PRIMARY KEY, name TEXT)")
    connection.commit()

    try:
        executor = SQLExecutor(_SQLiteEngine(connection))
        with pytest.raises(HTTPException) as exc_info:
            await executor.execute_select("SELECT missing FROM preview_items")
    finally:
        connection.close()

    assert exc_info.value.status_code == 400
    assert "SQL preview failed" in str(exc_info.value.detail)


class _FakePreviewService:
    async def preview_sql(self, sql: str) -> dict[str, object]:
        return {
            "sql": sql,
            "data": [[1, "alpha"]],
            "fields": [{"name": "id", "type": "integer"}, {"name": "name", "type": "varchar"}],
            "total": 1,
        }


@pytest.fixture
def preview_service_override() -> Generator[None, None, None]:
    app.dependency_overrides[get_dataset_service] = lambda: _FakePreviewService()
    yield
    _ = app.dependency_overrides.pop(get_dataset_service, None)


@pytest.mark.asyncio
@pytest.mark.usefixtures("preview_service_override")
async def test_preview_sql_route_uses_preview_sql_method(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/de2api/datasetData/previewSql",
        headers=auth_headers,
        json={"sql": "SELECT id, name FROM preview_items LIMIT 1"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == {
        "sql": "SELECT id, name FROM preview_items LIMIT 1",
        "data": [[1, "alpha"]],
        "fields": [{"name": "id", "type": "integer"}, {"name": "name", "type": "varchar"}],
        "total": 1,
    }
