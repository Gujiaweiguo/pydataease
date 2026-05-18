from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass

import pytest
from httpx import AsyncClient
from typing import cast

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.routers.dataset_field import get_field_repo  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


@dataclass(slots=True)
class FakeField:
    id: int = 0
    datasource_id: int | None = None
    dataset_table_id: int | None = None
    dataset_group_id: int | None = None
    chart_id: int | None = None
    origin_name: str = ""
    name: str = ""
    description: str | None = None
    dataease_name: str | None = None
    field_short_name: str | None = None
    group_type: str = "d"
    type: str = "VARCHAR"
    size: int | None = None
    de_type: int = 0
    de_extract_type: int = 0
    ext_field: int = 0
    checked: bool = True
    column_index: int = 0
    last_sync_time: int | None = None
    accuracy: int | None = None
    date_format: str | None = None
    date_format_type: str | None = None


def _make_field(
    fid: int = 1001,
    origin_name: str = "col_a",
    name: str = "Column A",
    group_type: str = "d",
    checked: bool = True,
    chart_id: int | None = None,
    ext_field: int = 0,
    column_index: int = 0,
    dataset_group_id: int = 500,
):
    return FakeField(
        id=fid,
        datasource_id=1,
        dataset_table_id=10,
        dataset_group_id=dataset_group_id,
        chart_id=chart_id,
        origin_name=origin_name,
        name=name,
        description=None,
        dataease_name="f_abcd",
        field_short_name="f_abcd",
        group_type=group_type,
        type="VARCHAR",
        size=255,
        de_type=0,
        de_extract_type=0,
        ext_field=ext_field,
        checked=checked,
        column_index=column_index,
        last_sync_time=None,
        accuracy=None,
        date_format=None,
        date_format_type=None,
    )


class FakeDatasetFieldRepository:
    def __init__(self) -> None:
        self.fields: list[FakeField] = [
            _make_field(fid=1001, origin_name="dim1", name="Dim 1", group_type="d", column_index=0),
            _make_field(fid=1002, origin_name="dim2", name="Dim 2", group_type="d", column_index=1),
            _make_field(fid=1003, origin_name="quota1", name="Quota 1", group_type="q", column_index=2),
            _make_field(fid=1004, origin_name="quota2", name="Quota 2", group_type="q", chart_id=99, dataset_group_id=500, column_index=3),
            _make_field(fid=1005, origin_name="dim_other", name="Dim Other", group_type="d", dataset_group_id=600, column_index=0),
        ]
        self.deleted_ids: list[int] = []
        self.deleted_chart_ids: list[int] = []
        self.saved: list[dict[str, object]] = []

    async def list_checked_by_group(self, dataset_group_id: int) -> list[FakeField]:
        return [
            f for f in self.fields
            if f.dataset_group_id == dataset_group_id
            and f.checked is True
            and f.chart_id is None
        ]

    async def list_checked_by_group_no_chart_filter(self, dataset_group_id: int) -> list[FakeField]:
        return [
            f for f in self.fields
            if f.dataset_group_id == dataset_group_id
            and f.checked is True
        ]

    async def get_by_id(self, field_id: int):
        return next((f for f in self.fields if f.id == field_id), None)

    async def delete_by_id(self, field_id: int) -> None:
        self.deleted_ids.append(field_id)
        self.fields = [f for f in self.fields if f.id != field_id]

    async def delete_by_chart_id(self, chart_id: int) -> None:
        self.deleted_chart_ids.append(chart_id)
        self.fields = [f for f in self.fields if f.chart_id != chart_id]

    async def list_origin_fields_by_groups(self, group_ids: list[int]) -> dict[str, list[FakeField]]:
        result: dict[str, list[FakeField]] = {}
        for gid in group_ids:
            result[str(gid)] = [
                f for f in self.fields
                if f.dataset_group_id == gid
                and f.checked is True
                and f.chart_id is None
                and f.ext_field == 0
            ]
        return result

    async def save_field(self, field_data: dict[str, object]) -> FakeField:
        self.saved.append(field_data)
        return _make_field(
            fid=cast(int, field_data.get("id", 9999)),
            origin_name=cast(str, field_data.get("origin_name", "")),
            name=cast(str, field_data.get("name", "")),
            group_type=cast(str, field_data.get("group_type", "d")),
            checked=cast(bool, field_data.get("checked", True)),
            chart_id=cast(int | None, field_data.get("chart_id")),
            ext_field=cast(int, field_data.get("ext_field", 0)),
            dataset_group_id=cast(int, field_data.get("dataset_group_id", 500)),
        )


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_repo() -> Generator[FakeDatasetFieldRepository, None, None]:
    repo = FakeDatasetFieldRepository()
    app.dependency_overrides[get_field_repo] = lambda: repo
    yield repo
    _ = app.dependency_overrides.pop(get_field_repo, None)


