from __future__ import annotations

from collections import defaultdict

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.system import CoreMenu
from app.repositories.system_repo import MenuRepository
from app.schemas.auth import TokenUser
from app.schemas.menu import MenuMeta, MenuVO
from app.services.permission_service import PermissionService
from app.settings.config import get_settings

TITLE_MAP: dict[str, str] = {
    "workbranch": "工作台",
    "panel": "仪表板",
    "screen": "数据大屏",
    "data": "数据准备",
    "dataset": "数据集",
    "datasource": "数据源",
    "sys-setting": "系统设置",
    "parameter": "系统参数",
    "org-management": "组织管理",
    "user-management": "用户管理",
    "role-management": "角色管理",
    "permission-management": "权限管理",
}


class MenuService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = MenuRepository(session)
        self.session = session

    async def get_menu_tree(self, user: TokenUser) -> list[MenuVO]:
        rows = await self.repo.list_all()
        by_pid: dict[int, list[CoreMenu]] = defaultdict(list)
        for row in rows:
            by_pid[row.pid].append(row)

        # Admin or disabled enforcement: return full tree
        if user.user_id == 1 or not get_settings().permission_enforcement_enabled:
            return self._build_children(0, by_pid)

        # Compute effective menu IDs from permissions
        perm_service = PermissionService(self.session)
        effective_ids = await perm_service.get_effective_menu_ids(user.user_id, user.oid)

        return self._build_children_filtered(0, by_pid, effective_ids)

    def _normalize_path(self, path: str, pid: int) -> str:
        """Strip leading '/' from non-root menu paths, matching Java MenuManage behavior."""
        if pid != 0 and path.startswith("/"):
            return path[1:]
        return path

    def _build_children(self, pid: int, by_pid: dict[int, list[CoreMenu]]) -> list[MenuVO]:
        result: list[MenuVO] = []
        for row in by_pid.get(pid, []):
            title = TITLE_MAP.get(row.name or "", "")
            path = self._normalize_path(row.path or "", row.pid)
            children = self._build_children(row.id, by_pid)
            if row.type == 1 and not row.component:
                # Directory node with no direct component — only include if has children
                if not children:
                    continue
                result.append(
                    MenuVO(
                        path=path,
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
                        path=path,
                        component=row.component,
                        hidden=row.hidden,
                        name=row.name or "",
                        inLayout=row.in_layout,
                        meta=MenuMeta(title=title, icon=row.icon),
                        children=[],
                    )
                )
        return result

    def _build_children_filtered(
        self, pid: int, by_pid: dict[int, list[CoreMenu]], effective_ids: set[int]
    ) -> list[MenuVO]:
        """Build menu tree but only include menu items whose IDs are in effective_ids.

        Parent directories are kept if they have at least one visible child.
        Menu items with auth=False (non-gated) are always included.
        """
        result: list[MenuVO] = []
        for row in by_pid.get(pid, []):
            title = TITLE_MAP.get(row.name or "", "")
            path = self._normalize_path(row.path or "", row.pid)
            children = self._build_children_filtered(row.id, by_pid, effective_ids)

            # Non-auth-gated menus are always visible
            is_visible = (not row.auth) or (row.id in effective_ids)

            if row.type == 1 and not row.component:
                # Directory node — include if has visible children (even if directory itself is not in effective set)
                if not children and not is_visible:
                    continue
                result.append(
                    MenuVO(
                        path=path,
                        component=None,
                        hidden=row.hidden,
                        name=row.name or "",
                        inLayout=row.in_layout,
                        meta=MenuMeta(title=title, icon=row.icon),
                        children=children,
                    )
                )
            else:
                # Leaf node — only include if visible
                if not is_visible:
                    continue
                result.append(
                    MenuVO(
                        path=path,
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
