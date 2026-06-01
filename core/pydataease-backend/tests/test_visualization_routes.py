from __future__ import annotations

# pyright: reportMissingTypeArgument=false

from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.chart import ChartResponse  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.visualization import StoreResponse, VisualizationResponse, VisualizationTreeNodeResponse  # pyright: ignore[reportImplicitRelativeImport]
from app.services.visualization_service import get_visualization_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.outer_params_service import get_outer_params_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.linkage_service import get_linkage_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.permission_service import get_permission_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.watermark_service import get_watermark_service  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


class FakeVisualizationService:
    def __init__(self) -> None:
        self.copied: list[tuple[object, TokenUser]] = []
        self.interactive_tree_payloads: list[tuple[object, TokenUser]] = []
        self.store_execute_calls: list[tuple[object, TokenUser]] = []
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

    async def copy(self, payload: object, user: TokenUser) -> str:
        self.copied.append((payload, user))
        return "copied-10"

    async def interactive_tree(self, payload: object, user: TokenUser) -> object:
        self.interactive_tree_payloads.append((payload, user))
        if isinstance(payload, dict) and "busiFlag" not in payload and "busi_flag" not in payload:
            return {key: [{"id": "0", "name": "root", "children": []}] for key in payload}
        return [{"id": "0", "name": "root", "children": []}]

    async def save(self, payload: object, user: TokenUser) -> VisualizationResponse:
        self.saved.append((payload, user))
        return VisualizationResponse(id=11, name="saved", pid=0, node_type="leaf", type="panel")

    async def save_canvas(self, payload: object, user: TokenUser) -> dict[str, object]:
        self.saved.append((payload, user))
        return {"id": "canvas-11", "status": 0}

    async def update(self, payload: object, user: TokenUser) -> VisualizationResponse:
        self.updated.append((payload, user))
        return VisualizationResponse(id=12, name="updated", pid=0, node_type="leaf", type="panel")

    async def update_canvas(self, payload: object, user: TokenUser) -> dict[str, object]:
        self.updated.append((payload, user))
        return {"status": 2}

    async def delete(self, visualization_id: int, user: TokenUser) -> VisualizationResponse:
        self.deleted.append((visualization_id, user))
        return VisualizationResponse(id=visualization_id, name="deleted", pid=0, node_type="leaf", type="panel", delete_flag=True)

    async def delete_logic(self, payload: object, user: TokenUser) -> dict[str, object]:
        self.deleted.append((getattr(payload, "dv_id", 0), user))
        return {"dvId": getattr(payload, "dv_id", None), "busiFlag": getattr(payload, "busi_flag", None), "deleted": True}

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

    async def execute_store(self, payload: object, user: TokenUser) -> StoreResponse:
        self.store_execute_calls.append((payload, user))
        return StoreResponse(resource_id=99, favorited=True)

    async def add_store(self, resource_id: int, resource_type: int, user: TokenUser) -> StoreResponse:
        _ = resource_type, user
        return StoreResponse(resource_id=resource_id, favorited=True)

    async def remove_store(self, resource_id: int, resource_type: int, user: TokenUser) -> StoreResponse:
        _ = resource_type, user
        return StoreResponse(resource_id=resource_id, favorited=False)

    async def query_stores(self, user, keyword=None, type_filter=None, asc=None) -> dict:
        _ = user, keyword, type_filter, asc
        return {"totalCount": 0, "list": []}

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

    async def export_log_stub(self, payload: object | None = None) -> list[object]:
        _ = payload
        return []

    async def get_component_info(self, dv_id: int) -> dict[str, object]:
        _ = dv_id
        return {}

    async def export_to_app_check(self, payload: object | None = None) -> dict[str, str]:
        _ = payload
        return {"status": "ok"}


