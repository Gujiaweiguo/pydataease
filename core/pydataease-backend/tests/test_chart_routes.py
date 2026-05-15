from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from app.main import app
from app.schemas.auth import TokenUser
from app.schemas.chart import ChartDetailResponse, ChartFieldResponse, ChartResponse
from app.services.chart_service import get_chart_service
from app.settings.config import get_settings


def _build_token(**claims: int) -> str:
    settings = get_settings()
    payload = {**claims, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


class FakeChartService:
    def __init__(self) -> None:
        self.saved: list[tuple[object, TokenUser]] = []
        self.updated: list[tuple[object, TokenUser]] = []
        self.deleted: list[int] = []

    async def get_by_id(self, chart_id: int) -> ChartResponse:
        return ChartResponse(id=chart_id, title="sales", scene_id=101, table_id=202, type="bar", render="antv")

    async def save(self, payload: object, user: TokenUser) -> ChartResponse:
        self.saved.append((payload, user))
        return ChartResponse(id=9001, title="saved", scene_id=101, table_id=202, type="bar", render="antv")

    async def update(self, payload: object, user: TokenUser) -> ChartResponse:
        self.updated.append((payload, user))
        return ChartResponse(id=9002, title="updated", scene_id=101, table_id=202, type="line", render="antv")

    async def delete(self, chart_id: int) -> None:
        self.deleted.append(chart_id)

    async def get_data(self, payload: object) -> dict[str, object]:
        _ = payload
        return {"fields": [{"name": "region"}], "data": [], "total": 0, "chartId": 123, "sceneId": 456}

    async def get_detail(self, chart_id: int) -> ChartDetailResponse:
        return ChartDetailResponse(
            chart=ChartResponse(id=chart_id, title="detail", scene_id=101, table_id=202, type="pie", render="antv"),
            fields=[ChartFieldResponse(id=1, origin_name="region", name="Region", type="VARCHAR")],
        )

    async def view_detail_list(self, scene_id: int) -> list[ChartResponse]:
        return [ChartResponse(id=scene_id + 1, title="child", scene_id=scene_id, table_id=202, type="bar", render="antv")]

    async def export_details(self, payload: object) -> dict:
        return {"file": "export.xlsx", "status": "SUCCESS"}


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeChartService, None, None]:
    svc = FakeChartService()
    app.dependency_overrides[get_chart_service] = lambda: svc
    yield svc
    _ = app.dependency_overrides.pop(get_chart_service, None)


@pytest.mark.asyncio
async def test_get_chart_route(client, auth_headers: dict[str, str], fake_service: FakeChartService) -> None:
    response = await client.get("/de2api/chart/123", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 123
    assert data["sceneId"] == 101


@pytest.mark.asyncio
async def test_save_chart_route(client, auth_headers: dict[str, str], fake_service: FakeChartService) -> None:
    response = await client.post(
        "/de2api/chart/save",
        headers=auth_headers,
        json={"title": "sales", "sceneId": 101, "tableId": 202, "type": "bar", "render": "antv"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["id"] == 9001
    assert len(fake_service.saved) == 1


@pytest.mark.asyncio
async def test_update_chart_route(client, auth_headers: dict[str, str], fake_service: FakeChartService) -> None:
    response = await client.post(
        "/de2api/chart/update",
        headers=auth_headers,
        json={"id": 9002, "title": "sales-2", "sceneId": 101, "type": "line"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["title"] == "updated"
    assert len(fake_service.updated) == 1


@pytest.mark.asyncio
async def test_delete_chart_route(client, auth_headers: dict[str, str], fake_service: FakeChartService) -> None:
    response = await client.post("/de2api/chart/del/77", headers=auth_headers)
    assert response.status_code == 200
    assert fake_service.deleted == [77]


@pytest.mark.asyncio
async def test_chart_get_data_route(client, auth_headers: dict[str, str], fake_service: FakeChartService) -> None:
    response = await client.post("/de2api/chart/getData", headers=auth_headers, json={"id": 123, "xAxis": [{"name": "region"}]})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["chartId"] == 123
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_chart_get_detail_route(client, auth_headers: dict[str, str], fake_service: FakeChartService) -> None:
    response = await client.get("/de2api/chart/getDetail/33", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["chart"]["id"] == 33
    assert data["fields"][0]["originName"] == "region"


@pytest.mark.asyncio
async def test_chart_view_detail_list_route(client, auth_headers: dict[str, str], fake_service: FakeChartService) -> None:
    response = await client.post("/de2api/chart/viewDetailList", headers=auth_headers, json={"sceneId": 222})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data[0]["sceneId"] == 222


@pytest.mark.asyncio
async def test_chart_route_requires_auth(client) -> None:
    response = await client.get("/de2api/chart/123")
    assert response.status_code == 401
