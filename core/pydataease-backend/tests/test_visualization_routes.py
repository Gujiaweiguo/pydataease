from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from app.main import app
from app.schemas.auth import TokenUser
from app.schemas.chart import ChartResponse
from app.schemas.visualization import StoreResponse, VisualizationResponse, VisualizationTreeNodeResponse
from app.services.visualization_service import get_visualization_service
from app.settings.config import get_settings


def _build_token(**claims: int) -> str:
    settings = get_settings()
    payload = {**claims, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


class FakeVisualizationService:
    def __init__(self) -> None:
        self.saved: list[tuple[object, TokenUser]] = []
        self.updated: list[tuple[object, TokenUser]] = []
        self.deleted: list[tuple[int, TokenUser]] = []
        self.moved: list[tuple[object, TokenUser]] = []
        self.renamed: list[tuple[object, TokenUser]] = []

    async def tree(self, payload: object) -> list[VisualizationTreeNodeResponse]:
        _ = payload
        return [
            VisualizationTreeNodeResponse(
                id=1,
                name="root",
                pid=0,
                level=0,
                node_type="folder",
                leaf=False,
                children=[VisualizationTreeNodeResponse(id=2, name="leaf", pid=1, level=1, node_type="leaf", leaf=True, children=[])],
            )
        ]

    async def find_by_id(self, payload: object) -> VisualizationResponse:
        _ = payload
        return VisualizationResponse(id=10, name="dashboard", pid=0, node_type="leaf", type="panel", component_data=[{"id": "c1"}], canvas_style_data={"bg": "#fff"})

    async def save(self, payload: object, user: TokenUser) -> VisualizationResponse:
        self.saved.append((payload, user))
        return VisualizationResponse(id=11, name="saved", pid=0, node_type="leaf", type="panel")

    async def update(self, payload: object, user: TokenUser) -> VisualizationResponse:
        self.updated.append((payload, user))
        return VisualizationResponse(id=12, name="updated", pid=0, node_type="leaf", type="panel")

    async def delete(self, visualization_id: int, user: TokenUser) -> VisualizationResponse:
        self.deleted.append((visualization_id, user))
        return VisualizationResponse(id=visualization_id, name="deleted", pid=0, node_type="leaf", type="panel", delete_flag=True)

    async def move(self, payload: object, user: TokenUser) -> VisualizationResponse:
        self.moved.append((payload, user))
        return VisualizationResponse(id=13, name="moved", pid=99, node_type="leaf", type="panel")

    async def rename(self, payload: object, user: TokenUser) -> VisualizationResponse:
        self.renamed.append((payload, user))
        return VisualizationResponse(id=14, name="renamed", pid=0, node_type="leaf", type="panel")

    async def find_recent(self, payload: object) -> list[VisualizationResponse]:
        _ = payload
        return [VisualizationResponse(id=15, name="recent", pid=0, node_type="leaf", type="screen")]

    async def per_resource(self, visualization_id: int) -> VisualizationResponse:
        return VisualizationResponse(id=visualization_id, name="shareable", pid=0, node_type="leaf", type="panel")

    async def view_detail_list(self, visualization_id: int) -> list[ChartResponse]:
        return [ChartResponse(id=101, title="chart", scene_id=visualization_id, table_id=202, type="bar", render="antv")]

    async def favorited(self, resource_id: int, resource_type: int, user: TokenUser) -> StoreResponse:
        _ = resource_type, user
        return StoreResponse(resource_id=resource_id, favorited=True)

    async def add_store(self, resource_id: int, resource_type: int, user: TokenUser) -> StoreResponse:
        _ = resource_type, user
        return StoreResponse(resource_id=resource_id, favorited=True)

    async def remove_store(self, resource_id: int, resource_type: int, user: TokenUser) -> StoreResponse:
        _ = resource_type, user
        return StoreResponse(resource_id=resource_id, favorited=False)

    async def get_view_linkage_gather(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"dvId": 10, "viewId": 101, "config": [{"id": 1}]}

    async def get_view_linkage_gather_array(self, payload: object) -> list[object]:
        _ = payload
        return [{"id": 1}]

    async def save_linkage(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"saved": True}

    async def get_visualization_all_linkage_info(self, dv_id: int, resource_table: str) -> dict[str, object]:
        return {"dvId": dv_id, "resourceTable": resource_table, "config": []}

    async def update_linkage_active(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"active": True}

    async def remove_linkage(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"removed": True}

    async def get_table_field_with_view_id(self, view_id: int) -> list[object]:
        return [{"id": view_id, "name": "region"}]

    async def query_with_view_id(self, dv_id: int, view_id: int) -> dict[str, object]:
        return {"dvId": dv_id, "viewId": view_id}

    async def update_jump_set(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"saved": True}

    async def query_target_visualization_jump_info(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"target": True}

    async def query_visualization_jump_info(self, dv_id: int, resource_table: str) -> dict[str, object]:
        return {"dvId": dv_id, "resourceTable": resource_table}

    async def update_jump_set_active(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"active": True}

    async def remove_jump_set(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"removed": True}

    async def query_with_visualization_id(self, dv_id: int) -> dict[str, object]:
        return {"dvId": dv_id, "params": []}

    async def update_outer_params_set(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"saved": True}

    async def get_outer_params_info(self, dv_id: int) -> dict[str, object]:
        return {"dvId": dv_id, "params": []}

    async def query_ds_with_visualization_id(self, dv_id: int) -> list[dict[str, object]]:
        return [{"datasetId": dv_id}]

    async def save_watermark(self, payload: object) -> dict:
        return {"saved": True}


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeVisualizationService, None, None]:
    svc = FakeVisualizationService()
    app.dependency_overrides[get_visualization_service] = lambda: svc
    yield svc
    _ = app.dependency_overrides.pop(get_visualization_service, None)


