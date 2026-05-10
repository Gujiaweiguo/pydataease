from __future__ import annotations

from collections import defaultdict

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.system import CoreMenu
from app.repositories.system_repo import MenuRepository
from app.schemas.menu import MenuMeta, MenuVO

TITLE_MAP: dict[str, str] = {
    "workbranch": "工作台",
    "panel": "仪表板",
    "screen": "数据大屏",
    "data": "数据准备",
    "dataset": "数据集",
    "datasource": "数据源",
    "sys-setting": "系统设置",
    "parameter": "系统参数",
}


class MenuService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = MenuRepository(session)

    async def get_menu_tree(self) -> list[MenuVO]:
        rows = await self.repo.list_all()
        by_pid: dict[int, list[CoreMenu]] = defaultdict(list)
        for row in rows:
            by_pid[row.pid].append(row)
        return self._build_children(0, by_pid)

    def _build_children(self, pid: int, by_pid: dict[int, list[CoreMenu]]) -> list[MenuVO]:
        result: list[MenuVO] = []
        for row in by_pid.get(pid, []):
            title = TITLE_MAP.get(row.name or "", "")
            children = self._build_children(row.id, by_pid)
            if row.type == 1 and not row.component:
                # Directory node with no direct component — only include if has children
                if not children:
                    continue
                result.append(
                    MenuVO(
                        path=row.path or "",
                        component=None,
                        hidden=row.hidden,
                        name=row.name or "",
                        inLayout=row.in_layout,
                        meta=MenuMeta(title=title, icon=row.icon),
                        children=children,
                    )
                )
            else:
                result.append(
                    MenuVO(
                        path=row.path or "",
                        component=row.component,
                        hidden=row.hidden,
                        name=row.name or "",
                        inLayout=row.in_layout,
                        meta=MenuMeta(title=title, icon=row.icon),
                        children=[],
                    )
                )
        return result


async def get_menu_service(session: AsyncSession = Depends(get_db)) -> MenuService:
    return MenuService(session)
