from __future__ import annotations

# pyright: reportMissingImports=false

from collections.abc import Generator
from typing import Any

import pytest

from app.main import app  # pyright: ignore[reportMissingImports, reportImplicitRelativeImport]
from app.routers.link_jump import get_link_jump_service  # pyright: ignore[reportMissingImports, reportImplicitRelativeImport]
from app.routers.outer_params import get_outer_params_service  # pyright: ignore[reportMissingImports, reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportMissingImports, reportImplicitRelativeImport]
from app.schemas.chart import ChartResponse  # pyright: ignore[reportMissingImports, reportImplicitRelativeImport]
from app.schemas.visualization import StoreResponse, VisualizationResponse  # pyright: ignore[reportMissingImports, reportImplicitRelativeImport]
from app.services.visualization_service import get_visualization_service  # pyright: ignore[reportMissingImports, reportImplicitRelativeImport]
from tests.test_link_jump import FakeLinkJumpService  # pyright: ignore[reportMissingImports, reportImplicitRelativeImport]
from tests.test_outer_params import FakeOuterParamsService  # pyright: ignore[reportMissingImports, reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportMissingImports, reportImplicitRelativeImport]


def _assert_ok(response) -> dict[str, Any]:
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert body["msg"] in ("", "success")
    assert "data" in body
    return body


class FakeVisualizationService:
    def __init__(self) -> None:
        self.save_canvas_calls: list[tuple[object, TokenUser]] = []
        self.update_canvas_calls: list[tuple[object, TokenUser]] = []
        self.update_base_calls: list[tuple[object, TokenUser]] = []

    async def save_canvas(self, payload: object, user: TokenUser) -> VisualizationResponse:
        self.save_canvas_calls.append((payload, user))
        return VisualizationResponse(
            id=101,
            name="canvas-created",
            pid=0,
            type="dashboard",
            content_id="content-101",
            check_version="v1",
        )

    async def update_canvas(self, payload: object, user: TokenUser) -> VisualizationResponse:
        self.update_canvas_calls.append((payload, user))
        return VisualizationResponse(
            id=102,
            name="canvas-updated",
            pid=1,
            type="dashboard",
            content_id="content-102",
            check_version="v2",
        )

    async def update_base(self, payload: object, user: TokenUser) -> VisualizationResponse:
        self.update_base_calls.append((payload, user))
        return VisualizationResponse(id=103, name="base-updated", pid=2, node_type="folder", type="dashboard")

    async def update_publish_status(self, payload: object, user: TokenUser) -> dict[str, object]:
        _ = payload, user
        return {"published": True, "status": 1}

    async def name_check(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"repeat": False, "msg": "ok"}

    async def check_canvas_change(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"changed": True, "checkVersion": "v2"}

    async def recover_to_published(self, payload: object) -> VisualizationResponse:
        _ = payload
        return VisualizationResponse(id=104, name="published-copy", pid=0, type="dashboard", check_version="published")

    async def delete_logic(self, payload: object, user: TokenUser) -> dict[str, object]:
        _ = user
        return {"dvId": getattr(payload, "dv_id", None), "busiFlag": getattr(payload, "busi_flag", None), "deleted": True}

    async def find_copy_resource(self, dv_id: int, busi_flag: str) -> dict[str, object]:
        return {"id": dv_id, "busiFlag": busi_flag, "copyFrom": 88}

    async def app_canvas_name_check(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"repeat": False, "datasetFolderName": "mobile-folder"}

    async def decompression(self, payload: dict[str, object]) -> dict[str, object]:
        return {"imported": True, "keys": sorted(payload.keys())}

    async def find_dv_type(self, dv_id: int) -> dict[str, object]:
        return {"id": dv_id, "type": "dashboard"}

    async def update_check_version(self, dv_id: int) -> dict[str, object]:
        return {"id": dv_id, "checkVersion": "v3"}

    async def favorited(self, resource_id: int, resource_type: int, user: TokenUser) -> StoreResponse:
        _ = resource_type, user
        return StoreResponse(resource_id=resource_id, favorited=True)

    async def query_stores(self, user: TokenUser, keyword=None, type_filter=None, asc=None) -> dict[str, object]:
        _ = user, keyword, type_filter, asc
        return {"totalCount": 1, "list": [{"resourceId": 301, "favorited": True}]}

    async def get_view_linkage_gather_array(self, payload: object) -> list[dict[str, object]]:
        _ = payload
        return [{"targetViewId": 202, "linkageActive": True, "linkageFields": []}]

    async def get_table_field_with_view_id(self, view_id: int) -> list[dict[str, object]]:
        return [{"id": view_id, "name": "region", "deType": 1}]

    async def query_with_view_id(self, dv_id: int, view_id: int) -> dict[str, object]:
        return {"dvId": dv_id, "viewId": view_id, "active": True}

    async def query_visualization_jump_info(self, dv_id: int, resource_table: str) -> dict[str, object]:
        return {"dvId": dv_id, "resourceTable": resource_table, "jumpInfo": []}

    async def query_target_visualization_jump_info(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"targetDvId": 909, "targets": [{"id": 1}]}

    async def view_detail_list(self, visualization_id: int) -> list[ChartResponse]:
        return [ChartResponse(id=401, title="sales", scene_id=visualization_id, table_id=501, type="bar", render="antv")]

    async def update_jump_set_active(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"active": False, "updated": True}

    async def remove_jump_set(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"removed": True}

    async def query_with_visualization_id(self, dv_id: int) -> dict[str, object]:
        return {"dvId": dv_id, "params": [{"name": "tenant"}]}

    async def get_outer_params_info(self, dv_id: int) -> dict[str, object]:
        return {"dvId": dv_id, "outerParamsInfoArray": [{"key": "tenant"}]}

    async def query_ds_with_visualization_id(self, dv_id: int) -> list[dict[str, object]]:
        return [{"datasetId": dv_id, "datasetName": "orders"}]


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeVisualizationService, None, None]:
    svc = FakeVisualizationService()
    link_jump_svc = FakeLinkJumpService()
    outer_params_svc = FakeOuterParamsService()
    app.dependency_overrides[get_visualization_service] = lambda: svc
    app.dependency_overrides[get_link_jump_service] = lambda: link_jump_svc
    app.dependency_overrides[get_outer_params_service] = lambda: outer_params_svc
    yield svc
    _ = app.dependency_overrides.pop(get_visualization_service, None)
    _ = app.dependency_overrides.pop(get_link_jump_service, None)
    _ = app.dependency_overrides.pop(get_outer_params_service, None)


