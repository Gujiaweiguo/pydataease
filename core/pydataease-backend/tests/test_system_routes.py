from __future__ import annotations

from collections.abc import Generator

import pytest
from httpx import AsyncClient

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.menu import MenuMeta, MenuVO  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.system import MenuTreeNodeResponse  # pyright: ignore[reportImplicitRelativeImport]
from app.services.menu_service import get_menu_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.system_service import get_system_service  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


class FakeSystemService:
    def __init__(self) -> None:
        self.saved_map_key: str | None = None
        self.saved_map_type: str | None = None
        self.saved_security_code: str | None = None

    async def query_online_map(self) -> object:
        return {"key": "test-map-key", "mapType": "gaode", "securityCode": "test-sec"}

    async def query_online_map_by_type(self, map_type: str) -> object:
        return {"key": f"{map_type}-key", "mapType": map_type, "securityCode": f"{map_type}-sec"}

    async def save_online_map(
        self,
        key: str | None,
        map_type: str | None = None,
        security_code: str | None = None,
    ) -> object:
        self.saved_map_key = key
        self.saved_map_type = map_type
        self.saved_security_code = security_code
        return {"key": key or "", "mapType": map_type or "gaode", "securityCode": security_code or ""}

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


class FakeMenuService:
    async def get_menu_tree(self, user=None) -> list[MenuVO]:
        return [
            MenuVO(
                path="/system",
                component=None,
                hidden=False,
                name="system",
                inLayout=True,
                meta=MenuMeta(title="system", icon="system"),
                children=[
                    MenuVO(
                        path="datasource",
                        component="system/datasource",
                        hidden=False,
                        name="datasource",
                        inLayout=True,
                        meta=MenuMeta(title="datasource", icon="datasource"),
                        children=[],
                    ),
                ],
            ),
        ]


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeSystemService, None, None]:
    svc = FakeSystemService()
    app.dependency_overrides[get_system_service] = lambda: svc
    app.dependency_overrides[get_menu_service] = lambda: FakeMenuService()
    yield svc
    _ = app.dependency_overrides.pop(get_system_service, None)
    _ = app.dependency_overrides.pop(get_menu_service, None)


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
    assert data["mapType"] == "gaode"


@pytest.mark.asyncio
async def test_query_online_map_by_type(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeSystemService,
) -> None:
    response = await client.get(
        "/de2api/sysParameter/queryOnlineMap/qq",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data == {"key": "qq-key", "mapType": "qq", "securityCode": "qq-sec"}


@pytest.mark.asyncio
async def test_save_online_map(
    client: AsyncClient,
    auth_headers: dict[str, str],
    fake_service: FakeSystemService,
) -> None:
    response = await client.post(
        "/de2api/sysParameter/saveOnlineMap",
        headers=auth_headers,
        json={"key": "new-map-key", "mapType": "tianditu", "securityCode": "sec-1"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data == {"key": "new-map-key", "mapType": "tianditu", "securityCode": "sec-1"}
    assert fake_service.saved_map_key == "new-map-key"
    assert fake_service.saved_map_type == "tianditu"
    assert fake_service.saved_security_code == "sec-1"


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
