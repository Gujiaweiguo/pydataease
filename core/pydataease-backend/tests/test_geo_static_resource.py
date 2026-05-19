from __future__ import annotations

# pyright: reportMissingTypeArgument=false, reportMissingImports=false

import pytest
from httpx import AsyncClient

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.services.geo_service import get_geo_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.static_resource_service import get_static_resource_service  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


def _auth_header(user_id: int = 1, oid: int = 1) -> dict[str, str]:
    token = _build_token(uid=user_id, oid=oid)
    return {"X-DE-TOKEN": token}


# ---------------------------------------------------------------------------
# Fake services
# ---------------------------------------------------------------------------


class FakeGeoService:
    def __init__(self) -> None:
        self.geos: list[dict] = []

    async def save_geo(self, payload) -> dict:
        existing = next((g for g in self.geos if g["id"] == payload.id), None)
        if existing is not None:
            if payload.name is not None:
                existing["name"] = payload.name
            if payload.geo_json is not None:
                existing["geoJson"] = payload.geo_json
            return existing
        geo = {
            "id": payload.id,
            "name": payload.name,
            "geoJson": payload.geo_json,
        }
        self.geos.append(geo)
        return geo

    async def delete_geo(self, geo_id: str) -> None:
        geo = next((g for g in self.geos if g["id"] == geo_id), None)
        if geo is None:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Geometry not found",
            )
        self.geos = [g for g in self.geos if g["id"] != geo_id]

    async def mapping(self, geo_id: str, payload) -> dict:
        geo = next((g for g in self.geos if g["id"] == geo_id), None)
        if geo is None:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Geometry not found",
            )
        return {"id": geo["id"], "name": geo["name"], "mapping": payload.mapping}


class FakeStaticResourceService:
    def __init__(self) -> None:
        self.resources: list[dict] = []

    async def upload(self, file_id: str, payload) -> dict:
        existing = next((r for r in self.resources if r["id"] == file_id), None)
        if existing is not None:
            existing["content"] = payload.content
            return existing
        resource = {
            "id": file_id,
            "name": None,
            "content": payload.content,
        }
        self.resources.append(resource)
        return resource

    async def find_as_base64(self, resource_id: str) -> dict[str, str]:
        resource = next(
            (r for r in self.resources if r["id"] == resource_id), None
        )
        if resource is None:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Static resource not found",
            )
        return {"resourceId": resource["id"], "content": resource["content"]}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_geo_service():
    return FakeGeoService()


@pytest.fixture
def fake_static_resource_service():
    return FakeStaticResourceService()


@pytest.fixture(autouse=True)
def override_services(fake_geo_service, fake_static_resource_service):
    app.dependency_overrides[get_geo_service] = lambda: fake_geo_service
    app.dependency_overrides[get_static_resource_service] = (
        lambda: fake_static_resource_service
    )
    yield
    app.dependency_overrides.pop(get_geo_service, None)
    app.dependency_overrides.pop(get_static_resource_service, None)