@pytest.mark.asyncio
async def test_save_canvas_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post(
        "/de2api/dataVisualization/saveCanvas",
        headers=auth_headers,
        json={
            "name": "Executive Dashboard",
            "pid": 0,
            "type": "dashboard",
            "canvasStyleData": "{\"bg\":\"#fff\"}",
            "componentData": "[{\"id\":\"chart-1\"}]",
            "canvasViewInfo": {"chart-1": {"viewId": 901}},
            "mobileLayout": False,
            "watermarkInfo": {"enable": False},
            "checkVersion": "v1",
        },
    )
    body = _assert_ok(response)
    assert body["data"]["id"] == 101
    assert fake_service.save_canvas_calls


@pytest.mark.asyncio
async def test_save_canvas_requires_auth(client, fake_service: FakeVisualizationService) -> None:
    response = await client.post("/de2api/dataVisualization/saveCanvas", json={"name": "Executive Dashboard"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_canvas_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post(
        "/de2api/dataVisualization/updateCanvas",
        headers=auth_headers,
        json={
            "id": 102,
            "name": "Executive Dashboard V2",
            "pid": 1,
            "type": "dashboard",
            "canvasStyleData": "{\"bg\":\"#000\"}",
            "componentData": "[{\"id\":\"chart-2\"}]",
            "canvasViewInfo": {"chart-2": {"viewId": 902}},
            "optType": "update",
            "contentId": "content-102",
            "status": 1,
            "mobileLayout": True,
            "watermarkInfo": {"enable": True},
            "checkVersion": "v2",
        },
    )
    body = _assert_ok(response)
    assert body["data"]["name"] == "canvas-updated"
    assert fake_service.update_canvas_calls


@pytest.mark.asyncio
async def test_update_canvas_requires_auth(client, fake_service: FakeVisualizationService) -> None:
    response = await client.post("/de2api/dataVisualization/updateCanvas", json={"id": 102, "name": "Executive Dashboard V2"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_base_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post(
        "/de2api/dataVisualization/updateBase",
        headers=auth_headers,
        json={"id": 103, "name": "Operations", "pid": 2, "nodeType": "folder", "type": "dashboard", "mobileLayout": False, "status": 1},
    )
    body = _assert_ok(response)
    assert body["data"]["nodeType"] == "folder"
    assert fake_service.update_base_calls


@pytest.mark.asyncio
async def test_update_base_requires_auth(client, fake_service: FakeVisualizationService) -> None:
    response = await client.post("/de2api/dataVisualization/updateBase", json={"id": 103, "name": "Operations"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_publish_status_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post(
        "/de2api/dataVisualization/updatePublishStatus",
        headers=auth_headers,
        json={"id": 104, "status": 1, "activeViewIds": [901, 902]},
    )
    body = _assert_ok(response)
    assert body["data"]["published"] is True


@pytest.mark.asyncio
async def test_name_check_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post(
        "/de2api/dataVisualization/nameCheck",
        headers=auth_headers,
        json={"id": 105, "pid": 0, "name": "Executive Dashboard", "type": "dashboard", "nodeType": "leaf", "opt": "new"},
    )
    body = _assert_ok(response)
    assert body["data"]["repeat"] is False


@pytest.mark.asyncio
async def test_check_canvas_change_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post(
        "/de2api/dataVisualization/checkCanvasChange",
        headers=auth_headers,
        json={"id": 106, "contentId": "content-106", "checkVersion": "v1"},
    )
    body = _assert_ok(response)
    assert body["data"]["changed"] is True


@pytest.mark.asyncio
async def test_recover_to_published_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post(
        "/de2api/dataVisualization/recoverToPublished",
        headers=auth_headers,
        json={"id": 104, "busiFlag": "dashboard"},
    )
    body = _assert_ok(response)
    assert body["data"]["checkVersion"] == "published"


@pytest.mark.asyncio
async def test_delete_logic_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post("/de2api/dataVisualization/deleteLogic/107/dashboard", headers=auth_headers)
    body = _assert_ok(response)
    assert body["data"]["deleted"] is True
    assert body["data"]["dvId"] == 107


@pytest.mark.asyncio
async def test_find_copy_resource_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.get("/de2api/dataVisualization/findCopyResource/108/dashboard", headers=auth_headers)
    body = _assert_ok(response)
    assert body["data"]["copyFrom"] == 88


@pytest.mark.asyncio
async def test_app_canvas_name_check_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post(
        "/de2api/dataVisualization/appCanvasNameCheck",
        headers=auth_headers,
        json={"datasetFolderPid": 11, "datasetFolderName": "mobile-folder"},
    )
    body = _assert_ok(response)
    assert body["data"]["datasetFolderName"] == "mobile-folder"


@pytest.mark.asyncio
async def test_decompression_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post(
        "/de2api/dataVisualization/decompression",
        headers=auth_headers,
        json={"templateId": 9, "name": "template-import", "overwrite": False},
    )
    body = _assert_ok(response)
    assert body["data"]["imported"] is True
    assert body["data"]["keys"] == ["name", "overwrite", "templateId"]


@pytest.mark.asyncio
async def test_find_dv_type_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.get("/de2api/dataVisualization/findDvType/109", headers=auth_headers)
    body = _assert_ok(response)
    assert body["data"]["type"] == "dashboard"


@pytest.mark.asyncio
async def test_update_check_version_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.get("/de2api/dataVisualization/updateCheckVersion/110", headers=auth_headers)
    body = _assert_ok(response)
    assert body["data"]["checkVersion"] == "v3"


@pytest.mark.asyncio
async def test_store_favorited_legacy_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.get("/de2api/store/favorited/301", headers=auth_headers)
    body = _assert_ok(response)
    assert body["data"]["resourceId"] == 301
    assert body["data"]["favorited"] is True


@pytest.mark.asyncio
async def test_store_query_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post("/de2api/store/query", headers=auth_headers, json={"keyword": "sales", "type": "dashboard", "asc": True})
    body = _assert_ok(response)
    assert body["data"]["totalCount"] == 1
    assert body["data"]["list"][0]["resourceId"] == 301


@pytest.mark.asyncio
async def test_linkage_get_view_linkage_gather_array_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post(
        "/de2api/linkage/getViewLinkageGatherArray",
        headers=auth_headers,
        json={"dvId": 111, "viewId": 211, "resourceTable": "core", "config": [], "active": True},
    )
    body = _assert_ok(response)
    assert body["data"][0]["targetViewId"] == 202


@pytest.mark.asyncio
async def test_link_jump_get_table_field_with_view_id_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.get("/de2api/linkJump/getTableFieldWithViewId/212", headers=auth_headers)
    body = _assert_ok(response)
    assert body["data"][0]["name"] == "Column A"


@pytest.mark.asyncio
async def test_link_jump_query_with_view_id_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.get("/de2api/linkJump/queryWithViewId/112/212", headers=auth_headers)
    body = _assert_ok(response)
    assert body["data"]["sourceDvId"] == 112
    assert body["data"]["sourceViewId"] == 212


@pytest.mark.asyncio
async def test_link_jump_query_visualization_jump_info_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.get("/de2api/linkJump/queryVisualizationJumpInfo/113/core", headers=auth_headers)
    body = _assert_ok(response)
    assert "baseJumpInfoMap" in body["data"]


@pytest.mark.asyncio
async def test_link_jump_query_target_visualization_jump_info_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post(
        "/de2api/linkJump/queryTargetVisualizationJumpInfo",
        headers=auth_headers,
        json={"sourceDvId": 114, "sourceViewId": 214, "targetDvId": 909},
    )
    body = _assert_ok(response)
    assert "baseJumpInfoVisualizationMap" in body["data"]


@pytest.mark.asyncio
async def test_link_jump_view_table_detail_list_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.get("/de2api/linkJump/viewTableDetailList/115", headers=auth_headers)
    body = _assert_ok(response)
    assert body["data"]["result"][0]["dvId"] == 115


@pytest.mark.asyncio
async def test_link_jump_update_jump_set_active_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post(
        "/de2api/linkJump/updateJumpSetActive",
        headers=auth_headers,
        json={"sourceDvId": 116, "sourceViewId": 216, "activeStatus": False},
    )
    body = _assert_ok(response)
    assert body["data"]["baseJumpInfoMap"] == {}


@pytest.mark.asyncio
async def test_link_jump_remove_jump_set_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.post(
        "/de2api/linkJump/removeJumpSet",
        headers=auth_headers,
        json={"sourceDvId": 117, "sourceViewId": 217},
    )
    body = _assert_ok(response)
    assert body["data"] is None


@pytest.mark.asyncio
async def test_outer_params_query_with_visualization_id_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.get("/de2api/outerParams/queryWithVisualizationId/118", headers=auth_headers)
    body = _assert_ok(response)
    assert body["data"]["visualizationId"] == "118"
    assert body["data"]["outerParamsInfoArray"][0]["paramName"] == "myParam"


@pytest.mark.asyncio
async def test_outer_params_get_outer_params_info_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.get("/de2api/outerParams/getOuterParamsInfo/119", headers=auth_headers)
    body = _assert_ok(response)
    assert body["data"]["outerParamsInfoMap"]["myParam"] == ["view-100#field-300#strict"]


@pytest.mark.asyncio
async def test_outer_params_query_ds_with_visualization_id_route(client, auth_headers: dict[str, str], fake_service: FakeVisualizationService) -> None:
    response = await client.get("/de2api/outerParams/queryDsWithVisualizationId/120", headers=auth_headers)
    body = _assert_ok(response)
    assert body["data"][0]["name"] == "Test Dataset"