class FakeLinkageService:
    def __init__(self) -> None:
        self.saved_linkage: list[object] = []
        self.removed_linkage: list[object] = []

    async def get_view_linkage_gather(self, request: object) -> dict[str, object]:
        return {"10": {"targetViewId": 101, "linkageActive": True, "linkageFields": []}}

    async def get_view_linkage_gather_array(self, request: object) -> list[object]:
        return [{"targetViewId": 101, "linkageActive": True, "linkageFields": []}]

    async def save_linkage(self, request: object) -> None:
        self.saved_linkage.append(request)

    async def get_visualization_all_linkage_info(self, dv_id: int, resource_table: str) -> dict[str, list[str]]:
        return {"101#201": ["102#202"]}

    async def update_linkage_active(self, request: object) -> dict[str, list[str]]:
        return {"101#201": ["102#202"]}

    async def remove_linkage(self, request: object) -> None:
        self.removed_linkage.append(request)


class DenyDashboardPermissionService:
    async def require_resource_access(self, user, resource_type: str, permission_type: str = "use") -> None:
        return None

    async def has_resource_permission(self, user, resource_type: str, permission_type: str = "use") -> bool:
        _ = user, permission_type
        return resource_type != "dashboard"

    async def get_effective_menu_ids(self, user_id: int, oid: int) -> set[int]:
        _ = user_id, oid
        return set()


class StrictDenyDashboardPermissionService:
    async def require_resource_access(self, user, resource_type: str, permission_type: str = "use") -> None:
        _ = user, permission_type
        assert resource_type != "dashboard", "dashboard permission should not be required"

    async def has_resource_permission(self, user, resource_type: str, permission_type: str = "use") -> bool:
        _ = user, permission_type
        return resource_type != "dashboard"

    async def get_effective_menu_ids(self, user_id: int, oid: int) -> set[int]:
        _ = user_id, oid
        return set()


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeVisualizationService, None, None]:
    svc = FakeVisualizationService()
    app.dependency_overrides[get_visualization_service] = lambda: svc
    from tests.test_outer_params import FakeOuterParamsService  # pyright: ignore[reportImplicitRelativeImport]
    fake_outer_params = FakeOuterParamsService()
    app.dependency_overrides[get_outer_params_service] = lambda: fake_outer_params
    fake_linkage = FakeLinkageService()
    app.dependency_overrides[get_linkage_service] = lambda: fake_linkage
    from tests.test_watermark import FakeWatermarkService  # pyright: ignore[reportImplicitRelativeImport]
    fake_watermark = FakeWatermarkService()
    app.dependency_overrides[get_watermark_service] = lambda: fake_watermark
    import app.routers.watermark as watermark_router  # pyright: ignore[reportImplicitRelativeImport]
    previous = watermark_router.is_feature_enabled
    watermark_router.is_feature_enabled = AsyncMock(return_value=True)
    yield svc
    _ = app.dependency_overrides.pop(get_visualization_service, None)
    _ = app.dependency_overrides.pop(get_outer_params_service, None)
    _ = app.dependency_overrides.pop(get_linkage_service, None)
    _ = app.dependency_overrides.pop(get_watermark_service, None)
    watermark_router.is_feature_enabled = previous


@pytest.mark.asyncio
async def test_visualization_tree_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post("/de2api/dataVisualization/tree", headers=auth_headers, json={"busiFlag": "dashboard"})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data[0]["children"][0]["leaf"] is True