@pytest.mark.asyncio
async def test_visualization_tree_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post("/de2api/dataVisualization/tree", headers=auth_headers, json={"busiFlag": "dashboard"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data[0]["children"][0]["leaf"] is True


@pytest.mark.asyncio
async def test_visualization_find_by_id_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post("/de2api/dataVisualization/findById", headers=auth_headers, json={"id": 10, "busiFlag": "dashboard"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["componentData"][0]["id"] == "c1"


@pytest.mark.asyncio
async def test_visualization_save_update_delete_routes(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    save_resp = await client.post("/de2api/dataVisualization/save", headers=auth_headers, json={"name": "new", "pid": 0, "nodeType": "leaf", "type": "panel"})
    assert save_resp.status_code == 200
    assert save_resp.json()["data"]["id"] == 11

    update_resp = await client.post("/de2api/dataVisualization/update", headers=auth_headers, json={"id": 12, "name": "up", "pid": 0, "nodeType": "leaf", "type": "panel"})
    assert update_resp.status_code == 200
    assert update_resp.json()["data"]["name"] == "updated"

    delete_resp = await client.post("/de2api/dataVisualization/delete", headers=auth_headers, json={"id": 12})
    assert delete_resp.status_code == 200
    assert delete_resp.json()["data"]["deleteFlag"] is True


@pytest.mark.asyncio
async def test_visualization_move_and_rename_routes(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    move_resp = await client.post("/de2api/dataVisualization/move", headers=auth_headers, json={"id": 13, "pid": 99})
    assert move_resp.status_code == 200
    assert move_resp.json()["data"]["pid"] == 99

    rename_resp = await client.post("/de2api/dataVisualization/reName", headers=auth_headers, json={"id": 14, "name": "renamed"})
    assert rename_resp.status_code == 200
    assert rename_resp.json()["data"]["name"] == "renamed"


@pytest.mark.asyncio
async def test_visualization_recent_and_per_resource_routes(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    recent_resp = await client.post("/de2api/dataVisualization/findRecent", headers=auth_headers, json={"size": 5})
    assert recent_resp.status_code == 200
    assert recent_resp.json()["data"][0]["id"] == 15

    per_resp = await client.get("/de2api/dataVisualization/perResource/16", headers=auth_headers)
    assert per_resp.status_code == 200
    assert per_resp.json()["data"]["id"] == 16


@pytest.mark.asyncio
async def test_store_routes(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    favorited_resp = await client.post("/de2api/store/favorited", headers=auth_headers, json={"resourceId": 99, "resourceType": 0})
    assert favorited_resp.status_code == 200
    assert favorited_resp.json()["data"]["favorited"] is True

    add_resp = await client.post("/de2api/store/99", headers=auth_headers, json={"resourceType": 0})
    assert add_resp.status_code == 200
    assert add_resp.json()["data"]["favorited"] is True

    del_resp = await client.post("/de2api/store/del/99", headers=auth_headers, json={"resourceType": 0})
    assert del_resp.status_code == 200
    assert del_resp.json()["data"]["favorited"] is False


@pytest.mark.asyncio
async def test_linkage_jump_outer_params_routes(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    linkage_resp = await client.post("/de2api/linkage/getViewLinkageGather", headers=auth_headers, json={"dvId": 10, "viewId": 101})
    assert linkage_resp.status_code == 200
    assert linkage_resp.json()["data"]["viewId"] == 101

    jump_resp = await client.post("/de2api/linkJump/updateJumpSet", headers=auth_headers, json={"dvId": 10, "viewId": 101, "active": True})
    assert jump_resp.status_code == 200
    assert jump_resp.json()["data"]["saved"] is True

    outer_resp = await client.post("/de2api/outerParams/updateOuterParamsSet", headers=auth_headers, json={"dvId": 10, "params": []})
    assert outer_resp.status_code == 200
    assert outer_resp.json()["data"]["saved"] is True


@pytest.mark.asyncio
async def test_visualization_view_detail_and_auth_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.get("/de2api/dataVisualization/viewDetailList/10", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"][0]["sceneId"] == 10

    unauthorized = await client.post("/de2api/dataVisualization/tree", json={"busiFlag": "dashboard"})
    assert unauthorized.status_code == 401
