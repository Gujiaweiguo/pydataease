"""Tests for VisualizationOuterParams API endpoints.

Uses fake service injection pattern (same as test_link_jump).
All 4 endpoints are tested via httpx AsyncClient against the FastAPI app.
"""

# pyright: reportCallIssue=false
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from jose import jwt

from app.main import app
from app.routers.outer_params import get_outer_params_service
from app.schemas.outer_params import (
    OuterParamsBaseResponse,
    OuterParamsInfoDTO,
    OuterParamsTargetViewInfoDTO,
    VisualizationOuterParamsDTO,
)
from app.settings.config import get_settings


def _build_token(user_id: int = 1) -> str:
    settings = get_settings()
    payload = {"uid": user_id, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


class FakeOuterParamsService:
    """Fake service that records calls and returns predictable data."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    async def query_with_visualization_id(
        self, visualization_id: str
    ) -> VisualizationOuterParamsDTO | None:
        self.calls.append(
            ("query_with_visualization_id", {"visualization_id": visualization_id})
        )
        return VisualizationOuterParamsDTO(
            params_id="params-001",
            visualization_id=visualization_id,
            checked=True,
            outer_params_info_array=[
                OuterParamsInfoDTO(
                    params_info_id="info-001",
                    params_id="params-001",
                    param_name="myParam",
                    checked=True,
                    required=True,
                    target_view_info_list=[
                        OuterParamsTargetViewInfoDTO(
                            target_view_id="view-100",
                            target_ds_id="ds-200",
                            target_field_id="field-300",
                            match_mode="strict",
                        )
                    ],
                )
            ],
        )

    async def update_outer_params_set(
        self, dto: VisualizationOuterParamsDTO
    ) -> None:
        self.calls.append(
            ("update_outer_params_set", {"visualization_id": dto.visualization_id})
        )

    async def get_outer_params_info(
        self, visualization_id: str
    ) -> OuterParamsBaseResponse:
        self.calls.append(
            ("get_outer_params_info", {"visualization_id": visualization_id})
        )
        info_dto = OuterParamsInfoDTO(
            source_info="myParam",
            required=True,
            target_info_list=["view-100#field-300#strict"],
        )
        return OuterParamsBaseResponse(
            outer_params_info_map={"myParam": ["view-100#field-300#strict"]},
            outer_params_info_base_map={"myParam": info_dto},
        )

    async def query_ds_with_visualization_id(
        self, visualization_id: str
    ) -> list[dict]:
        self.calls.append(
            ("query_ds_with_visualization_id", {"visualization_id": visualization_id})
        )
        return [
            {
                "id": 1001,
                "name": "Test Dataset",
                "pid": 0,
                "node_type": "dataset",
                "datasetFields": [],
                "datasetViews": [],
            }
        ]


@pytest.fixture(autouse=True)
def override_service():
    fake = FakeOuterParamsService()
    app.dependency_overrides[get_outer_params_service] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_outer_params_service, None)


@pytest.mark.asyncio
async def test_query_with_visualization_id(client: AsyncClient, override_service):
    token = _build_token()
    resp = await client.get(
        "/de2api/outerParams/queryWithVisualizationId/9999",
        headers={"X-DE-TOKEN": token},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert data["visualizationId"] == "9999"
    assert data["checked"] is True
    assert len(data["outerParamsInfoArray"]) == 1
    assert data["outerParamsInfoArray"][0]["paramName"] == "myParam"
    override_service.calls[0][0] == "query_with_visualization_id"


@pytest.mark.asyncio
async def test_update_outer_params_set(client: AsyncClient, override_service):
    token = _build_token()
    payload = {
        "visualizationId": "8888",
        "checked": True,
        "outerParamsInfoArray": [
            {
                "paramName": "newParam",
                "checked": True,
                "required": False,
                "targetViewInfoList": [
                    {
                        "targetViewId": "v1",
                        "targetDsId": "d1",
                        "targetFieldId": "f1",
                        "matchMode": "fuzzy",
                    }
                ],
            }
        ],
    }
    resp = await client.post(
        "/de2api/outerParams/updateOuterParamsSet",
        json=payload,
        headers={"X-DE-TOKEN": token},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"] is None
    assert override_service.calls[0][0] == "update_outer_params_set"
    assert override_service.calls[0][1]["visualization_id"] == "8888"


@pytest.mark.asyncio
async def test_get_outer_params_info(client: AsyncClient, override_service):
    token = _build_token()
    resp = await client.get(
        "/de2api/outerParams/getOuterParamsInfo/7777",
        headers={"X-DE-TOKEN": token},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert data["outerParamsInfoMap"]["myParam"] == ["view-100#field-300#strict"]
    assert data["outerParamsInfoBaseMap"]["myParam"]["sourceInfo"] == "myParam"
    override_service.calls[0][0] == "get_outer_params_info"


@pytest.mark.asyncio
async def test_query_ds_with_visualization_id(client: AsyncClient, override_service):
    token = _build_token()
    resp = await client.get(
        "/de2api/outerParams/queryDsWithVisualizationId/6666",
        headers={"X-DE-TOKEN": token},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert len(data) == 1
    assert data[0]["name"] == "Test Dataset"
    override_service.calls[0][0] == "query_ds_with_visualization_id"


@pytest.mark.asyncio
async def test_unauthorized_returns_401(client: AsyncClient):
    """All endpoints should return 401 without a valid token."""
    endpoints = [
        ("/de2api/outerParams/queryWithVisualizationId/1", "GET"),
        ("/de2api/outerParams/getOuterParamsInfo/1", "GET"),
        ("/de2api/outerParams/queryDsWithVisualizationId/1", "GET"),
    ]
    for path, method in endpoints:
        resp = await client.get(path) if method == "GET" else None
        assert resp is not None
        assert resp.status_code == 401, f"Expected 401 for {path}"

    # POST endpoint
    resp = await client.post(
        "/de2api/outerParams/updateOuterParamsSet",
        json={"visualizationId": "1"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_query_with_visualization_id_returns_none(
    client: AsyncClient, override_service
):
    """When service returns None, endpoint should return null data."""

    async def _return_none(vid):
        return None

    override_service.query_with_visualization_id = _return_none
    token = _build_token()
    resp = await client.get(
        "/de2api/outerParams/queryWithVisualizationId/missing",
        headers={"X-DE-TOKEN": token},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"] is None
