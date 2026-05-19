from __future__ import annotations

# pyright: reportArgumentType=false, reportAttributeAccessIssue=false, reportMissingImports=false

import os
import sqlite3
from datetime import date, datetime, time
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.services.sql_executor import SQLExecutor  # pyright: ignore[reportImplicitRelativeImport]


class _FakeCursor:
    def __init__(self, description: list[tuple[object, ...]]) -> None:
        self.description = description


class _FakeResult:
    def __init__(
        self,
        keys: list[str],
        rows: list[tuple[object, ...]],
        description: list[tuple[object, ...]] | None = None,
    ) -> None:
        self._keys = keys
        self._rows = rows
        self.cursor = _FakeCursor(description or [])

    def keys(self) -> list[str]:
        return self._keys

    def all(self) -> list[tuple[object, ...]]:
        return self._rows


class _FakeConnection:
    def __init__(self, *, result: _FakeResult | None = None, error: Exception | None = None) -> None:
        self._result = result
        self._error = error
        self.executed_sql: str | None = None

    async def execute(self, statement: object) -> _FakeResult:
        self.executed_sql = str(statement)
        if self._error is not None:
            raise self._error
        assert self._result is not None
        return self._result


class _FakeConnectContext:
    def __init__(self, connection: _FakeConnection) -> None:
        self._connection = connection

    async def __aenter__(self) -> _FakeConnection:
        return self._connection

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False


class _FakeEngine:
    def __init__(self, connection: _FakeConnection) -> None:
        self._connection = connection

    def connect(self) -> _FakeConnectContext:
        return _FakeConnectContext(self._connection)


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
        self.executed_sql: str | None = None

    async def execute(self, statement: object) -> _SQLiteResult:
        self.executed_sql = str(statement)
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


class _FakeSessionContext:
    def __init__(self, session: object) -> None:
        self._session = session

    async def __aenter__(self) -> object:
        return self._session

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False


def _user() -> TokenUser:
    return TokenUser(user_id=7, oid=9)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM (DELETE FROM t) AS x",
        "DROP TABLE metrics",
        "ALTER TABLE metrics ADD COLUMN owner TEXT",
        "GRANT SELECT ON metrics TO analyst",
        "REVOKE SELECT ON metrics FROM analyst",
        "SELECT * FROM metrics; DROP TABLE metrics",
        "SELECT * FROM metrics -- bypass\nDROP TABLE metrics",
        "SELECT * FROM metrics /* bypass */ DROP TABLE metrics",
    ],
)
async def test_execute_select_rejects_mutating_and_bypass_sql(sql: str) -> None:
    executor = SQLExecutor(cast(Any, _FakeEngine(_FakeConnection(result=_FakeResult([], [])))))

    with pytest.raises(HTTPException, match=r"Only SELECT queries are allowed|Only a single SELECT query is allowed"):
        await executor.execute_select(sql)


@pytest.mark.asyncio
async def test_execute_select_allows_union_query_and_enforces_limit() -> None:
    connection = _FakeConnection(
        result=_FakeResult(
            keys=["id"],
            rows=[(1,), (2,)],
            description=[("id", "integer")],
        )
    )
    executor = SQLExecutor(cast(Any, _FakeEngine(connection)))

    payload = await executor.execute_select("SELECT 1 AS id UNION SELECT 2 AS id", limit=5)

    assert connection.executed_sql == "SELECT 1 AS id UNION SELECT 2 AS id LIMIT 5"
    assert payload["total"] == 2


@pytest.mark.asyncio
async def test_execute_select_appends_limit_to_cte_query() -> None:
    connection = _FakeConnection(result=_FakeResult(keys=["id"], rows=[(1,)], description=[("id", "integer")]))
    executor = SQLExecutor(cast(Any, _FakeEngine(connection)))

    payload = await executor.execute_select("WITH recent AS (SELECT 1 AS id) SELECT id FROM recent", limit=9)

    assert payload["sql"] == "WITH recent AS (SELECT 1 AS id) SELECT id FROM recent LIMIT 9"


@pytest.mark.asyncio
async def test_execute_select_preserves_existing_limit_in_complex_query() -> None:
    connection = _FakeConnection(result=_FakeResult(keys=["id"], rows=[(1,)], description=[("id", "integer")]))
    executor = SQLExecutor(cast(Any, _FakeEngine(connection)))
    sql = "SELECT * FROM (SELECT 1 AS id) t LIMIT 3"

    payload = await executor.execute_select(sql, limit=99)

    assert connection.executed_sql == sql
    assert payload["sql"] == sql


