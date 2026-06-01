from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.main import app
from app.services.sys_variable_service import get_sys_variable_service
from tests.fixtures.auth_fixtures import _build_token


class FakeSysVariableService:
    def __init__(self) -> None:
        self.created_payload = None
        self.page_payload = None
        self.page_args = None
        self.batch_deleted_ids = None

    async def create(self, payload, user) -> dict[str, object]:
        self.created_payload = payload.model_dump(by_alias=True)
        return {"id": 101, **self.created_payload, "createBy": user.user_id, "createTime": 1, "updateTime": 1}

    async def edit(self, payload) -> dict[str, object]:
        data = payload.model_dump(by_alias=True)
        return {**data, "createBy": 7, "createTime": 1, "updateTime": 2}

    async def detail(self, variable_id: int) -> dict[str, object]:
        return {
            "id": variable_id,
            "name": "city",
            "alias": "城市",
            "type": "TEXT",
            "remark": "demo",
            "datasetGroupId": 10,
            "datasetTableId": 11,
            "createBy": 7,
            "createTime": 1,
            "updateTime": 2,
        }

    async def delete(self, variable_id: int) -> None:
        return None

    async def query(self, payload) -> list[dict[str, object]]:
        keyword = None if payload is None else payload.keyword
        return [{"id": 101, "name": keyword or "city", "alias": "城市", "type": "TEXT", "remark": None, "datasetGroupId": None, "datasetTableId": None, "createBy": 7, "createTime": 1, "updateTime": 1}]

    async def value_page(self, page: int, limit: int, payload) -> dict[str, object]:
        self.page_args = (page, limit)
        self.page_payload = None if payload is None else payload.model_dump(by_alias=True)
        return {
            "records": [
                {"id": 201, "variableId": 101, "value": "beijing", "name": "北京", "remark": None, "createTime": 1, "updateTime": 1}
            ],
            "total": 1,
            "page": page,
            "pageSize": limit,
        }

    async def value_list(self, variable_id: int) -> list[dict[str, object]]:
        return [{"id": 201, "variableId": variable_id, "value": "beijing", "name": "北京", "remark": None, "createTime": 1, "updateTime": 1}]

    async def create_value(self, payload) -> dict[str, object]:
        data = payload.model_dump(by_alias=True)
        return {"id": 202, **data, "createTime": 1, "updateTime": 1}

    async def edit_value(self, payload) -> dict[str, object]:
        data = payload.model_dump(by_alias=True)
        return {**data, "createTime": 1, "updateTime": 2}

    async def delete_value(self, value_id: int) -> None:
        return None

    async def batch_delete_values(self, payload) -> None:
        self.batch_deleted_ids = payload.ids


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeSysVariableService, None, None]:
    svc = FakeSysVariableService()
    app.dependency_overrides[get_sys_variable_service] = lambda: svc
    import app.routers.sys_variable as sys_variable_router  # pyright: ignore[reportImplicitRelativeImport]
    feature_check = AsyncMock(return_value=True)
    previous = sys_variable_router.is_feature_enabled
    sys_variable_router.is_feature_enabled = feature_check
    yield svc
    _ = app.dependency_overrides.pop(get_sys_variable_service, None)
    sys_variable_router.is_feature_enabled = previous


@pytest.fixture
def route_paths() -> set[str]:
    return {getattr(route, "path", "") for route in app.routes}


def api_path(path: str) -> str:
    return f"/de2api{path}"


def test_sys_variable_routes_registered(route_paths: set[str]) -> None:
    expected = {
        "/sysVariable/create",
        "/sysVariable/edit",
        "/sysVariable/detail/{id}",
        "/sysVariable/delete/{id}",
        "/sysVariable/query",
        "/sysVariable/value/selected/{page}/{limit}",
        "/sysVariable/value/selected/{id}",
        "/sysVariable/value/create",
        "/sysVariable/value/edit",
        "/sysVariable/value/delete/{id}",
        "/sysVariable/value/batchDel",
    }
    for path in expected:
        assert api_path(path) in route_paths


@pytest.mark.asyncio
async def test_create_variable_returns_wrapped_payload(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeSysVariableService,
) -> None:
    response = await client.post(
        "/de2api/sysVariable/create",
        headers=auth_headers,
        json={"name": "city", "alias": "城市", "type": "TEXT", "datasetGroupId": 10},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["data"]["name"] == "city"
    assert fake_service.created_payload is not None
    assert fake_service.created_payload["datasetGroupId"] == 10


@pytest.mark.asyncio
async def test_query_variable_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/sysVariable/query", json={"keyword": "city"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_variable_detail_returns_wrapped_success(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeSysVariableService,
) -> None:
    response = await client.get("/de2api/sysVariable/detail/7", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "code": 0,
        "data": {
            "id": 7,
            "name": "city",
            "alias": "城市",
            "type": "TEXT",
            "remark": "demo",
            "datasetGroupId": 10,
            "datasetTableId": 11,
            "createBy": 7,
            "createTime": 1,
            "updateTime": 2,
        },
        "msg": "success",
    }


@pytest.mark.asyncio
async def test_value_page_uses_path_and_body(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeSysVariableService,
) -> None:
    response = await client.post(
        "/de2api/sysVariable/value/selected/2/20",
        headers=auth_headers,
        json={"variableId": 101, "keyword": "bei"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["page"] == 2
    assert body["data"]["pageSize"] == 20
    assert fake_service.page_args == (2, 20)
    assert fake_service.page_payload == {"variableId": 101, "keyword": "bei"}


@pytest.mark.asyncio
async def test_batch_delete_values_accepts_ids(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeSysVariableService,
) -> None:
    response = await client.post(
        "/de2api/sysVariable/value/batchDel",
        headers=auth_headers,
        json={"ids": [3, 4]},
    )
    assert response.status_code == 200
    assert response.json() == {"code": 0, "data": None, "msg": "success"}
    assert fake_service.batch_deleted_ids == [3, 4]