# ---------------------------------------------------------------------------
# Geo tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_geo_save(
    client: AsyncClient, fake_geo_service: FakeGeoService
) -> None:
    resp = await client.post(
        "/de2api/geometry/save",
        json={"id": "geo_1", "name": "Beijing", "geoJson": {"type": "Point"}},
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["id"] == "geo_1"
    assert body["data"]["name"] == "Beijing"
    assert body["data"]["geoJson"] == {"type": "Point"}


@pytest.mark.anyio
async def test_geo_save_update_existing(
    client: AsyncClient, fake_geo_service: FakeGeoService
) -> None:
    await client.post(
        "/de2api/geometry/save",
        json={"id": "geo_1", "name": "Beijing"},
        headers=_auth_header(),
    )
    resp = await client.post(
        "/de2api/geometry/save",
        json={"id": "geo_1", "name": "Shanghai", "geoJson": {"type": "Polygon"}},
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["name"] == "Shanghai"
    assert body["data"]["geoJson"] == {"type": "Polygon"}
    assert len(fake_geo_service.geos) == 1


@pytest.mark.anyio
async def test_geo_delete(
    client: AsyncClient, fake_geo_service: FakeGeoService
) -> None:
    await client.post(
        "/de2api/geometry/save",
        json={"id": "geo_del", "name": "ToDelete"},
        headers=_auth_header(),
    )
    resp = await client.post(
        "/de2api/geometry/delete/geo_del",
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    assert len(fake_geo_service.geos) == 0


@pytest.mark.anyio
async def test_geo_delete_not_found(
    client: AsyncClient, fake_geo_service: FakeGeoService
) -> None:
    resp = await client.post(
        "/de2api/geometry/delete/nonexistent",
        headers=_auth_header(),
    )
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_geo_mapping(
    client: AsyncClient, fake_geo_service: FakeGeoService
) -> None:
    await client.post(
        "/de2api/geometry/save",
        json={"id": "geo_map", "name": "China"},
        headers=_auth_header(),
    )
    resp = await client.post(
        "/de2api/geometry/geo_map/mapping",
        json={"mapping": {"Beijing": "北京", "Shanghai": "上海"}},
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["id"] == "geo_map"
    assert body["data"]["mapping"] == {"Beijing": "北京", "Shanghai": "上海"}


@pytest.mark.anyio
async def test_geo_mapping_not_found(
    client: AsyncClient, fake_geo_service: FakeGeoService
) -> None:
    resp = await client.post(
        "/de2api/geometry/nonexistent/mapping",
        json={"mapping": {}},
        headers=_auth_header(),
    )
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_geo_save_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/de2api/geometry/save",
        json={"id": "geo_1"},
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_geo_delete_requires_auth(client: AsyncClient) -> None:
    resp = await client.post("/de2api/geometry/delete/geo_1")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# StaticResource tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_static_resource_upload(
    client: AsyncClient, fake_static_resource_service: FakeStaticResourceService
) -> None:
    resp = await client.post(
        "/de2api/staticResource/upload/file_1",
        json={"content": "data:image/png;base64,iVBOR..."},
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["id"] == "file_1"
    assert body["data"]["content"] == "data:image/png;base64,iVBOR..."


@pytest.mark.anyio
async def test_static_resource_upload_update_existing(
    client: AsyncClient, fake_static_resource_service: FakeStaticResourceService
) -> None:
    await client.post(
        "/de2api/staticResource/upload/file_1",
        json={"content": "old_content"},
        headers=_auth_header(),
    )
    resp = await client.post(
        "/de2api/staticResource/upload/file_1",
        json={"content": "new_content"},
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["content"] == "new_content"
    assert len(fake_static_resource_service.resources) == 1


@pytest.mark.anyio
async def test_static_resource_find_as_base64(
    client: AsyncClient, fake_static_resource_service: FakeStaticResourceService
) -> None:
    await client.post(
        "/de2api/staticResource/upload/file_1",
        json={"content": "data:image/png;base64,iVBOR..."},
        headers=_auth_header(),
    )
    resp = await client.post(
        "/de2api/staticResource/findResourceAsBase64",
        json={"resourceId": "file_1"},
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["resourceId"] == "file_1"
    assert body["data"]["content"] == "data:image/png;base64,iVBOR..."


@pytest.mark.anyio
async def test_static_resource_find_not_found(
    client: AsyncClient, fake_static_resource_service: FakeStaticResourceService
) -> None:
    resp = await client.post(
        "/de2api/staticResource/findResourceAsBase64",
        json={"resourceId": "nonexistent"},
        headers=_auth_header(),
    )
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_static_resource_upload_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/de2api/staticResource/upload/file_1",
        json={"content": "test"},
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_static_resource_find_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/de2api/staticResource/findResourceAsBase64",
        json={"resourceId": "file_1"},
    )
    assert resp.status_code == 401
