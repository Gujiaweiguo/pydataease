from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from jose import jwt

from app.main import app
from app.schemas.system import MenuTreeNodeResponse
from app.services.system_service import SystemService, get_system_service
from app.settings.config import get_settings


def _build_token(**claims: int) -> str:
    settings = get_settings()
    payload = {**claims, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


class FakeSystemService:
    def __init__(self) -> None:
        self.saved_map_key: str | None = None

    async def query_online_map(self) -> object:
        return {"key": "test-map-key"}

    async def save_online_map(self, key: str | None) -> object:
        self.saved_map_key = key
        return {"key": key or ""}

    async def request_timeout(self) -> int:
        return 120

    async def query_menus(self) -> list[MenuTreeNodeResponse]:
        return [
            MenuTreeNodeResponse(
                id=1,
                pid=0,
                type=0,
                name="system",
                component=None,
                menu_sort=1,
                icon="system",
                path="/system",
                hidden=False,
                in_layout=True,
                auth=False,
                children=[
                    MenuTreeNodeResponse(
                        id=2,
                        pid=1,
                        type=1,
                        name="datasource",
                        component="system/datasource",
                        menu_sort=1,
                        icon="datasource",
                        path="datasource",
                        hidden=False,
                        in_layout=True,
                        auth=False,
                        children=[],
                    )
                ],
            )
        ]

    async def list_fonts(self) -> list[object]:
        return []

    async def default_font(self) -> object:
        return None

    async def get_area_entities(self, pcode: str) -> list[object]:
        return []


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeSystemService, None, None]:
    svc = FakeSystemService()
    app.dependency_overrides[get_system_service] = lambda: svc
    yield svc
    _ = app.dependency_overrides.pop(get_system_service, None)


@pytest.mark.asyncio
async def test_query_online_map(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeSystemService,
) -> None:
    response = await client.get(
        "/de2api/sysParameter/queryOnlineMap",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["key"] == "test-map-key"


@pytest.mark.asyncio
async def test_save_online_map(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeSystemService,
) -> None:
    response = await client.post(
        "/de2api/sysParameter/saveOnlineMap",
        headers=auth_headers,
        json={"key": "new-map-key"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["key"] == "new-map-key"
    assert fake_service.saved_map_key == "new-map-key"


@pytest.mark.asyncio
async def test_request_timeout(
    client: AsyncClient,
    fake_service: FakeSystemService,
) -> None:
    response = await client.get(
        "/de2api/sysParameter/requestTimeOut",
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data == 120


@pytest.mark.asyncio
async def test_query_menus(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeSystemService,
) -> None:
    response = await client.get(
        "/de2api/menu/query",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "system"
    assert len(data[0]["children"]) == 1
    assert data[0]["children"][0]["name"] == "datasource"


@pytest.mark.asyncio
async def test_list_fonts(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeSystemService,
) -> None:
    response = await client.get(
        "/de2api/font/listFont",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data == []


@pytest.mark.asyncio
async def test_default_font(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeSystemService,
) -> None:
    response = await client.get(
        "/de2api/font/defaultFont",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data is None


@pytest.mark.asyncio
async def test_area_entities(
    client: AsyncClient,
    fake_service: FakeSystemService,
) -> None:
    response = await client.get(
        "/de2api/map/areaEntitys/156",
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data == []


@pytest.mark.asyncio
async def test_save_online_map_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/de2api/sysParameter/saveOnlineMap",
        json={"key": "test"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_query_menus_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/de2api/menu/query")
    assert response.status_code == 401
