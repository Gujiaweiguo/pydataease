from __future__ import annotations

from collections.abc import Generator
from importlib import import_module
from typing import Any

import pytest
from httpx import AsyncClient

from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]

app = import_module("app.main").app
get_dataset_sql_log_service = import_module(
    "app.services.dataset_sql_log_service"
).get_dataset_sql_log_service


class FakeDatasetSqlLogService:
    def __init__(self) -> None:
        self.logs: list[dict[str, Any]] = []
        self.deleted_table_ids: list[str] = []
        self.saved_calls: list[tuple[Any, Any]] = []
        self._counter = 0

    async def save(self, payload: Any, user: Any) -> dict[str, Any]:
        self._counter += 1
        self.saved_calls.append((payload, user))
        entry = {
            "id": str(self._counter),
            "tableId": payload.table_id,
            "sqlSnapshot": payload.sql_snapshot,
            "tableName": payload.table_name,
            "createTime": 1700000000000 + self._counter,
            "createBy": str(user.user_id),
            "status": payload.status,
            "errorMsg": payload.error_msg,
        }
        self.logs.append(entry)
        return entry

    async def list_by_table_id(self, table_id: str) -> list[dict[str, Any]]:
        return [entry for entry in self.logs if entry["tableId"] == table_id]

    async def delete_by_table_id(self, table_id: str) -> None:
        self.deleted_table_ids.append(table_id)
        self.logs = [entry for entry in self.logs if entry["tableId"] != table_id]


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeDatasetSqlLogService, None, None]:
    svc = FakeDatasetSqlLogService()
    app.dependency_overrides[get_dataset_sql_log_service] = lambda: svc
    yield svc
    _ = app.dependency_overrides.pop(get_dataset_sql_log_service, None)


