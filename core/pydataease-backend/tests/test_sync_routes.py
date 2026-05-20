from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.main import app
from tests.fixtures.auth_fixtures import _build_token


EXPECTED_ROUTES = {
    "/de2api/sync/datasource/source/pager/{page}/{limit}": {"POST"},
    "/de2api/sync/datasource/target/pager/{page}/{limit}": {"POST"},
    "/de2api/sync/datasource/latestUse/{sourceType}": {"POST"},
    "/de2api/sync/datasource/validate": {"POST"},
    "/de2api/sync/datasource/getSchema": {"POST"},
    "/de2api/sync/datasource/save": {"POST"},
    "/de2api/sync/datasource/get/{id}": {"GET"},
    "/de2api/sync/datasource/update": {"POST"},
    "/de2api/sync/datasource/delete/{id}": {"POST"},
    "/de2api/sync/datasource/batchDel": {"POST"},
    "/de2api/sync/datasource/fields": {"POST"},
    "/de2api/sync/datasource/validate/{id}": {"GET"},
    "/de2api/sync/datasource/list/{type}": {"GET"},
    "/de2api/sync/task/pager/{page}/{limit}": {"POST"},
    "/de2api/sync/task/execute/{id}": {"GET"},
    "/de2api/sync/task/start/{id}": {"GET"},
    "/de2api/sync/task/stop/{id}": {"GET"},
    "/de2api/sync/task/add": {"POST"},
    "/de2api/sync/task/remove/{taskId}": {"POST"},
    "/de2api/sync/task/batch/del": {"POST"},
    "/de2api/sync/task/update": {"POST"},
    "/de2api/sync/task/get/{taskId}": {"GET"},
    "/de2api/sync/datasource/table/list/{dsId}": {"GET"},
    "/de2api/sync/task/log/pager/{current}/{size}": {"POST"},
    "/de2api/sync/task/log/delete/{logId}": {"POST"},
    "/de2api/sync/task/log/detail/{logId}/{fromLineNum}": {"GET"},
    "/de2api/sync/task/log/clear": {"POST"},
    "/de2api/sync/task/log/terminationTask/{logId}": {"POST"},
    "/de2api/sync/summary/resourceCount": {"POST"},
    "/de2api/sync/summary/logChartData": {"POST"},
}


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def route_paths() -> set[str]:
    return {path for route in app.routes if (path := getattr(route, "path", None)) is not None}


@pytest.fixture
def route_methods() -> dict[str, set[str]]:
    return {
        path: set(getattr(route, "methods", set()))
        for route in app.routes
        if (path := getattr(route, "path", None)) is not None
    }


def test_sync_routes_registered(route_paths: set[str]) -> None:
    assert len(EXPECTED_ROUTES) == 30
    for path in EXPECTED_ROUTES:
        assert path in route_paths


def test_sync_route_methods_match_contract(route_methods: dict[str, set[str]]) -> None:
    for path, methods in EXPECTED_ROUTES.items():
        assert methods.issubset(route_methods[path])


@pytest.mark.asyncio
async def test_sync_source_pager_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/sync/datasource/source/pager/1/10")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_sync_task_execute_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/de2api/sync/task/execute/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_sync_source_pager_returns_empty_page(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.post("/de2api/sync/datasource/source/pager/1/10", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"code": 0, "data": {"items": [], "total": 0}, "msg": "success"}


@pytest.mark.asyncio
async def test_sync_datasource_validate_returns_invalid(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.post("/de2api/sync/datasource/validate", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"] == {"valid": False}


@pytest.mark.asyncio
async def test_sync_task_log_detail_returns_empty_content(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.get("/de2api/sync/task/log/detail/1/0", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"] == {"logContent": "", "end": True}


@pytest.mark.asyncio
async def test_sync_summary_resource_count_returns_zeroes(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.post("/de2api/sync/summary/resourceCount", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"] == {"taskCount": 0, "sourceCount": 0}
