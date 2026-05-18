from __future__ import annotations

# pyright: reportMissingTypeArgument=false, reportCallIssue=false, reportIncompatibleMethodOverride=false, reportMissingImports=false

from collections.abc import Generator

import pytest
from httpx import AsyncClient

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.datasource import DatasourceFieldResponse, DatasourceResponse, DatasourceTableResponse, DatasourceValidateResponse, EngineInfoResponse  # pyright: ignore[reportImplicitRelativeImport]
from app.services.datasource_service import get_datasource_service  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


class FakeDatasourceService:
    def __init__(self) -> None:
        self.saved_payloads: list[tuple[object, TokenUser]] = []
        self.updated_payloads: list[tuple[object, TokenUser]] = []
        self.deleted_ids: list[int] = []

    async def query(self, keyword: str) -> list[DatasourceResponse]:
        return [
            DatasourceResponse(
                id=101,
                name=f"{keyword}-warehouse",
                type="pg",
                configuration={"host": "db", "database": "analytics", "schema": "public"},
                description="main datasource",
                pid=0,
                edit_type=None,
                create_time=1,
                update_time=2,
                update_by=7,
                create_by="7",
                status="Success",
                qrtz_instance=None,
                task_status="WaitingForExecution",
                enable_data_fill=False,
            )
        ]

    async def save(self, payload: object, user: TokenUser) -> DatasourceResponse:
        self.saved_payloads.append((payload, user))
        return DatasourceResponse(
            id=202,
            name="warehouse",
            type="pg",
            configuration={"host": "db", "database": "analytics", "schema": "public"},
            description="created",
            pid=0,
            edit_type=None,
            create_time=10,
            update_time=10,
            update_by=user.user_id,
            create_by=str(user.user_id),
            status="Success",
            qrtz_instance=None,
            task_status="WaitingForExecution",
            enable_data_fill=False,
        )

    async def update(self, payload: object, user: TokenUser) -> DatasourceResponse:
        self.updated_payloads.append((payload, user))
        return DatasourceResponse(
            id=202,
            name="warehouse-updated",
            type="pg",
            configuration={"host": "db", "database": "analytics", "schema": "public"},
            description="updated",
            pid=0,
            edit_type=None,
            create_time=10,
            update_time=20,
            update_by=user.user_id,
            create_by=str(user.user_id),
            status="Success",
            qrtz_instance=None,
            task_status="WaitingForExecution",
            enable_data_fill=False,
        )

    async def delete(self, datasource_id: int) -> None:
        self.deleted_ids.append(datasource_id)

    async def validate(self, payload: object) -> DatasourceValidateResponse:
        return DatasourceValidateResponse(success=True, message="Connection successful", datasource_type="pg")

    async def get_tables(self, datasource_id: int) -> list[DatasourceTableResponse]:
        return [DatasourceTableResponse(name="orders", schema_name="public")]

    async def get_fields(self, datasource_id: int, table_name: str) -> list[DatasourceFieldResponse]:
        return [DatasourceFieldResponse(name="id", origin_name="id", data_type="bigint", de_type=2, type="bigint", nullable=False)]

    async def get_engine_info(self) -> EngineInfoResponse:
        return EngineInfoResponse(configured=True, type="postgresql", status="Success", name="postgresql-engine")

    async def upload_file(self, file, id=None, edit_type=None) -> dict:
        return {"sheets": ["Sheet1"], "fileName": "test.xlsx"}


class FakeDecoratedDatasourceService(FakeDatasourceService):
    async def save(self, payload: object, user: TokenUser) -> dict[str, object]:
        self.saved_payloads.append((payload, user))
        return {
            "id": 303,
            "name": "api-ds",
            "type": "API",
            "configuration": {},
            "apiConfigurationStr": [{"name": "orders", "type": "table"}],
            "paramsStr": [{"name": "runtime", "type": "params"}],
            "syncSetting": {"syncRate": "SIMPLE_CRON"},
        }

    async def update(self, payload: object, user: TokenUser) -> dict[str, object]:
        self.updated_payloads.append((payload, user))
        return {
            "id": 303,
            "name": "excel-remote",
            "type": "ExcelRemote",
            "configuration": {"sheets": []},
            "syncSetting": {"syncRate": "SIMPLE_CRON"},
            "fileName": "orders.xlsx",
            "size": 12,
        }


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeDatasourceService, None, None]:
    service = FakeDatasourceService()
    app.dependency_overrides[get_datasource_service] = lambda: service
    yield service
    _ = app.dependency_overrides.pop(get_datasource_service, None)