@pytest.mark.asyncio
async def test_list_by_dataset_group(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_repo: FakeDatasetFieldRepository,
) -> None:
    response = await client.post(
        "/de2api/datasetField/listByDatasetGroup/500",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 3
    assert data[0]["originName"] == "dim1"
    assert data[1]["originName"] == "dim2"
    assert data[2]["originName"] == "quota1"


@pytest.mark.asyncio
async def test_list_by_dq(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_repo: FakeDatasetFieldRepository,
) -> None:
    response = await client.post(
        "/de2api/datasetField/listByDQ/500",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["dimensionList"]) == 2
    assert len(data["quotaList"]) == 2
    assert data["dimensionList"][0]["groupType"] == "d"
    assert data["quotaList"][0]["groupType"] == "q"


@pytest.mark.asyncio
async def test_get_field(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_repo: FakeDatasetFieldRepository,
) -> None:
    response = await client.post(
        "/de2api/datasetField/get/1001",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 1001
    assert data["originName"] == "dim1"


@pytest.mark.asyncio
async def test_get_field_not_found(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_repo: FakeDatasetFieldRepository,
) -> None:
    response = await client.post(
        "/de2api/datasetField/get/9999",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["data"] is None


@pytest.mark.asyncio
async def test_save_field_create(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_repo: FakeDatasetFieldRepository,
) -> None:
    response = await client.post(
        "/de2api/datasetField/save",
        headers=auth_headers,
        json={
            "originName": "new_col",
            "name": "New Column",
            "groupType": "q",
            "datasetGroupId": 500,
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["originName"] == "new_col"
    assert len(fake_repo.saved) == 1


@pytest.mark.asyncio
async def test_save_field_update(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_repo: FakeDatasetFieldRepository,
) -> None:
    response = await client.post(
        "/de2api/datasetField/save",
        headers=auth_headers,
        json={
            "id": 1001,
            "originName": "updated_col",
            "name": "Updated Column",
            "groupType": "d",
            "datasetGroupId": 500,
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["originName"] == "updated_col"
    assert len(fake_repo.saved) == 1


@pytest.mark.asyncio
async def test_delete_field(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_repo: FakeDatasetFieldRepository,
) -> None:
    response = await client.post(
        "/de2api/datasetField/delete/1001",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert fake_repo.deleted_ids == [1001]


@pytest.mark.asyncio
async def test_list_by_ds_ids(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_repo: FakeDatasetFieldRepository,
) -> None:
    response = await client.post(
        "/de2api/datasetField/listByDsIds",
        headers=auth_headers,
        json={"ids": [500]},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "500" in data
    assert len(data["500"]) == 3


@pytest.mark.asyncio
async def test_get_function(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_repo: FakeDatasetFieldRepository,
) -> None:
    response = await client.post(
        "/de2api/datasetField/getFunction",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 11
    assert data[0]["name"] == "SUBSTRING"
    assert data[1]["name"] == "ABS"


@pytest.mark.asyncio
async def test_delete_by_chart_id(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_repo: FakeDatasetFieldRepository,
) -> None:
    response = await client.post(
        "/de2api/datasetField/deleteByChartId/99",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert fake_repo.deleted_chart_ids == [99]


@pytest.mark.asyncio
async def test_list_by_dataset_group_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasetField/listByDatasetGroup/500")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_save_field_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/datasetField/save",
        json={"originName": "x"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_field_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasetField/delete/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_function_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasetField/getFunction")
    assert response.status_code == 401
