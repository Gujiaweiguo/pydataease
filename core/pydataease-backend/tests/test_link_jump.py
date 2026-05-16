"""Tests for VisualizationLinkJump API endpoints.

Uses fake service injection pattern (same as test_dataset_field_routes).
All 8 endpoints are tested via httpx AsyncClient against the FastAPI app.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from jose import jwt

from app.main import app
from app.routers.link_jump import get_link_jump_service
from app.schemas.link_jump import (
    DatasetTableFieldDTO,
    LinkJumpBaseRequest,
    LinkJumpBaseResponse,
    LinkJumpInfoDTO,
    LinkJumpTargetViewInfo,
    OutParamsJumpDTO,
    ViewTableDetailDTO,
    ViewTableFieldDTO,
    VisualizationComponentDTO,
    VisualizationLinkJumpDTO,
)
from app.settings.config import get_settings


def _build_token(user_id: int = 1) -> str:
    settings = get_settings()
    payload = {"uid": user_id, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


class FakeLinkJumpService:
    """Fake service that records calls and returns predictable data."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    async def get_table_field_with_view_id(
        self, view_id: int
    ) -> list[DatasetTableFieldDTO]:
        self.calls.append(("get_table_field_with_view_id", {"view_id": view_id}))
        return [
            DatasetTableFieldDTO(
                id=1001, origin_name="col_a", name="Column A", type="VARCHAR", de_type=0
            ),
            DatasetTableFieldDTO(
                id=1002, origin_name="col_b", name="Column B", type="BIGINT", de_type=2
            ),
        ]

    async def query_with_view_id(
        self, dv_id: int, view_id: int, uid: int, resource_table: str = "core"
    ) -> VisualizationLinkJumpDTO | None:
        self.calls.append(
            (
                "query_with_view_id",
                {"dv_id": dv_id, "view_id": view_id, "uid": uid},
            )
        )
        return VisualizationLinkJumpDTO(
            id=9001,
            source_dv_id=dv_id,
            source_view_id=view_id,
            link_jump_info=None,
            checked=True,
            link_jump_info_array=[
                LinkJumpInfoDTO(
                    id=8001,
                    link_jump_id=9001,
                    link_type="inner",
                    jump_type="_blank",
                    window_size="middle",
                    target_dv_id=5001,
                    source_field_id=1001,
                    content=None,
                    checked=True,
                    attach_params=False,
                    target_view_info_list=[
                        LinkJumpTargetViewInfo(
                            target_id=7001,
                            link_jump_info_id=8001,
                            source_field_active_id=1001,
                            target_view_id="2001",
                            target_field_id="3001",
                            target_type="view",
                        )
                    ],
                )
            ],
        )

    async def query_visualization_jump_info(
        self, dv_id: int, uid: int, resource_table: str = "core"
    ) -> LinkJumpBaseResponse:
        self.calls.append(
            (
                "query_visualization_jump_info",
                {"dv_id": dv_id, "uid": uid, "resource_table": resource_table},
            )
        )
        return LinkJumpBaseResponse(
            base_jump_info_map={
                "4001#1001": LinkJumpInfoDTO(
                    id=8001,
                    link_type="inner",
                    checked=True,
                    target_dv_id=5001,
                    source_field_id=1001,
                )
            },
            base_jump_info_visualization_map=None,
        )

    async def update_jump_set(self, jump_dto: VisualizationLinkJumpDTO) -> None:
        self.calls.append(
            ("update_jump_set", {"source_dv_id": jump_dto.source_dv_id, "source_view_id": jump_dto.source_view_id})
        )

    async def query_target_visualization_jump_info(
        self, request: LinkJumpBaseRequest
    ) -> LinkJumpBaseResponse:
        self.calls.append(
            (
                "query_target_visualization_jump_info",
                {"source_dv_id": request.source_dv_id, "target_dv_id": request.target_dv_id},
            )
        )
        return LinkJumpBaseResponse(
            base_jump_info_map=None,
            base_jump_info_visualization_map={
                "4001#1001#1001": ["2001#3001"]
            },
        )

    async def view_table_detail_list(
        self, dv_id: int
    ) -> VisualizationComponentDTO:
        self.calls.append(("view_table_detail_list", {"dv_id": dv_id}))
        return VisualizationComponentDTO(
            component_data='[{"id":"chart1"}]',
            result=[
                ViewTableDetailDTO(
                    id=4001,
                    title="Chart 1",
                    type="bar",
                    dv_id=dv_id,
                    table_fields=[
                        ViewTableFieldDTO(
                            id=1001, origin_name="col_a", name="Column A", type="VARCHAR", de_type=0
                        )
                    ],
                )
            ],
            out_params_jump_info=[
                OutParamsJumpDTO(id="op1", name="param1", title="param1", type="outerParams")
            ],
        )

    async def update_jump_set_active(
        self, request: LinkJumpBaseRequest, uid: int
    ) -> LinkJumpBaseResponse:
        self.calls.append(
            (
                "update_jump_set_active",
                {"source_dv_id": request.source_dv_id, "active_status": request.active_status},
            )
        )
        return LinkJumpBaseResponse(
            base_jump_info_map={},
            base_jump_info_visualization_map=None,
        )

    async def remove_jump_set(self, jump_dto: VisualizationLinkJumpDTO) -> None:
        self.calls.append(
            ("remove_jump_set", {"source_dv_id": jump_dto.source_dv_id, "source_view_id": jump_dto.source_view_id})
        )


