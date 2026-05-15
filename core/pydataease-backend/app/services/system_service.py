from __future__ import annotations

from typing import final

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.system import CoreMenu
from app.repositories.system_repo import MenuRepository
from app.schemas.system import MenuTreeNodeResponse, OnlineMapResponse


def _build_menu_tree(menus: list[CoreMenu]) -> list[MenuTreeNodeResponse]:
    nodes: dict[int, MenuTreeNodeResponse] = {}
    for m in menus:
        node = MenuTreeNodeResponse.model_validate(m)
        node.children = []
        nodes[m.id] = node

    roots: list[MenuTreeNodeResponse] = []
    for m in menus:
        node = nodes[m.id]
        if m.pid == 0 or m.pid not in nodes:
            roots.append(node)
        else:
            nodes[m.pid].children.append(node)
    return roots


_system_params: dict[str, str | int] = {
    "onlineMapKey": "",
    "requestTimeOut": 120,
}


@final
class SystemService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.menu_repo = MenuRepository(session)

    async def query_online_map(self) -> OnlineMapResponse:
        key = _system_params.get("onlineMapKey", "")
        return OnlineMapResponse(key=str(key))

    async def save_online_map(self, key: str | None) -> OnlineMapResponse:
        _system_params["onlineMapKey"] = key or ""
        return OnlineMapResponse(key=key or "")

    async def request_timeout(self) -> int:
        return int(_system_params.get("requestTimeOut", 120))

    async def query_menus(self) -> list[MenuTreeNodeResponse]:
        menus = await self.menu_repo.list_all()
        return _build_menu_tree(list(menus))

    async def list_fonts(self) -> list[object]:
        return []

    async def default_font(self) -> object:
        return None

    async def get_area_entities(self, pcode: str) -> list[object]:
        return []


async def get_system_service(
    session: AsyncSession = Depends(get_db),
) -> SystemService:
    return SystemService(session)
