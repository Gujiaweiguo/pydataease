from __future__ import annotations

# pyright: reportMissingTypeArgument=false

import pytest
from httpx import AsyncClient

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.services.custom_geo_service import get_custom_geo_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.dataset_sql_log_service import get_dataset_sql_log_service  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


def _auth_header(user_id: int = 1, oid: int = 1) -> dict[str, str]:
    token = _build_token(uid=user_id, oid=oid)
    return {"X-DE-TOKEN": token}


# ---------------------------------------------------------------------------
# Fake services
# ---------------------------------------------------------------------------


class FakeCustomGeoService:
    def __init__(self) -> None:
        self.areas: list[dict] = []
        self.sub_areas: list[dict] = []
        self._area_counter = 0

    async def list_areas(self) -> list[dict]:
        return self.areas

    async def get_area(self, area_id: str) -> dict | None:
        return next((a for a in self.areas if a["id"] == area_id), None)

    async def save_area(self, payload, user) -> dict:
        self._area_counter += 1
        area_id = payload.id or f"area_{self._area_counter}"
        now = 1700000000000
        user_id = str(user.user_id) if user else "system"
        existing = next((a for a in self.areas if a["id"] == area_id), None)
        if existing:
            existing["name"] = payload.name
            return existing
        area = {
            "id": area_id,
            "name": payload.name,
            "createBy": user_id,
            "createTime": now,
            "updateBy": None,
            "updateTime": None,
        }
        self.areas.append(area)
        return area

    async def delete_area(self, area_id: str) -> None:
        self.areas = [a for a in self.areas if a["id"] != area_id]
        self.sub_areas = [s for s in self.sub_areas if s["geoAreaId"] != area_id]

    async def save_sub_area(self, payload) -> dict:
        sub = {
            "id": len(self.sub_areas) + 1,
            "geoAreaId": payload.geo_area_id,
            "name": payload.name,
            "geoJson": payload.geo_json,
        }
        self.sub_areas.append(sub)
        return sub

    async def delete_sub_area(self, sub_area_id: int) -> None:
        self.sub_areas = [s for s in self.sub_areas if s["id"] != sub_area_id]

    async def list_sub_area_options(self) -> list[dict]:
        return self.sub_areas


class FakeDatasetSqlLogService:
    def __init__(self) -> None:
        self.logs: list[dict] = []
        self._counter = 0

    async def save(self, payload, user) -> dict:
        self._counter += 1
        entry = {
            "id": str(self._counter),
            "tableId": payload.table_id,
            "sqlSnapshot": payload.sql_snapshot,
            "tableName": payload.table_name,
            "createTime": 1700000000000,
            "createBy": str(user.user_id),
            "status": payload.status,
            "errorMsg": payload.error_msg,
        }
        self.logs.append(entry)
        return entry

    async def list_by_table_id(self, table_id: str) -> list[dict]:
        return [entry for entry in self.logs if entry["tableId"] == table_id]

    async def delete_by_table_id(self, table_id: str) -> None:
        self.logs = [entry for entry in self.logs if entry["tableId"] != table_id]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_geo_service():
    return FakeCustomGeoService()


@pytest.fixture
def fake_sqllog_service():
    return FakeDatasetSqlLogService()


@pytest.fixture(autouse=True)
def override_services(fake_geo_service, fake_sqllog_service):
    app.dependency_overrides[get_custom_geo_service] = lambda: fake_geo_service
    app.dependency_overrides[get_dataset_sql_log_service] = lambda: fake_sqllog_service
    yield
    app.dependency_overrides.pop(get_custom_geo_service, None)
    app.dependency_overrides.pop(get_dataset_sql_log_service, None)


# ---------------------------------------------------------------------------
# CustomGeo tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_geo_area_list_empty(client: AsyncClient) -> None:
    resp = await client.get("/de2api/customGeo/geoArea/list", headers=_auth_header())
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert isinstance(body["data"], list)


