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


_DEFAULT_MAP_TYPE = "gaode"
_online_maps: dict[str, dict[str, str]] = {
    _DEFAULT_MAP_TYPE: {"key": "", "mapType": _DEFAULT_MAP_TYPE, "securityCode": ""}
}
_system_params: dict[str, str | int] = {"requestTimeOut": 120}


@final
class SystemService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.menu_repo = MenuRepository(session)

    async def query_online_map(self) -> OnlineMapResponse:
        payload = _online_maps.get(_DEFAULT_MAP_TYPE) or next(iter(_online_maps.values()), {"key": "", "mapType": _DEFAULT_MAP_TYPE, "securityCode": ""})
        return OnlineMapResponse.model_validate(payload)

    async def query_online_map_by_type(self, map_type: str) -> OnlineMapResponse:
        payload = _online_maps.get(map_type, {"key": "", "mapType": map_type, "securityCode": ""})
        return OnlineMapResponse.model_validate(payload)

    async def save_online_map(self, key: str | None, map_type: str | None = None, security_code: str | None = None) -> OnlineMapResponse:
        normalized_type = map_type or _DEFAULT_MAP_TYPE
        payload = {
            "key": key or "",
            "mapType": normalized_type,
            "securityCode": security_code or "",
        }
        _online_maps[normalized_type] = payload
        if normalized_type == _DEFAULT_MAP_TYPE:
            _online_maps[_DEFAULT_MAP_TYPE] = payload
        return OnlineMapResponse.model_validate(payload)

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