@pytest.mark.asyncio
async def test_datasource_query_save_update_delete_and_engine_routes(
    client: AsyncClient, auth_headers: dict[str, str], fake_service: FakeDatasourceService
) -> None:
    query_response = await client.get("/de2api/datasource/query/ware", headers=auth_headers)
    save_response = await client.post(
        "/de2api/datasource/save",
        headers=auth_headers,
        json={
            "name": "warehouse",
            "type": "pg",
            "configuration": {"host": "db", "port": 5432, "username": "demo", "password": "pwd", "database": "analytics", "schema": "public"},
            "description": "created",
        },
    )
    update_response = await client.post(
        "/de2api/datasource/update",
        headers=auth_headers,
        json={
            "id": 202,
            "name": "warehouse-updated",
            "configuration": {"host": "db", "port": 5432, "username": "demo", "password": "pwd", "database": "analytics", "schema": "public"},
        },
    )
    delete_response = await client.post("/de2api/datasource/delete/202", headers=auth_headers)
    engine_response = await client.get("/de2api/engine/info", headers=auth_headers)

    assert query_response.status_code == 200
    assert query_response.json()["data"][0]["name"] == "ware-warehouse"
    assert save_response.status_code == 200
    assert save_response.json()["data"]["id"] == 202
    assert update_response.status_code == 200
    assert update_response.json()["data"]["name"] == "warehouse-updated"
    assert delete_response.status_code == 200
    assert delete_response.json() == {"code": 0, "data": None, "msg": "success"}
    assert engine_response.status_code == 200
    assert engine_response.json()["data"] == {
        "configured": True,
        "type": "postgresql",
        "status": "Success",
        "name": "postgresql-engine",
    }
    assert fake_service.deleted_ids == [202]


@pytest.mark.asyncio
async def test_datasource_validate_tables_and_fields_routes(
    client: AsyncClient, auth_headers: dict[str, str], fake_service: FakeDatasourceService
) -> None:
    validate_response = await client.post(
        "/de2api/datasource/validate",
        headers=auth_headers,
        json={
            "name": "warehouse",
            "type": "pg",
            "configuration": {"host": "db", "port": 5432, "username": "demo", "password": "pwd", "database": "analytics", "schema": "public"},
        },
    )
    schema_response = await client.get("/de2api/datasource/getSchema/202", headers=auth_headers)
    field_response = await client.get("/de2api/datasource/getTableField/202/orders", headers=auth_headers)

    assert validate_response.status_code == 200
    assert validate_response.json()["data"] == {
        "success": True,
        "message": "Connection successful",
        "datasource_type": "pg",
    }
    assert schema_response.json()["data"] == [{"name": "orders", "schema": "public", "type": "TABLE"}]
    assert field_response.json()["data"] == [{"name": "id", "originName": "id", "fieldType": "bigint", "deType": 2, "type": "bigint", "nullable": False}]


@pytest.mark.asyncio
async def test_datasource_routes_require_auth(client: AsyncClient) -> None:
    response = await client.get("/de2api/datasource/query/ware")

    assert response.status_code == 401
    assert response.json() == {
        "code": 401,
        "data": None,
        "msg": "token is empty for uri {/de2api/datasource/query/ware}",
    }