@pytest.mark.asyncio
async def test_visualization_tree_route_uses_screen_permission_for_datav(
    client, auth_headers: dict[str, str], fake_service: FakeVisualizationService
) -> None:
    app.dependency_overrides[get_permission_service] = lambda: StrictDenyDashboardPermissionService()
    try:
        response = await client.post("/de2api/dataVisualization/tree", headers=auth_headers, json={"busiFlag": "dataV"})
    finally:
        _ = app.dependency_overrides.pop(get_permission_service, None)

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
async def test_visualization_extra_routes(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    copy_resp = await client.post(
        "/de2api/dataVisualization/copy",
        headers=auth_headers,
        json={"id": 10, "name": "dashboard-copy", "pid": 0, "type": "panel", "busiFlag": "dashboard"},
    )
    assert copy_resp.status_code == 200
    assert copy_resp.json()["data"] == "copied-10"

    interactive_resp = await client.post(
        "/de2api/dataVisualization/interactiveTree",
        headers=auth_headers,
        json={"dashboard": {"busiFlag": "dashboard"}},
    )
    assert interactive_resp.status_code == 200
    assert interactive_resp.json()["data"]["dashboard"][0]["id"] == "0"

    for route in (
        "/de2api/dataVisualization/exportLogApp",
        "/de2api/dataVisualization/exportLogTemplate",
        "/de2api/dataVisualization/exportLogPDF",
        "/de2api/dataVisualization/exportLogImg",
    ):
        response = await client.post(route, headers=auth_headers, json={"id": 1})
        assert response.status_code == 200
        assert response.json()["data"] == []

    component_resp = await client.get("/de2api/panel/view/getComponentInfo/22", headers=auth_headers)
    assert component_resp.status_code == 200
    assert component_resp.json()["data"] == {}

    export_check_resp = await client.post(
        "/de2api/dataVisualization/export2AppCheck",
        headers=auth_headers,
        json={"dvId": 22, "viewIds": [1], "dsIds": [2]},
    )
    assert export_check_resp.status_code == 200
    assert export_check_resp.json()["data"]["status"] == "ok"

    execute_resp = await client.post(
        "/de2api/store/execute",
        headers=auth_headers,
        json={"id": 99, "type": "panel"},
    )
    assert execute_resp.status_code == 200
    assert execute_resp.json()["data"]["favorited"] is True


@pytest.mark.asyncio
async def test_visualization_screen_routes_do_not_require_dashboard_permission(
    client, auth_headers: dict[str, str], fake_service: FakeVisualizationService
) -> None:
    app.dependency_overrides[get_permission_service] = lambda: StrictDenyDashboardPermissionService()
    try:
        save_resp = await client.post(
            "/de2api/dataVisualization/save",
            headers=auth_headers,
            json={"name": "screen-new", "pid": 0, "nodeType": "leaf", "type": "screen"},
        )
        update_resp = await client.post(
            "/de2api/dataVisualization/update",
            headers=auth_headers,
            json={"id": 12, "name": "screen-up", "pid": 0, "nodeType": "leaf", "type": "screen"},
        )
        save_canvas_resp = await client.post(
            "/de2api/dataVisualization/saveCanvas",
            headers=auth_headers,
            json={"name": "screen-canvas", "pid": 0, "type": "screen", "canvasViewInfo": {}},
        )
        update_canvas_resp = await client.post(
            "/de2api/dataVisualization/updateCanvas",
            headers=auth_headers,
            json={"id": 12, "name": "screen-canvas-up", "pid": 0, "type": "screen", "canvasViewInfo": {}},
        )
        copy_resp = await client.post(
            "/de2api/dataVisualization/copy",
            headers=auth_headers,
            json={"id": 10, "name": "screen-copy", "pid": 0, "type": "screen", "busiFlag": "screen"},
        )
        delete_resp = await client.post(
            "/de2api/dataVisualization/delete",
            headers=auth_headers,
            json={"id": 12, "busiFlag": "screen"},
        )
        delete_logic_resp = await client.post(
            "/de2api/dataVisualization/deleteLogic/12/screen",
            headers=auth_headers,
        )
    finally:
        _ = app.dependency_overrides.pop(get_permission_service, None)

    assert save_resp.status_code == 200
    assert update_resp.status_code == 200
    assert save_canvas_resp.status_code == 200
    assert update_canvas_resp.status_code == 200
    assert copy_resp.status_code == 200
    assert delete_resp.status_code == 200
    assert delete_logic_resp.status_code == 200


@pytest.mark.asyncio
async def test_interactive_tree_returns_empty_root_branch_when_single_resource_permission_denied(
    client, auth_headers: dict[str, str], fake_service: FakeVisualizationService
) -> None:
    app.dependency_overrides[get_permission_service] = lambda: DenyDashboardPermissionService()
    try:
        response = await client.post(
            "/de2api/dataVisualization/interactiveTree",
            headers=auth_headers,
            json={"busiFlag": "dashboard"},
        )
    finally:
        _ = app.dependency_overrides.pop(get_permission_service, None)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data == [{"id": "0", "name": "root", "pid": -1, "leaf": False, "weight": 7, "extraFlag": 0, "extraFlag1": 0, "children": []}]


@pytest.mark.asyncio
async def test_interactive_tree_returns_empty_root_branch_when_batch_resource_permission_denied(
    client, auth_headers: dict[str, str], fake_service: FakeVisualizationService
) -> None:
    app.dependency_overrides[get_permission_service] = lambda: DenyDashboardPermissionService()
    try:
        response = await client.post(
            "/de2api/dataVisualization/interactiveTree",
            headers=auth_headers,
            json={
                "dashboard": {"busiFlag": "dashboard"},
                "screen": {"busiFlag": "screen"},
            },
        )
    finally:
        _ = app.dependency_overrides.pop(get_permission_service, None)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["dashboard"] == [
        {"id": "0", "name": "root", "pid": -1, "leaf": False, "weight": 7, "extraFlag": 0, "extraFlag1": 0, "children": []}
    ]
    assert data["screen"][0]["id"] == "0"


@pytest.mark.asyncio
async def test_linkage_jump_outer_params_routes(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    linkage_resp = await client.post("/de2api/linkage/getViewLinkageGather", headers=auth_headers, json={"dvId": 10, "viewId": 101})
    assert linkage_resp.status_code == 200
    assert linkage_resp.json()["data"]["viewId"] == 101

    jump_resp = await client.post("/de2api/linkJump/updateJumpSet", headers=auth_headers, json={"dvId": 10, "viewId": 101, "active": True})
    assert jump_resp.status_code == 200
    assert jump_resp.json()["code"] == 0

    outer_resp = await client.post("/de2api/outerParams/updateOuterParamsSet", headers=auth_headers, json={"visualizationId": "10", "outerParamsInfoArray": []})
    assert outer_resp.status_code == 200
    assert outer_resp.json()["code"] == 0


@pytest.mark.asyncio
async def test_visualization_view_detail_and_auth_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.get("/de2api/dataVisualization/viewDetailList/10", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"][0]["sceneId"] == 10

    unauthorized = await client.post("/de2api/dataVisualization/tree", json={"busiFlag": "dashboard"})
    assert unauthorized.status_code == 401


@pytest.mark.asyncio
async def test_watermark_find_with_auth_returns_default(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.get("/de2api/watermark/find", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data is None


@pytest.mark.asyncio
async def test_watermark_find_with_auth_returns_stored(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    # First save watermark config
    await client.post("/de2api/watermark/save", headers=auth_headers, json={"settingContent": '{"type":"custom","content":"logo","enable":true}'})

    response = await client.get("/de2api/watermark/find", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data is not None
    assert data["settingContent"] == '{"type":"custom","content":"logo","enable":true}'


@pytest.mark.asyncio
async def test_watermark_find_without_auth_returns_401(client) -> None:
    response = await client.get("/de2api/watermark/find")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_linkage_save_linkage_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    payload = {
        "dvId": 10,
        "sourceViewId": 101,
        "linkageInfo": [
            {
                "targetViewId": 102,
                "linkageActive": True,
                "linkageFields": [{"sourceField": 201, "targetField": 202}],
            }
        ],
    }
    response = await client.post("/de2api/linkage/saveLinkage", headers=auth_headers, json=payload)
    assert response.status_code == 200
    assert response.json()["data"] is None


@pytest.mark.asyncio
async def test_linkage_get_all_linkage_info_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.get("/de2api/linkage/getVisualizationAllLinkageInfo/10/core", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["code"] == 0


@pytest.mark.asyncio
async def test_linkage_update_active_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    payload = {"dvId": 10, "sourceViewId": 101, "activeStatus": True}
    response = await client.post("/de2api/linkage/updateLinkageActive", headers=auth_headers, json=payload)
    assert response.status_code == 200
    assert response.json()["code"] == 0


@pytest.mark.asyncio
async def test_linkage_remove_linkage_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    payload = {"dvId": 10, "sourceViewId": 101}
    response = await client.post("/de2api/linkage/removeLinkage", headers=auth_headers, json=payload)
    assert response.status_code == 200
    assert response.json()["data"] is None