@pytest.fixture
def fake_service():
    return FakeLinkJumpService()


@pytest.fixture(autouse=True)
def override_service(fake_service):
    app.dependency_overrides[get_link_jump_service] = lambda: fake_service
    yield
    app.dependency_overrides.pop(get_link_jump_service, None)


@pytest.fixture
def auth_headers():
    return {"X-DE-TOKEN": _build_token(user_id=1)}


@pytest.fixture
async def client():
    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# --- Tests ---


async def test_get_table_field_with_view_id(client: AsyncClient, auth_headers: dict, fake_service: FakeLinkJumpService):
    """EP 1: GET /linkJump/getTableFieldWithViewId/{viewId}"""
    response = await client.get(
        "/de2api/linkJump/getTableFieldWithViewId/4001",
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    # ResultMessage wraps: {"code": 0, "data": ..., "msg": ""}
    assert body["code"] == 0
    data = body["data"]
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["id"] == 1001
    assert data[0]["name"] == "Column A"
    assert fake_service.calls[0][0] == "get_table_field_with_view_id"


async def test_query_with_view_id(client: AsyncClient, auth_headers: dict, fake_service: FakeLinkJumpService):
    """EP 2: GET /linkJump/queryWithViewId/{dvId}/{viewId}"""
    response = await client.get(
        "/de2api/linkJump/queryWithViewId/5001/4001",
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    data = body["data"]
    assert data is not None
    assert data["sourceDvId"] == 5001
    assert data["sourceViewId"] == 4001
    assert data["checked"] is True
    assert len(data["linkJumpInfoArray"]) == 1
    assert data["linkJumpInfoArray"][0]["linkType"] == "inner"
    assert fake_service.calls[0][0] == "query_with_view_id"


async def test_query_visualization_jump_info(client: AsyncClient, auth_headers: dict, fake_service: FakeLinkJumpService):
    """EP 3: GET /linkJump/queryVisualizationJumpInfo/{dvId}/{resourceTable}"""
    response = await client.get(
        "/de2api/linkJump/queryVisualizationJumpInfo/5001/core",
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    data = body["data"]
    assert "baseJumpInfoMap" in data
    assert "4001#1001" in data["baseJumpInfoMap"]
    assert data["baseJumpInfoMap"]["4001#1001"]["linkType"] == "inner"
    assert fake_service.calls[0][0] == "query_visualization_jump_info"


async def test_update_jump_set(client: AsyncClient, auth_headers: dict, fake_service: FakeLinkJumpService):
    """EP 4: POST /linkJump/updateJumpSet"""
    payload = {
        "sourceDvId": 5001,
        "sourceViewId": 4001,
        "checked": True,
        "linkJumpInfoArray": [
            {
                "linkType": "inner",
                "jumpType": "_blank",
                "windowSize": "middle",
                "targetDvId": 5002,
                "sourceFieldId": 1001,
                "checked": True,
                "attachParams": False,
                "targetViewInfoList": [
                    {
                        "sourceFieldActiveId": 1001,
                        "targetViewId": "2001",
                        "targetFieldId": "3001",
                        "targetType": "view",
                    }
                ],
            }
        ],
    }
    response = await client.post(
        "/de2api/linkJump/updateJumpSet",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert fake_service.calls[0][0] == "update_jump_set"
    assert fake_service.calls[0][1]["source_dv_id"] == 5001
    assert fake_service.calls[0][1]["source_view_id"] == 4001


async def test_query_target_visualization_jump_info(
    client: AsyncClient, auth_headers: dict, fake_service: FakeLinkJumpService
):
    """EP 5: POST /linkJump/queryTargetVisualizationJumpInfo"""
    payload = {
        "sourceDvId": 5001,
        "sourceViewId": 4001,
        "targetDvId": 5002,
    }
    response = await client.post(
        "/de2api/linkJump/queryTargetVisualizationJumpInfo",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    data = body["data"]
    assert "baseJumpInfoVisualizationMap" in data
    assert "4001#1001#1001" in data["baseJumpInfoVisualizationMap"]
    assert fake_service.calls[0][0] == "query_target_visualization_jump_info"


async def test_view_table_detail_list(client: AsyncClient, auth_headers: dict, fake_service: FakeLinkJumpService):
    """EP 6: GET /linkJump/viewTableDetailList/{dvId}"""
    response = await client.get(
        "/de2api/linkJump/viewTableDetailList/5001",
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    data = body["data"]
    assert data["componentData"] == '[{"id":"chart1"}]'
    assert len(data["result"]) == 1
    assert data["result"][0]["id"] == 4001
    assert data["result"][0]["title"] == "Chart 1"
    assert len(data["result"][0]["tableFields"]) == 1
    assert len(data["outParamsJumpInfo"]) == 1
    assert data["outParamsJumpInfo"][0]["type"] == "outerParams"
    assert fake_service.calls[0][0] == "view_table_detail_list"


async def test_update_jump_set_active(client: AsyncClient, auth_headers: dict, fake_service: FakeLinkJumpService):
    """EP 7: POST /linkJump/updateJumpSetActive"""
    payload = {
        "sourceDvId": 5001,
        "sourceViewId": 4001,
        "activeStatus": True,
    }
    response = await client.post(
        "/de2api/linkJump/updateJumpSetActive",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert fake_service.calls[0][0] == "update_jump_set_active"


async def test_remove_jump_set(client: AsyncClient, auth_headers: dict, fake_service: FakeLinkJumpService):
    """EP 8: POST /linkJump/removeJumpSet"""
    payload = {
        "sourceDvId": 5001,
        "sourceViewId": 4001,
    }
    response = await client.post(
        "/de2api/linkJump/removeJumpSet",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert fake_service.calls[0][0] == "remove_jump_set"
    assert fake_service.calls[0][1]["source_dv_id"] == 5001
    assert fake_service.calls[0][1]["source_view_id"] == 4001


async def test_unauthenticated_requests_are_rejected(client: AsyncClient):
    """All endpoints require authentication."""
    response = await client.get("/de2api/linkJump/getTableFieldWithViewId/4001")
    # Should be 401 or wrapped 401
    assert response.status_code in (401, 200)
    if response.status_code == 200:
        assert response.json()["code"] != 0
