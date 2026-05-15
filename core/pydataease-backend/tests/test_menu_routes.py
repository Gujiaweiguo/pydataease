from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt
from httpx import AsyncClient

from app.main import app
from app.schemas.menu import MenuMeta, MenuVO
from app.services.menu_service import get_menu_service
from app.settings.config import get_settings


_FAKE_TREE: list[MenuVO] = [
    MenuVO(
        path="/workbranch",
        component="workbranch/index",
        hidden=False,
        name="workbranch",
        inLayout=True,
        meta=MenuMeta(title="工作台"),
        children=[],
    ),
    MenuVO(
        path="/data",
        component=None,
        hidden=False,
        name="data",
        inLayout=True,
        meta=MenuMeta(title="数据准备"),
        children=[
            MenuVO(
                path="dataset",
                component="data/dataset",
                hidden=False,
                name="dataset",
                inLayout=True,
                meta=MenuMeta(title="数据集"),
                children=[],
            ),
        ],
    ),
]


class FakeMenuService:
    async def get_menu_tree(self, user=None) -> list[MenuVO]:
        return _FAKE_TREE


@pytest.fixture(autouse=True)
def _override_menu_service():
    app.dependency_overrides[get_menu_service] = lambda: FakeMenuService()
    yield
    app.dependency_overrides.pop(get_menu_service, None)


def _build_token(user_id: int = 1, oid: int = 1) -> str:
    settings = get_settings()
    payload = {"uid": user_id, "oid": oid, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


@pytest.mark.asyncio
async def test_menu_query_authenticated_returns_200(client: AsyncClient) -> None:
    token = _build_token()
    response = await client.get("/de2api/menu/query", headers={"X-DE-TOKEN": token})

    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    tree = data["data"]
    assert isinstance(tree, list)
    assert len(tree) >= 1
    assert tree[0]["name"] == "workbranch"
    assert tree[0]["meta"]["title"] == "工作台"


@pytest.mark.asyncio
async def test_menu_query_unauthenticated_returns_401(client: AsyncClient) -> None:
    response = await client.get("/de2api/menu/query")

    assert response.status_code == 401
    assert response.json()["code"] == 401