@pytest.mark.asyncio
async def test_dataset_sql_log_save_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetSqlLogService,
) -> None:
    response = await client.post(
        "/de2api/datasetTableSqlLog/save",
        headers=auth_headers,
        json={
            "tableId": "table-1",
            "sqlSnapshot": "SELECT 1",
            "tableName": "orders",
            "status": "SUCCESS",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == "1"
    assert data["tableId"] == "table-1"
    assert data["sqlSnapshot"] == "SELECT 1"
    assert data["status"] == "SUCCESS"
    assert len(fake_service.saved_calls) == 1


@pytest.mark.asyncio
async def test_dataset_sql_log_save_route_captures_error_status(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetSqlLogService,
) -> None:
    response = await client.post(
        "/de2api/datasetTableSqlLog/save",
        headers=auth_headers,
        json={
            "tableId": "table-err",
            "sqlSnapshot": "SELECT * FROM missing_table",
            "tableName": "missing_table",
            "status": "ERROR",
            "errorMsg": "relation does not exist",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "ERROR"
    assert data["errorMsg"] == "relation does not exist"
    assert fake_service.logs[0]["errorMsg"] == "relation does not exist"


@pytest.mark.asyncio
async def test_dataset_sql_log_save_route_accepts_empty_payload(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetSqlLogService,
) -> None:
    response = await client.post(
        "/de2api/datasetTableSqlLog/save",
        headers=auth_headers,
        json={},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == "1"
    assert data["tableId"] is None
    assert data["sqlSnapshot"] is None
    assert data["status"] is None
    assert len(fake_service.logs) == 1


@pytest.mark.asyncio
async def test_dataset_sql_log_save_route_accepts_missing_optional_fields(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetSqlLogService,
) -> None:
    response = await client.post(
        "/de2api/datasetTableSqlLog/save",
        headers=auth_headers,
        json={"tableId": "table-partial"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["tableId"] == "table-partial"
    assert data["sqlSnapshot"] is None
    assert data["tableName"] is None
    assert fake_service.logs[0]["tableId"] == "table-partial"


@pytest.mark.asyncio
async def test_dataset_sql_log_list_by_table_id_returns_saved_logs(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetSqlLogService,
) -> None:
    await client.post(
        "/de2api/datasetTableSqlLog/save",
        headers=auth_headers,
        json={"tableId": "table-list", "sqlSnapshot": "SELECT 1", "status": "SUCCESS"},
    )

    response = await client.post(
        "/de2api/datasetTableSqlLog/listByTableId",
        headers=auth_headers,
        json={"tableId": "table-list"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["tableId"] == "table-list"
    assert data[0]["sqlSnapshot"] == "SELECT 1"
    assert len(fake_service.logs) == 1


@pytest.mark.asyncio
async def test_dataset_sql_log_list_by_empty_table_id_returns_empty_list(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetSqlLogService,
) -> None:
    await client.post(
        "/de2api/datasetTableSqlLog/save",
        headers=auth_headers,
        json={"tableId": "table-filled", "sqlSnapshot": "SELECT 1"},
    )

    response = await client.post(
        "/de2api/datasetTableSqlLog/listByTableId",
        headers=auth_headers,
        json={},
    )

    assert response.status_code == 200
    assert response.json()["data"] == []
    assert len(fake_service.logs) == 1


@pytest.mark.asyncio
async def test_dataset_sql_log_delete_by_table_id_removes_logs(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetSqlLogService,
) -> None:
    await client.post(
        "/de2api/datasetTableSqlLog/save",
        headers=auth_headers,
        json={"tableId": "table-delete", "sqlSnapshot": "SELECT 1"},
    )

    response = await client.post(
        "/de2api/datasetTableSqlLog/deleteByTableId/table-delete",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert fake_service.deleted_table_ids == ["table-delete"]
    assert fake_service.logs == []


@pytest.mark.asyncio
async def test_dataset_sql_log_delete_then_list_returns_empty(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetSqlLogService,
) -> None:
    await client.post(
        "/de2api/datasetTableSqlLog/save",
        headers=auth_headers,
        json={"tableId": "table-cycle", "sqlSnapshot": "SELECT 1"},
    )
    await client.post(
        "/de2api/datasetTableSqlLog/deleteByTableId/table-cycle",
        headers=auth_headers,
    )

    response = await client.post(
        "/de2api/datasetTableSqlLog/listByTableId",
        headers=auth_headers,
        json={"tableId": "table-cycle"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == []
    assert fake_service.deleted_table_ids == ["table-cycle"]


@pytest.mark.asyncio
async def test_dataset_sql_log_save_multiple_logs_and_list_all(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetSqlLogService,
) -> None:
    await client.post(
        "/de2api/datasetTableSqlLog/save",
        headers=auth_headers,
        json={"tableId": "table-multi", "sqlSnapshot": "SELECT 1", "status": "SUCCESS"},
    )
    await client.post(
        "/de2api/datasetTableSqlLog/save",
        headers=auth_headers,
        json={
            "tableId": "table-multi",
            "sqlSnapshot": "SELECT 2",
            "status": "ERROR",
            "errorMsg": "bad sql",
        },
    )

    response = await client.post(
        "/de2api/datasetTableSqlLog/listByTableId",
        headers=auth_headers,
        json={"tableId": "table-multi"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2
    assert [entry["sqlSnapshot"] for entry in data] == ["SELECT 1", "SELECT 2"]
    assert len(fake_service.logs) == 2


@pytest.mark.asyncio
async def test_dataset_sql_log_save_passes_user_info_correctly(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetSqlLogService,
) -> None:
    await client.post(
        "/de2api/datasetTableSqlLog/save",
        headers=auth_headers,
        json={"tableId": "table-user", "sqlSnapshot": "SELECT current_user"},
    )

    payload, user = fake_service.saved_calls[0]
    assert payload.table_id == "table-user"
    assert user.user_id == 7
    assert user.oid == 9
    assert fake_service.logs[0]["createBy"] == "7"


@pytest.mark.asyncio
async def test_dataset_sql_log_delete_nonexistent_table_id_is_ok(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetSqlLogService,
) -> None:
    response = await client.post(
        "/de2api/datasetTableSqlLog/deleteByTableId/missing-table",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert fake_service.deleted_table_ids == ["missing-table"]
    assert fake_service.logs == []


@pytest.mark.asyncio
async def test_dataset_sql_log_save_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/datasetTableSqlLog/save",
        json={"tableId": "table-1", "sqlSnapshot": "SELECT 1"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_sql_log_list_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/datasetTableSqlLog/listByTableId",
        json={"tableId": "table-1"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_sql_log_delete_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasetTableSqlLog/deleteByTableId/table-1")
    assert response.status_code == 401
