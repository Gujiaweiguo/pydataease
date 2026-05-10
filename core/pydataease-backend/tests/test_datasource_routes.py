from __future__ import annotations

from datetime import UTC, datetime, timedelta
from collections.abc import Generator

import pytest
from httpx import AsyncClient
from jose import jwt

from app.main import app
from app.schemas.auth import TokenUser
from app.schemas.datasource import (
    DatasourceFieldResponse,
    DatasourceResponse,
    DatasourceTableResponse,
    DatasourceValidateResponse,
    EngineInfoResponse,
)
from app.services.datasource_service import get_datasource_service
from app.settings.config import get_settings


def _build_token(**claims: int) -> str:
    settings = get_settings()
    payload = {
        **claims,
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


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
        return [DatasourceFieldResponse(name="id", data_type="bigint", nullable=False)]

    async def get_engine_info(self) -> EngineInfoResponse:
        return EngineInfoResponse(configured=True, type="postgresql", status="Success", name="postgresql-engine")

    async def upload_file(self, file, id=None, edit_type=None) -> dict:
        return {"sheets": ["Sheet1"], "fileName": "test.xlsx"}


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
    assert field_response.json()["data"] == [{"name": "id", "data_type": "bigint", "nullable": False}]


@pytest.mark.asyncio
async def test_datasource_routes_require_auth(client: AsyncClient) -> None:
    response = await client.get("/de2api/datasource/query/ware")

    assert response.status_code == 401
    assert response.json() == {
        "code": 401,
        "data": None,
        "msg": "token is empty for uri {/de2api/datasource/query/ware}",
    }
