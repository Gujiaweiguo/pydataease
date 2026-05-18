from __future__ import annotations

from collections.abc import Generator

import pytest
from httpx import AsyncClient

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.services.dataset_service import (  # pyright: ignore[reportImplicitRelativeImport]
    get_dataset_service,
)
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.dataset_fixtures import (  # pyright: ignore[reportImplicitRelativeImport]
    FakeDatasetService,
)


class ExtendedFakeDatasetService(FakeDatasetService):
    def __init__(self) -> None:
        super().__init__()
        self.preview_ids: list[int] = []
        self.total_ids: list[int] = []
        self.ds_details_payloads: list[dict[str, object]] = []
        self.export_payloads: list[dict[str, object]] = []

    async def get_dataset_preview(self, group_id: int) -> dict[str, object]:
        self.preview_ids.append(group_id)
        return {
            "id": group_id,
            "name": f"dataset-{group_id}",
            "allFields": [{"name": "city", "deType": 0}],
            "data": [{"city": "Hangzhou"}],
            "total": 1,
        }

    async def get_dataset_total(self, group_id: int) -> int:
        self.total_ids.append(group_id)
        return 0

    async def ds_details(self, payload: dict[str, object]) -> list[dict[str, object]]:
        self.ds_details_payloads.append(payload)
        raw_ids = payload.get("ids", [])
        ids = raw_ids if isinstance(raw_ids, list) else []
        return [
            {"id": dataset_id, "name": f"dataset-{dataset_id}", "nodeType": "dataset"}
            for dataset_id in ids
        ]

    async def export_dataset(self, payload: object) -> dict[str, object]:
        if isinstance(payload, dict):
            self.export_payloads.append(payload)
        return await super().export_dataset(payload)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture(autouse=True)
def fake_service() -> Generator[ExtendedFakeDatasetService, None, None]:
    svc = ExtendedFakeDatasetService()
    app.dependency_overrides[get_dataset_service] = lambda: svc
    yield svc
    _ = app.dependency_overrides.pop(get_dataset_service, None)


@pytest.mark.asyncio
async def test_dataset_get_preview_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: ExtendedFakeDatasetService,
) -> None:
    assert fake_service.preview_ids == []

    response = await client.post("/de2api/datasetTree/get/321", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 321
    assert data["name"] == "dataset-321"
    assert data["allFields"] == [{"name": "city", "deType": 0}]
    assert data["data"] == [{"city": "Hangzhou"}]
    assert data["total"] == 1


@pytest.mark.asyncio
async def test_dataset_get_preview_route_tracks_group_id(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: ExtendedFakeDatasetService,
) -> None:
    response = await client.post("/de2api/datasetTree/get/654", headers=auth_headers)

    assert response.status_code == 200
    assert fake_service.preview_ids == [654]


@pytest.mark.asyncio
async def test_dataset_ds_details_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    payload = {"ids": [1, 2]}

    response = await client.post("/de2api/datasetTree/dsDetails", headers=auth_headers, json=payload)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data == [
        {"id": 1, "name": "dataset-1", "nodeType": "dataset"},
        {"id": 2, "name": "dataset-2", "nodeType": "dataset"},
    ]


@pytest.mark.asyncio
async def test_dataset_ds_details_route_passes_payload(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: ExtendedFakeDatasetService,
) -> None:
    payload = {"ids": [1, 2]}

    response = await client.post("/de2api/datasetTree/dsDetails", headers=auth_headers, json=payload)

    assert response.status_code == 200
    assert fake_service.ds_details_payloads == [payload]


@pytest.mark.asyncio
async def test_dataset_detail_with_perm_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    payload = {"ids": [1, 2]}

    response = await client.post("/de2api/datasetTree/detailWithPerm", headers=auth_headers, json=payload)

    assert response.status_code == 200
    assert response.json()["data"] == [
        {"id": 1, "name": "dataset-1", "nodeType": "dataset"},
        {"id": 2, "name": "dataset-2", "nodeType": "dataset"},
    ]


@pytest.mark.asyncio
async def test_dataset_detail_with_perm_matches_ds_details(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    payload = {"ids": [1, 2]}

    ds_details_response = await client.post(
        "/de2api/datasetTree/dsDetails",
        headers=auth_headers,
        json=payload,
    )
    detail_with_perm_response = await client.post(
        "/de2api/datasetTree/detailWithPerm",
        headers=auth_headers,
        json=payload,
    )

    assert ds_details_response.status_code == 200
    assert detail_with_perm_response.status_code == 200
    assert detail_with_perm_response.json()["data"] == ds_details_response.json()["data"]


@pytest.mark.asyncio
async def test_dataset_detail_routes_share_same_service_method(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: ExtendedFakeDatasetService,
) -> None:
    payload = {"ids": [1, 2]}

    first = await client.post("/de2api/datasetTree/dsDetails", headers=auth_headers, json=payload)
    second = await client.post("/de2api/datasetTree/detailWithPerm", headers=auth_headers, json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert fake_service.ds_details_payloads == [payload, payload]


@pytest.mark.asyncio
async def test_dataset_total_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await client.post(
        "/de2api/datasetData/getDatasetTotal",
        headers=auth_headers,
        json={"id": 77},
    )

    assert response.status_code == 200
    assert response.json()["data"] == 0


@pytest.mark.asyncio
async def test_dataset_total_route_converts_id_before_service_call(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: ExtendedFakeDatasetService,
) -> None:
    response = await client.post(
        "/de2api/datasetData/getDatasetTotal",
        headers=auth_headers,
        json={"id": "88"},
    )

    assert response.status_code == 200
    assert fake_service.total_ids == [88]


@pytest.mark.asyncio
async def test_dataset_export_dataset_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    payload = {"id": 901, "type": "xlsx"}

    response = await client.post(
        "/de2api/datasetTree/exportDataset",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["data"] == {"file": "dataset.xlsx", "status": "SUCCESS"}


@pytest.mark.asyncio
async def test_dataset_export_dataset_route_passes_payload(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: ExtendedFakeDatasetService,
) -> None:
    payload = {"id": 901, "type": "xlsx"}

    response = await client.post(
        "/de2api/datasetTree/exportDataset",
        headers=auth_headers,
        json=payload,
    )

    assert response.status_code == 200
    assert fake_service.export_payloads == [payload]


@pytest.mark.asyncio
async def test_dataset_save_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/datasetTree/save",
        json={"id": 200, "name": "my-dataset-updated", "nodeType": "dataset"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_rename_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasetTree/rename", json={"id": 300, "name": "renamed"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_move_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasetTree/move", json={"id": 400, "pid": 5})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_per_delete_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasetTree/perDelete/800")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_bar_info_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/de2api/datasetTree/barInfo/600")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_get_preview_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasetTree/get/321")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_export_dataset_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasetTree/exportDataset", json={"id": 901, "type": "xlsx"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_ds_details_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasetTree/dsDetails", json={"ids": [1, 2]})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_detail_with_perm_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasetTree/detailWithPerm", json={"ids": [1, 2]})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_total_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasetData/getDatasetTotal", json={"id": 77})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_preview_sql_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasetData/previewSql", json={"sql": "SELECT 1"})
    assert response.status_code == 401