@pytest.mark.asyncio
async def test_execute_select_formats_rows_and_infers_python_types() -> None:
    rows = [
        (
            True,
            7,
            3.14,
            Decimal("10.50"),
            "alpha",
            b"x",
            datetime(2024, 1, 2, 3, 4, 5),
            date(2024, 1, 2),
            time(3, 4, 5),
            {"k": "v"},
            [1, 2],
        )
    ]
    connection = _FakeConnection(
        result=_FakeResult(
            keys=["b", "i", "f", "n", "s", "bytes", "ts", "d", "t", "obj", "arr"],
            rows=rows,
            description=[tuple() for _ in range(11)],
        )
    )
    executor = SQLExecutor(cast(Any, _FakeEngine(connection)))

    payload = await executor.execute_select("SELECT * FROM typed_values")

    assert payload["data"] == [list(rows[0])]
    assert payload["fields"] == [
        {"name": "b", "type": "boolean"},
        {"name": "i", "type": "integer"},
        {"name": "f", "type": "float"},
        {"name": "n", "type": "numeric"},
        {"name": "s", "type": "varchar"},
        {"name": "bytes", "type": "bytea"},
        {"name": "ts", "type": "timestamp"},
        {"name": "d", "type": "date"},
        {"name": "t", "type": "time"},
        {"name": "obj", "type": "jsonb"},
        {"name": "arr", "type": "jsonb"},
    ]


@pytest.mark.asyncio
async def test_execute_select_prefers_cursor_description_type_metadata() -> None:
    class _TypeCode:
        name = "BIGINT"

    connection = _FakeConnection(
        result=_FakeResult(
            keys=["id", "label"],
            rows=[(1, "alpha")],
            description=[("id", _TypeCode()), ("label", "VARCHAR")],
        )
    )
    executor = SQLExecutor(cast(Any, _FakeEngine(connection)))

    payload = await executor.execute_select("SELECT id, label FROM preview_items")

    assert payload["fields"] == [{"name": "id", "type": "bigint"}, {"name": "label", "type": "varchar"}]


@pytest.mark.asyncio
async def test_execute_select_wraps_timeout_error() -> None:
    executor = SQLExecutor(cast(Any, _FakeEngine(_FakeConnection(error=TimeoutError("query timed out")))))

    with pytest.raises(HTTPException, match="SQL preview failed: query timed out") as exc_info:
        await executor.execute_select("SELECT 1")

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_execute_select_wraps_sqlalchemy_error() -> None:
    executor = SQLExecutor(cast(Any, _FakeEngine(_FakeConnection(error=SQLAlchemyError("driver failed")))))

    with pytest.raises(HTTPException, match="SQL preview failed: driver failed"):
        await executor.execute_select("SELECT 1")


@pytest.mark.asyncio
async def test_execute_with_permissions_disabled_uses_permission_branch_without_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.settings.config as config_module  # pyright: ignore[reportImplicitRelativeImport]

    connection = _FakeConnection(result=_FakeResult(keys=["id"], rows=[(1,)], description=[("id", "integer")]))
    executor = SQLExecutor(cast(Any, _FakeEngine(connection)))
    monkeypatch.setattr(config_module, "get_settings", lambda: SimpleNamespace(row_column_permission_enabled=False))

    payload = await executor.execute_select("SELECT id FROM secure_items", user=_user(), dataset_id=12)

    assert connection.executed_sql == "SELECT id FROM secure_items LIMIT 1000"
    assert payload["fields"] == [{"name": "id", "type": "integer"}]


