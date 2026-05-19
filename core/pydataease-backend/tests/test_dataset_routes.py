from __future__ import annotations

from collections.abc import Generator

import pytest
from httpx import AsyncClient

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.services.dataset_service import get_dataset_service  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.dataset_fixtures import (  # pyright: ignore[reportImplicitRelativeImport]
    FakeDatasetService,
)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeDatasetService, None, None]:
    svc = FakeDatasetService()
    app.dependency_overrides[get_dataset_service] = lambda: svc
    yield svc
    _ = app.dependency_overrides.pop(get_dataset_service, None)


@pytest.mark.asyncio
async def test_dataset_tree_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetService,
) -> None:
    response = await client.post(
        "/de2api/datasetTree/tree",
        headers=auth_headers,
        json={"busiFlag": "dataset"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "root-folder"
    assert data[0]["leaf"] is False
    assert len(data[0]["children"]) == 1
    assert data[0]["children"][0]["name"] == "child-dataset"
    assert data[0]["children"][0]["leaf"] is True


@pytest.mark.asyncio
async def test_dataset_create_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetService,
) -> None:
    response = await client.post(
        "/de2api/datasetTree/create",
        headers=auth_headers,
        json={
            "name": "my-dataset",
            "pid": 0,
            "nodeType": "folder",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 100
    assert data["name"] == "new-dataset"
    assert len(fake_service.created) == 1


@pytest.mark.asyncio
async def test_dataset_save_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetService,
) -> None:
    response = await client.post(
        "/de2api/datasetTree/save",
        headers=auth_headers,
        json={
            "id": 200,
            "name": "my-dataset-updated",
            "nodeType": "dataset",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 200
    assert data["name"] == "updated-dataset"


@pytest.mark.asyncio
async def test_dataset_rename_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetService,
) -> None:
    response = await client.post(
        "/de2api/datasetTree/rename",
        headers=auth_headers,
        json={"id": 300, "name": "renamed"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == "renamed-dataset"


@pytest.mark.asyncio
async def test_dataset_move_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetService,
) -> None:
    response = await client.post(
        "/de2api/datasetTree/move",
        headers=auth_headers,
        json={"id": 400, "pid": 5},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["pid"] == 5


@pytest.mark.asyncio
async def test_dataset_delete_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetService,
) -> None:
    response = await client.post(
        "/de2api/datasetTree/delete/999",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert fake_service.deleted_ids == [999]


@pytest.mark.asyncio
async def test_dataset_details_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetService,
) -> None:
    response = await client.post(
        "/de2api/datasetTree/details/500",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == "500"
    assert data["name"] == "detail-ds"


@pytest.mark.asyncio
async def test_dataset_bar_info_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetService,
) -> None:
    response = await client.get(
        "/de2api/datasetTree/barInfo/600",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == "600"
    assert data["createBy"] == "7"


@pytest.mark.asyncio
async def test_dataset_table_field_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetService,
) -> None:
    response = await client.post(
        "/de2api/datasetData/tableField",
        headers=auth_headers,
        json={"datasetGroupId": 700},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["originName"] == "col_a"
    assert data[0]["name"] == "Column A"


@pytest.mark.asyncio
async def test_dataset_preview_sql_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetService,
) -> None:
    response = await client.post(
        "/de2api/datasetData/previewSql",
        headers=auth_headers,
        json={"sql": "SELECT 1"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["data"] == []
    assert data["fields"] == []


@pytest.mark.asyncio
async def test_dataset_per_delete_route(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeDatasetService,
) -> None:
    response = await client.post(
        "/de2api/datasetTree/perDelete/800",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"] is True


@pytest.mark.asyncio
async def test_dataset_tree_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/datasetTree/tree",
        json={"busiFlag": "dataset"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_create_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/datasetTree/create",
        json={"name": "x", "nodeType": "folder"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_delete_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasetTree/delete/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_details_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasetTree/details/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dataset_table_field_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/datasetData/tableField",
        json={"datasetGroupId": 1},
    )
    assert response.status_code == 401
