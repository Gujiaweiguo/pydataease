from __future__ import annotations

import pytest

from app.services.visualization_service import get_visualization_service
from tests.test_visualization_routes import FakeVisualizationService


@pytest.fixture
def fake_service(install_override) -> FakeVisualizationService:
    service = FakeVisualizationService()
    install_override(get_visualization_service, service)
    return service


@pytest.mark.usefixtures("fake_service")
class TestDataVisualizationContract:
    async def test_find_by_id_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/dataVisualization/findById should accept DataVisualizationBaseRequest and return DataVisualizationVO in ResultMessage.data."""
        response = await async_client.post(
            "/de2api/dataVisualization/findById",
            headers=auth_headers,
            json={"id": 10, "busiFlag": "dashboard"},
        )

        assert response.status_code == 200
        assert response.json()["code"] == 0
        assert response.json()["data"]["componentData"][0]["id"] == "c1"

    async def test_find_by_id_auth_failure_contract(self, async_client) -> None:
        """POST /de2api/dataVisualization/findById should fail when auth token is missing, invalid, or expired."""
        response = await async_client.post("/de2api/dataVisualization/findById", json={"id": 10, "busiFlag": "dashboard"})

        assert response.status_code == 401

    async def test_save_canvas_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/dataVisualization/saveCanvas should save new canvas and return identifier/string payload in ResultMessage.data."""
        response = await async_client.post(
            "/de2api/dataVisualization/save",
            headers=auth_headers,
            json={"name": "new", "pid": 0, "nodeType": "leaf", "type": "panel"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["msg"] == "success"
        assert body["data"]["id"] == 11
        assert body["data"]["name"] == "saved"
        assert body["data"]["pid"] == 0
        assert body["data"]["nodeType"] == "leaf"
        assert body["data"]["type"] == "panel"

    async def test_update_canvas_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/dataVisualization/updateCanvas should update canvas and return DataVisualizationVO in ResultMessage.data."""
        response = await async_client.post(
            "/de2api/dataVisualization/update",
            headers=auth_headers,
            json={"id": 12, "name": "up", "pid": 0, "nodeType": "leaf", "type": "panel"},
        )

        assert response.status_code == 200
        assert response.json()["code"] == 0
        assert response.json()["data"]["name"] == "updated"

    async def test_delete_logic_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/dataVisualization/deleteLogic/{dvId}/{busiFlag} should soft-delete visualization and return success ResultMessage."""
        response = await async_client.post("/de2api/dataVisualization/delete", headers=auth_headers, json={"id": 12})

        assert response.status_code == 200
        assert response.json()["code"] == 0
        assert response.json()["data"]["deleteFlag"] is True


@pytest.mark.usefixtures("fake_service")
class TestVisualizationAuxiliaryContract:
    async def test_link_jump_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/linkJump/updateJumpSet should save visualization jump settings from VisualizationLinkJumpDTO."""
        response = await async_client.post(
            "/de2api/linkJump/updateJumpSet",
            headers=auth_headers,
            json={"dvId": 10, "viewId": 101, "active": True},
        )

        assert response.status_code == 200
        assert response.json() == {"code": 0, "data": {"saved": True}, "msg": "success"}

    async def test_linkage_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/linkage/saveLinkage should save linkage rules from VisualizationLinkageRequest."""
        response = await async_client.post(
            "/de2api/linkage/saveLinkage",
            headers=auth_headers,
            json={"dvId": 10, "viewId": 101},
        )

        assert response.status_code == 200
        assert response.json() == {"code": 0, "data": {"saved": True}, "msg": "success"}

    async def test_outer_params_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/outerParams/updateOuterParamsSet should persist visualization outer params configuration."""
        response = await async_client.post(
            "/de2api/outerParams/updateOuterParamsSet",
            headers=auth_headers,
            json={"dvId": 10, "params": []},
        )

        assert response.status_code == 200
        assert response.json() == {"code": 0, "data": {"saved": True}, "msg": "success"}

    async def test_watermark_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/watermark/save should persist visualization watermark configuration."""
        response = await async_client.post("/de2api/watermark/save", headers=auth_headers, json={"dvId": 10, "settingContent": "watermark-config"})

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["saved"] is True
