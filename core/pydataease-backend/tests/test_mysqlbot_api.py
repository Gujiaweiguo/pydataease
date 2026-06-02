"""Tests for MySQLBot callback API endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.main import app
from app.services.mysqlbot_service import MysqlBotService, get_mysqlbot_service
from app.schemas.mysqlbot import (
    MysqlBotDatasource,
    MysqlBotField,
    MysqlBotQueryResponse,
    MysqlBotTable,
)


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------

_FAKE_API_KEY = "test-apikey-for-mysqlbot"


class _FakeSettingRow:
    def __init__(self, value: str) -> None:
        self.setting_value = value


class _FakeSysSettingRepo:
    def __init__(self, _session=None) -> None:
        pass

    async def get_by_key(self, key: str):
        if key == "sqlbot.apiKey":
            return _FakeSettingRow(_FAKE_API_KEY)
        return None


class FakeMysqlBotService(MysqlBotService):
    """Stub service that returns predictable data without touching the DB."""

    def __init__(self) -> None:
        # Skip parent __init__ — no real session needed
        self.session = None  # type: ignore[assignment]
        self.repo = None  # type: ignore[assignment]

    async def list_datasources(self) -> list[MysqlBotDatasource]:
        return [
            MysqlBotDatasource(id=1, name="test-mysql", type="mysql", host="10.0.0.1", port=3306, dataBase="testdb", user="root", password="secret"),
            MysqlBotDatasource(id=2, name="test-pg", type="postgresql", host="10.0.0.2", port=5432, dataBase="pgdb", user="postgres", password="pgpass"),
        ]

    async def list_tables(self, datasource_id: int) -> list[MysqlBotTable]:
        if datasource_id == 999:
            raise ValueError(f"Datasource {datasource_id} not found")
        return [
            MysqlBotTable(name="orders", comment="public"),
            MysqlBotTable(name="users", comment="public"),
        ]

    async def list_fields(self, datasource_id: int, table_name: str) -> list[MysqlBotField]:
        if datasource_id == 999:
            raise ValueError(f"Datasource {datasource_id} not found")
        return [
            MysqlBotField(name="id", type="integer", comment=None),
            MysqlBotField(name="name", type="varchar", comment="user name"),
        ]

    async def execute_query(self, datasource_id: int, sql: str) -> MysqlBotQueryResponse:
        if datasource_id == 999:
            raise ValueError(f"Datasource {datasource_id} not found")
        if "DROP" in sql.upper():
            raise PermissionError("Only SELECT statements are allowed")
        return MysqlBotQueryResponse(
            fields=["id", "name"],
            data=[[1, "Alice"], [2, "Bob"]],
            total=2,
        )


@pytest.fixture(autouse=True)
def _install_fakes(monkeypatch):
    """Override auth and service for all tests in this module."""
    import app.dependencies.mysqlbot_auth as auth_mod

    monkeypatch.setattr(auth_mod, "SysSettingRepository", _FakeSysSettingRepo)
    app.dependency_overrides[get_mysqlbot_service] = lambda: FakeMysqlBotService()
    yield
    app.dependency_overrides.pop(get_mysqlbot_service, None)


# ---------------------------------------------------------------------------
# Auth gate tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mysqlbot_no_api_key_returns_401(client: AsyncClient) -> None:
    response = await client.get("/de2api/mysqlbot/api/datasources")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_mysqlbot_wrong_api_key_returns_401(client: AsyncClient) -> None:
    response = await client.get(
        "/de2api/mysqlbot/api/datasources",
        headers={"X-API-Key": "bad-key"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /datasources
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_datasources(client: AsyncClient) -> None:
    response = await client.get(
        "/de2api/mysqlbot/api/datasources",
        headers={"X-API-Key": _FAKE_API_KEY},
    )
    assert response.status_code == 200
    body = response.json()
    # Response is wrapped by ResultMessageMiddleware
    data = body.get("data", body)
    assert len(data) == 2
    assert data[0]["name"] == "test-mysql"
    assert data[0]["host"] == "10.0.0.1"
    assert data[0]["port"] == 3306
    assert data[0]["dataBase"] == "testdb"
    assert data[1]["type"] == "postgresql"


# ---------------------------------------------------------------------------
# GET /datasources/{id}/tables
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_tables(client: AsyncClient) -> None:
    response = await client.get(
        "/de2api/mysqlbot/api/datasources/1/tables",
        headers={"X-API-Key": _FAKE_API_KEY},
    )
    assert response.status_code == 200
    body = response.json()
    data = body.get("data", body)
    assert len(data) == 2
    assert data[0]["name"] == "orders"


@pytest.mark.asyncio
async def test_list_tables_not_found(client: AsyncClient) -> None:
    response = await client.get(
        "/de2api/mysqlbot/api/datasources/999/tables",
        headers={"X-API-Key": _FAKE_API_KEY},
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /datasources/{id}/tables/{table}/fields
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_fields(client: AsyncClient) -> None:
    response = await client.get(
        "/de2api/mysqlbot/api/datasources/1/tables/orders/fields",
        headers={"X-API-Key": _FAKE_API_KEY},
    )
    assert response.status_code == 200
    body = response.json()
    data = body.get("data", body)
    assert len(data) == 2
    assert data[0]["name"] == "id"
    assert data[1]["comment"] == "user name"


@pytest.mark.asyncio
async def test_list_fields_not_found(client: AsyncClient) -> None:
    response = await client.get(
        "/de2api/mysqlbot/api/datasources/999/tables/orders/fields",
        headers={"X-API-Key": _FAKE_API_KEY},
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /datasources/{id}/query
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_execute_query(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/mysqlbot/api/datasources/1/query",
        json={"sql": "SELECT * FROM orders LIMIT 10"},
        headers={"X-API-Key": _FAKE_API_KEY},
    )
    assert response.status_code == 200
    body = response.json()
    data = body.get("data", body)
    assert data["fields"] == ["id", "name"]
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_execute_query_empty_sql(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/mysqlbot/api/datasources/1/query",
        json={"sql": "  "},
        headers={"X-API-Key": _FAKE_API_KEY},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_execute_query_not_found(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/mysqlbot/api/datasources/999/query",
        json={"sql": "SELECT 1"},
        headers={"X-API-Key": _FAKE_API_KEY},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_execute_query_non_readonly_sql(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/mysqlbot/api/datasources/1/query",
        json={"sql": "DROP TABLE orders"},
        headers={"X-API-Key": _FAKE_API_KEY},
    )
    assert response.status_code == 400
