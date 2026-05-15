"""T13 Integration Test — Full System Validation.

Validates that all API domains are operational and compatible:
1. Health endpoint works
2. Auth middleware blocks unauthenticated requests
3. Datasource CRUD
4. Dataset tree + CRUD
5. Chart CRUD + getData
6. Visualization tree + CRUD + linkage + jump + outer params
7. Share CRUD + tickets
8. Export tasks CRUD
9. System parameters + menus
10. Task status endpoint
11. WebSocket endpoint exists
"""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.routing import APIWebSocketRoute
from jose import jwt

from app.main import app
from app.services.chart_service import get_chart_service
from app.services.dataset_service import get_dataset_service
from app.services.datasource_service import get_datasource_service
from app.services.export_service import get_export_service
from app.services.share_service import get_share_service
from app.services.menu_service import get_menu_service
from app.services.system_service import get_system_service
from app.services.task_service import get_task_service
from app.services.visualization_service import get_visualization_service
from app.settings.config import get_settings
from tests.test_auth_middleware import _ensure_test_routes
from tests.test_chart_routes import FakeChartService
from tests.test_dataset_routes import FakeDatasetService
from tests.test_datasource_routes import FakeDatasourceService
from tests.test_export_routes import FakeExportService
from tests.test_share_routes import FakeShareService
from tests.test_system_routes import FakeMenuService
from tests.test_system_routes import FakeSystemService
from tests.test_task_routes import FakeTaskService
from tests.test_visualization_routes import FakeVisualizationService

_ensure_test_routes()


def _build_token(**claims: int) -> str:
    settings = get_settings()
    payload = {**claims, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def integrated_fakes() -> Generator[dict[str, object], None, None]:
    services = {
        "datasource": FakeDatasourceService(),
        "dataset": FakeDatasetService(),
        "chart": FakeChartService(),
        "visualization": FakeVisualizationService(),
        "share": FakeShareService(),
        "export": FakeExportService(),
        "system": FakeSystemService(),
        "task": FakeTaskService(),
    }
    overrides = {
        get_datasource_service: lambda: services["datasource"],
        get_dataset_service: lambda: services["dataset"],
        get_chart_service: lambda: services["chart"],
        get_visualization_service: lambda: services["visualization"],
        get_share_service: lambda: services["share"],
        get_export_service: lambda: services["export"],
        get_system_service: lambda: services["system"],
        get_menu_service: lambda: FakeMenuService(),
        get_task_service: lambda: services["task"],
    }
    app.dependency_overrides.update(overrides)
    yield services
    for dependency in overrides:
        _ = app.dependency_overrides.pop(dependency, None)


@pytest.mark.asyncio
async def test_full_system_validation_journey(client, auth_headers: dict[str, str], integrated_fakes: dict[str, object]) -> None:
    health_response = await client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok"}

    unauthorized = await client.get("/de2api/datasource/query/bootstrap")
    assert unauthorized.status_code == 401
    assert unauthorized.json()["code"] == 401

    authorized = await client.get("/de2api/protected/me", headers=auth_headers)
    assert authorized.status_code == 200
    assert authorized.json()["data"] == {"user_id": 7, "oid": 9}

    datasource_save = await client.post(
        "/de2api/datasource/save",
        headers=auth_headers,
        json={
            "name": "warehouse",
            "type": "pg",
            "configuration": {"host": "db", "port": 5432, "username": "demo", "password": "pwd", "database": "analytics", "schema": "public"},
            "description": "created",
        },
    )
    assert datasource_save.status_code == 200
    assert datasource_save.json()["data"]["id"] == 202
    assert len(integrated_fakes["datasource"].saved_payloads) == 1  # type: ignore[attr-defined]

    dataset_tree = await client.post("/de2api/datasetTree/tree", headers=auth_headers, json={"busiFlag": "dataset"})
    assert dataset_tree.status_code == 200
    assert dataset_tree.json()["data"][0]["children"][0]["name"] == "child-dataset"

    dataset_create = await client.post(
        "/de2api/datasetTree/create",
        headers=auth_headers,
        json={"name": "new-dataset", "pid": 0, "nodeType": "folder"},
    )
    assert dataset_create.status_code == 200
    assert dataset_create.json()["data"]["id"] == 100

    chart_save = await client.post(
        "/de2api/chart/save",
        headers=auth_headers,
        json={"title": "sales", "sceneId": 101, "tableId": 202, "type": "bar", "render": "antv"},
    )
    assert chart_save.status_code == 200
    assert chart_save.json()["data"]["id"] == 9001

    chart_data = await client.post(
        "/de2api/chart/getData",
        headers=auth_headers,
        json={"id": 123, "xAxis": [{"name": "region"}]},
    )
    assert chart_data.status_code == 200
    assert chart_data.json()["data"]["chartId"] == 123
    assert chart_data.json()["data"]["fields"][0]["name"] == "region"

    visualization_tree = await client.post(
        "/de2api/dataVisualization/tree",
        headers=auth_headers,
        json={"busiFlag": "dashboard"},
    )
    assert visualization_tree.status_code == 200
    assert visualization_tree.json()["data"][0]["children"][0]["leaf"] is True

    visualization_save = await client.post(
        "/de2api/dataVisualization/save",
        headers=auth_headers,
        json={"name": "new", "pid": 0, "nodeType": "leaf", "type": "panel"},
    )
    assert visualization_save.status_code == 200
    assert visualization_save.json()["data"]["id"] == 11

    linkage = await client.post(
        "/de2api/linkage/getViewLinkageGather",
        headers=auth_headers,
        json={"dvId": 10, "viewId": 101},
    )
    assert linkage.status_code == 200
    assert linkage.json()["data"]["viewId"] == 101

    jump = await client.post(
        "/de2api/linkJump/updateJumpSet",
        headers=auth_headers,
        json={"dvId": 10, "viewId": 101, "active": True},
    )
    assert jump.status_code == 200
    assert jump.json()["data"]["saved"] is True

    outer_params = await client.post(
        "/de2api/outerParams/updateOuterParamsSet",
        headers=auth_headers,
        json={"dvId": 10, "params": []},
    )
    assert outer_params.status_code == 200
    assert outer_params.json()["data"]["saved"] is True

    share_save = await client.post(
        "/de2api/share/save",
        headers=auth_headers,
        json={"resourceId": 200, "autoPwd": True},
    )
    assert share_save.status_code == 200
    assert share_save.json()["data"]["uuid"] == "newshareuuid"

    share_ticket = await client.post(
        "/de2api/share/saveTicket",
        headers=auth_headers,
        json={"uuid": "shareuuid", "ticket": "ticket-abc"},
    )
    assert share_ticket.status_code == 200
    assert share_ticket.json()["data"]["ticket"] == "ticket-abc"

    export_task = await client.post(
        "/de2api/exportCenter/exportTasks/create",
        headers=auth_headers,
        json={"exportFrom": 1, "exportFromType": "dataset", "params": {}},
    )
    assert export_task.status_code == 200
    assert export_task.json()["data"]["exportStatus"] == "INITIATED"

    system_menu = await client.get("/de2api/menu/query", headers=auth_headers)
    assert system_menu.status_code == 200
    assert system_menu.json()["data"][0]["children"][0]["name"] == "datasource"

    task_status = await client.get("/de2api/task/status/task-123", headers=auth_headers)
    assert task_status.status_code == 200
    assert task_status.json()["data"]["exportStatus"] == "RUNNING"

    websocket_routes = [route for route in app.routes if isinstance(route, APIWebSocketRoute)]
    assert any(route.path == "/websocket" for route in websocket_routes)