@pytest.mark.anyio
async def test_geo_area_save_and_list(
    client: AsyncClient, fake_geo_service: FakeCustomGeoService
) -> None:
    resp = await client.post(
        "/de2api/customGeo/geoArea/save",
        json={"name": "Test Area"},
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["name"] == "Test Area"

    list_resp = await client.get("/de2api/customGeo/geoArea/list", headers=_auth_header())
    areas = list_resp.json()["data"]
    assert len(areas) == 1


@pytest.mark.anyio
async def test_geo_area_get_by_id(
    client: AsyncClient, fake_geo_service: FakeCustomGeoService
) -> None:
    save_resp = await client.post(
        "/de2api/customGeo/geoArea/save",
        json={"name": "Area X"},
        headers=_auth_header(),
    )
    area_id = save_resp.json()["data"]["id"]

    resp = await client.get(f"/de2api/customGeo/geoArea/{area_id}", headers=_auth_header())
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == area_id


@pytest.mark.anyio
async def test_geo_area_delete(
    client: AsyncClient, fake_geo_service: FakeCustomGeoService
) -> None:
    save_resp = await client.post(
        "/de2api/customGeo/geoArea/save",
        json={"name": "To Delete"},
        headers=_auth_header(),
    )
    area_id = save_resp.json()["data"]["id"]

    resp = await client.delete(
        f"/de2api/customGeo/geoArea/{area_id}", headers=_auth_header()
    )
    assert resp.status_code == 200
    assert len(fake_geo_service.areas) == 0


@pytest.mark.anyio
async def test_geo_sub_area_save(
    client: AsyncClient, fake_geo_service: FakeCustomGeoService
) -> None:
    resp = await client.post(
        "/de2api/customGeo/geoSubArea/save",
        json={"geoAreaId": "area_1", "name": "Sub 1", "geoJson": {"type": "Point"}},
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["name"] == "Sub 1"
    assert body["data"]["geoJson"] == {"type": "Point"}


@pytest.mark.anyio
async def test_geo_sub_area_delete(
    client: AsyncClient, fake_geo_service: FakeCustomGeoService
) -> None:
    save_resp = await client.post(
        "/de2api/customGeo/geoSubArea/save",
        json={"geoAreaId": "area_1", "name": "Sub Del", "geoJson": {}},
        headers=_auth_header(),
    )
    sub_id = save_resp.json()["data"]["id"]

    resp = await client.delete(
        f"/de2api/customGeo/geoSubArea/{sub_id}", headers=_auth_header()
    )
    assert resp.status_code == 200
    assert len(fake_geo_service.sub_areas) == 0


@pytest.mark.anyio
async def test_geo_sub_area_options(
    client: AsyncClient, fake_geo_service: FakeCustomGeoService
) -> None:
    await client.post(
        "/de2api/customGeo/geoSubArea/save",
        json={"geoAreaId": "area_1", "name": "Opt1", "geoJson": {}},
        headers=_auth_header(),
    )
    resp = await client.get("/de2api/customGeo/geoSubArea/options", headers=_auth_header())
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 1


@pytest.mark.anyio
async def test_geo_area_works_without_auth(client: AsyncClient) -> None:
    """customGeo paths are whitelisted — accessible without token."""
    resp = await client.get("/de2api/customGeo/geoArea/list")
    assert resp.status_code == 200
    assert resp.json()["code"] == 0


# ---------------------------------------------------------------------------
# DatasetSqlLog tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_sqllog_save(
    client: AsyncClient, fake_sqllog_service: FakeDatasetSqlLogService
) -> None:
    resp = await client.post(
        "/de2api/datasetTableSqlLog/save",
        json={
            "tableId": "t1",
            "sqlSnapshot": "SELECT 1",
            "tableName": "my_table",
            "status": "success",
        },
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["tableId"] == "t1"
    assert body["data"]["sqlSnapshot"] == "SELECT 1"


@pytest.mark.anyio
async def test_sqllog_list_by_table_id(
    client: AsyncClient, fake_sqllog_service: FakeDatasetSqlLogService
) -> None:
    await client.post(
        "/de2api/datasetTableSqlLog/save",
        json={"tableId": "t1", "sqlSnapshot": "SELECT 1"},
        headers=_auth_header(),
    )
    await client.post(
        "/de2api/datasetTableSqlLog/save",
        json={"tableId": "t2", "sqlSnapshot": "SELECT 2"},
        headers=_auth_header(),
    )

    resp = await client.post(
        "/de2api/datasetTableSqlLog/listByTableId",
        json={"tableId": "t1"},
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["tableId"] == "t1"


@pytest.mark.anyio
async def test_sqllog_delete_by_table_id(
    client: AsyncClient, fake_sqllog_service: FakeDatasetSqlLogService
) -> None:
    await client.post(
        "/de2api/datasetTableSqlLog/save",
        json={"tableId": "t1", "sqlSnapshot": "SELECT 1"},
        headers=_auth_header(),
    )

    resp = await client.post(
        "/de2api/datasetTableSqlLog/deleteByTableId/t1",
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    assert len(fake_sqllog_service.logs) == 0


@pytest.mark.anyio
async def test_sqllog_save_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/de2api/datasetTableSqlLog/save",
        json={"tableId": "t1"},
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_sqllog_list_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/de2api/datasetTableSqlLog/listByTableId",
        json={"tableId": "t1"},
    )
    assert resp.status_code == 401