@pytest.mark.asyncio
async def test_execute_with_permissions_applies_row_and_column_rules(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.dependencies.database as db_module  # pyright: ignore[reportImplicitRelativeImport]
    import app.services.data_permission_service as perm_module  # pyright: ignore[reportImplicitRelativeImport]
    import app.settings.config as config_module  # pyright: ignore[reportImplicitRelativeImport]

    class _FakePermissionService:
        def __init__(self, session: object) -> None:
            self.session = session

        async def collect_row_filters(self, user: TokenUser, dataset_id: int) -> list[str]:
            assert user.user_id == 7
            assert dataset_id == 88
            return ["tenant_id = 9"]

        async def apply_column_rules(
            self,
            user: TokenUser,
            dataset_id: int,
            fields: list[dict[str, str]],
            rows: list[list[object]],
        ) -> tuple[list[dict[str, str]], list[list[object]]]:
            assert user.user_id == 7
            assert dataset_id == 88
            return fields[:1], [[row[0]] for row in rows]

    connection = _FakeConnection(
        result=_FakeResult(
            keys=["id", "secret"],
            rows=[(1, "hidden")],
            description=[("id", "integer"), ("secret", "varchar")],
        )
    )
    executor = SQLExecutor(cast(Any, _FakeEngine(connection)))

    monkeypatch.setattr(config_module, "get_settings", lambda: SimpleNamespace(row_column_permission_enabled=True))
    monkeypatch.setattr(perm_module, "DataPermissionService", _FakePermissionService)
    monkeypatch.setattr(perm_module, "apply_row_filters", lambda sql, filters: f"{sql} WHERE {filters[0]}")
    monkeypatch.setattr(db_module, "async_session", lambda: _FakeSessionContext(object()))

    payload = await executor.execute_select("SELECT id, secret FROM secure_items", user=_user(), dataset_id=88)

    assert connection.executed_sql == "SELECT id, secret FROM secure_items LIMIT 1000 WHERE tenant_id = 9"
    assert payload == {
        "sql": "SELECT id, secret FROM secure_items LIMIT 1000 WHERE tenant_id = 9",
        "data": [[1]],
        "fields": [{"name": "id", "type": "integer"}],
        "total": 1,
    }


@pytest.mark.asyncio
async def test_execute_select_runs_where_clauses_with_sqlite() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("CREATE TABLE preview_items (id INTEGER PRIMARY KEY, category TEXT, active INTEGER)")
    connection.execute(
        "INSERT INTO preview_items (id, category, active) VALUES (1, 'alpha', 1), (2, 'beta', 0), (3, 'alpha', 1)"
    )
    connection.commit()

    try:
        payload = await SQLExecutor(cast(Any, _SQLiteEngine(connection))).execute_select(
            "SELECT id, category FROM preview_items WHERE category = 'alpha' AND active = 1 ORDER BY id"
        )
    finally:
        connection.close()

    assert payload["data"] == [[1, "alpha"], [3, "alpha"]]
    assert payload["fields"] == [{"name": "id", "type": "integer"}, {"name": "category", "type": "varchar"}]


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("DE_E2E") != "1", reason="Requires PostgreSQL (set DE_E2E=1)")
async def test_execute_select_postgres_returns_expected_rows(db_session: AsyncSession) -> None:
    payload = cast(dict[str, object], await SQLExecutor(db_session.bind).execute_select(
        "SELECT value FROM (VALUES (1), (2), (3)) AS sample(value) WHERE value >= 2 ORDER BY value",
        limit=10,
    ))

    assert payload["sql"].endswith("LIMIT 10")
    assert payload["data"] == [[2], [3]]
    fields = cast(list[dict[str, object]], payload["fields"])
    assert fields[0]["name"] == "value"


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("DE_E2E") != "1", reason="Requires PostgreSQL (set DE_E2E=1)")
async def test_execute_select_postgres_handles_cte_subquery_and_join(db_session: AsyncSession) -> None:
    payload = cast(dict[str, object], await SQLExecutor(db_session.bind).execute_select(
        "WITH base AS (SELECT * FROM (VALUES (1, 'east'), (2, 'west')) AS t(id, region)) SELECT b.id, b.region FROM base b JOIN (SELECT 1 AS min_id) limits ON b.id >= limits.min_id ORDER BY b.id",
        limit=4,
    ))

    assert payload["data"] == [[1, "east"], [2, "west"]]
    fields = cast(list[dict[str, object]], payload["fields"])
    assert [field["name"] for field in fields] == ["id", "region"]


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv("DE_E2E") != "1", reason="Requires PostgreSQL (set DE_E2E=1)")
async def test_execute_select_postgres_supports_union_queries(db_session: AsyncSession) -> None:
    payload = cast(dict[str, object], await SQLExecutor(db_session.bind).execute_select(
        "SELECT id FROM (SELECT 1 AS id UNION SELECT 2 AS id) AS unioned ORDER BY id",
        limit=2,
    ))

    assert payload["data"] == [[1], [2]]
    assert payload["total"] == 2
