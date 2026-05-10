from __future__ import annotations

import pytest

from app.services.chart_service import get_chart_service
from tests.test_chart_routes import FakeChartService


@pytest.fixture
def fake_service(install_override) -> FakeChartService:
    service = FakeChartService()
    install_override(get_chart_service, service)
    return service


@pytest.mark.usefixtures("fake_service")
class TestChartViewContract:
    async def test_get_chart_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/chart/getChart/{id} should return ChartViewDTO for the requested chart id."""
        response = await async_client.post("/de2api/chart/getChart/123", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["msg"] == "success"
        assert body["data"]["id"] == 123
        assert body["data"]["title"] == "sales"
        assert body["data"]["sceneId"] == 101
        assert body["data"]["tableId"] == 202
        assert body["data"]["type"] == "bar"
        assert body["data"]["render"] == "antv"

    async def test_get_chart_auth_failure_contract(self, async_client) -> None:
        """POST /de2api/chart/getChart/{id} should fail when auth token is missing, invalid, or expired."""
        response = await async_client.post("/de2api/chart/getChart/123")

        assert response.status_code == 401

    async def test_save_chart_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/chart/save should persist ChartViewDTO and return saved chart payload in ResultMessage.data."""
        response = await async_client.post(
            "/de2api/chart/save",
            headers=auth_headers,
            json={"title": "sales", "sceneId": 101, "tableId": 202, "type": "bar", "render": "antv"},
        )

        assert response.status_code == 200
        assert response.json()["code"] == 0
        assert response.json()["data"]["id"] == 9001

    async def test_save_chart_auth_failure_contract(self, async_client) -> None:
        """POST /de2api/chart/save should fail when auth token is missing, invalid, or expired."""
        response = await async_client.post(
            "/de2api/chart/save",
            json={"title": "sales", "sceneId": 101, "tableId": 202, "type": "bar", "render": "antv"},
        )

        assert response.status_code == 401


@pytest.mark.usefixtures("fake_service")
class TestChartDataContract:
    async def test_get_data_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/chartData/getData should accept ChartViewDTO and return chart query result in ResultMessage.data."""
        response = await async_client.post(
            "/de2api/chartData/getData",
            headers=auth_headers,
            json={"id": 123, "xAxis": [{"name": "region"}]},
        )

        assert response.status_code == 200
        assert response.json() == {
            "code": 0,
            "data": {"fields": [{"name": "region"}], "data": [], "total": 0, "chartId": 123, "sceneId": 456},
            "msg": "success",
        }

    async def test_get_data_auth_failure_contract(self, async_client) -> None:
        """POST /de2api/chartData/getData should fail when auth token is missing, invalid, or expired."""
        response = await async_client.post("/de2api/chartData/getData", json={"id": 123, "xAxis": [{"name": "region"}]})

        assert response.status_code == 401

    @pytest.mark.skip(reason="Endpoint not yet implemented")
    async def test_export_details_success_contract(self) -> None:
        """POST /de2api/chartData/innerExportDetails should return blob/file response for ChartExcelRequest when authorized."""