@pytest.mark.asyncio
async def test_datasource_save_update_preserve_decorated_contract(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    service = FakeDecoratedDatasourceService()
    app.dependency_overrides[get_datasource_service] = lambda: service
    try:
        save_response = await client.post(
            "/de2api/datasource/save",
            headers=auth_headers,
            json={
                "name": "api-ds",
                "type": "API",
                "configuration": "W3sibmFtZSI6ICJvcmRlcnMiLCAidHlwZSI6ICJ0YWJsZSJ9XQ==",
                "syncSetting": {"syncRate": "SIMPLE_CRON"},
            },
        )
        update_response = await client.post(
            "/de2api/datasource/update",
            headers=auth_headers,
            json={
                "id": 303,
                "name": "excel-remote",
                "type": "ExcelRemote",
                "configuration": "W3sidGFibGVOYW1lIjogIm9yZGVycyJ9XQ==",
                "syncSetting": {"syncRate": "SIMPLE_CRON"},
            },
        )
    finally:
        _ = app.dependency_overrides.pop(get_datasource_service, None)

    assert save_response.status_code == 200
    save_data = save_response.json()["data"]
    assert save_data["configuration"] == {}
    assert save_data["apiConfigurationStr"] == [{"name": "orders", "type": "table"}]
    assert save_data["paramsStr"] == [{"name": "runtime", "type": "params"}]
    assert save_data["syncSetting"] == {"syncRate": "SIMPLE_CRON"}

    assert update_response.status_code == 200
    update_data = update_response.json()["data"]
    assert update_data["type"] == "ExcelRemote"
    assert update_data["syncSetting"] == {"syncRate": "SIMPLE_CRON"}
    assert update_data["fileName"] == "orders.xlsx"
    assert update_data["size"] == 12


@pytest.mark.asyncio
async def test_datasource_save_accepts_blank_copy_id_payload(
    client: AsyncClient, auth_headers: dict[str, str], fake_service: FakeDatasourceService
) -> None:
    response = await client.post(
        "/de2api/datasource/save",
        headers=auth_headers,
        json={
            "id": "",
            "name": "demo-pg-copy-e2e",
            "type": "pg",
            "pid": "0",
            "configuration": "eyJob3N0IjoibG9jYWxob3N0IiwicG9ydCI6NTQzMiwic2NoZW1hIjoicHVibGljIiwic3NoVHlwZSI6InBhc3N3b3JkIiwidXJsVHlwZSI6Imhvc3ROYW1lIiwiZGF0YUJhc2UiOiJkYXRhZWFzZSIsInBhc3N3b3JkIjoiZGF0YWVhc2UiLCJ1c2VybmFtZSI6ImRhdGFlYXNlIn0=",
            "copy": True,
        },
    )

    assert response.status_code == 200
    assert len(fake_service.saved_payloads) == 1
    payload, _ = fake_service.saved_payloads[0]
    assert getattr(payload, "id") is None
    assert getattr(payload, "pid") == 0


@pytest.mark.asyncio
async def test_datasource_save_accepts_numeric_edit_type_for_excel(
    client: AsyncClient, auth_headers: dict[str, str], fake_service: FakeDatasourceService
) -> None:
    response = await client.post(
        "/de2api/datasource/save",
        headers=auth_headers,
        json={
            "name": "excel-local-e2e",
            "type": "Excel",
            "editType": 0,
            "configuration": "W3sic2hlZXRJZCI6IjEiLCJ0YWJsZU5hbWUiOiJvcmRlcnMiLCJmaWVsZHMiOltdLCJqc29uQXJyYXkiOltdfV0=",
        },
    )

    assert response.status_code == 200
    assert len(fake_service.saved_payloads) == 1
    payload, _ = fake_service.saved_payloads[0]
    assert getattr(payload, "edit_type") == "0"


@pytest.mark.asyncio
async def test_datasource_delete_conflict_is_exposed(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    class ConflictDatasourceService(FakeDatasourceService):
        async def delete(self, datasource_id: int) -> None:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Datasource is still referenced by datasets and cannot be deleted",
            )

    service = ConflictDatasourceService()
    app.dependency_overrides[get_datasource_service] = lambda: service
    try:
        response = await client.post("/de2api/datasource/delete/999", headers=auth_headers)
    finally:
        _ = app.dependency_overrides.pop(get_datasource_service, None)

    assert response.status_code == 409
