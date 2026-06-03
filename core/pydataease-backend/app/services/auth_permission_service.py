from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any, final

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.org import CoreOrg
from app.models.org_permission import CoreOrgPermission
from app.models.resource_acl import CoreResourceAcl
from app.models.role import CoreRole
from app.models.role_user import CoreRoleUser
from app.models.role_permission import CoreRolePermission
from app.models.system import CoreMenu
from app.models.user import CoreUser
from app.models.user_org import CoreUserOrg
from app.models.user_permission import CoreUserPermission
from app.repositories.auth_permission_repo import AuthPermissionRepository
from app.schemas.auth import TokenUser
from app.schemas.auth_permission import (
    BusiPerEditor,
    BusiPermissionRequest,
    BusiTargetPerCreator,
    MenuPerEditor,
    MenuPermissionRequest,
    MenuTargetPerCreator,
    PermissionItem,
    PermissionOrigin,
    PermissionVO,
    ResourceVO,
)
from app.settings.config import get_settings
from app.utils.id_utils import _sid

_SUPPORTED_BUSI_FLAGS = {"dashboard", "screen", "dataset", "datasource"}
_VISUALIZATION_TYPE_MAP = {"dashboard": "panel", "screen": "screen"}
_ORG_ADMIN_ROLE_ID = 2


def _build_resource_tree(nodes: list[dict[str, Any]], pid: str = "0") -> list[dict[str, Any]]:
    """Build recursive tree from flat node list (same as InteractiveTreeService._build_tree)."""
    children: list[dict[str, Any]] = []
    for node in nodes:
        if node.get("pid", "0") == pid:
            node_copy = dict(node)
            node_copy["children"] = _build_resource_tree(nodes, node["id"])
            children.append(node_copy)
    return children


def _target_type_str(type_int: int) -> str:
    """Convert permission type int to string: 0→'user', 1→'role', 2→'org'."""
    mapping = {0: "user", 1: "role", 2: "org"}
    try:
        return mapping[type_int]
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported target type") from exc


@final
class AuthPermissionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = AuthPermissionRepository(session)

    async def get_menu_resource_tree(self, user: TokenUser) -> list[ResourceVO]:
        rows = await self.repo.get_menu_tree_nodes()
        flat = [self._menu_row_to_node(row) for row in self._filter_menu_rows(rows, user)]
        return [ResourceVO.model_validate(item) for item in _build_resource_tree(flat, pid="0")]

    async def get_busi_resource_tree(self, flag: str, user: TokenUser) -> list[ResourceVO]:
        del user
        self._validate_busi_flag(flag)

        if flag in _VISUALIZATION_TYPE_MAP:
            rows = await self.repo.get_visualization_tree(_VISUALIZATION_TYPE_MAP[flag])
            flat = [
                {
                    "id": _sid(row.id),
                    "name": row.name or "",
                    "pid": _sid(row.pid) if row.pid else "0",
                    "leaf": row.node_type == "leaf" if row.node_type else True,
                    "extraFlag": 0,
                }
                for row in rows
            ]
            children = _build_resource_tree(flat, pid="0")
        elif flag == "dataset":
            rows = await self.repo.get_dataset_tree()
            flat = [
                {
                    "id": _sid(row.id),
                    "name": row.name or "",
                    "pid": _sid(row.pid) if row.pid else "0",
                    "leaf": row.node_type == "dataset" if row.node_type else True,
                    "extraFlag": 0,
                }
                for row in rows
            ]
            children = _build_resource_tree(flat, pid="0")
        else:
            rows = await self.repo.get_datasource_tree()
            children = [
                {
                    "id": _sid(row.id),
                    "name": row.name or "",
                    "children": [],
                    "leaf": True,
                    "extraFlag": 0,
                }
                for row in rows
            ]

        root = ResourceVO(id="0", name="root", children=[ResourceVO.model_validate(item) for item in children], leaf=False, extra_flag=0)
        return [root]

    async def get_busi_permission(self, request: BusiPermissionRequest, user: TokenUser) -> PermissionVO:
        target_type = self._target_type_from_int(request.type)
        self._validate_busi_flag(request.flag)
        await self._assert_target_in_scope(target_type, request.id, user)
        entries = await self.repo.get_resource_acl(target_type, request.id, request.flag)
        permissions = [self._permission_item_from_acl(entry) for entry in entries]
        return PermissionVO(
            root=self._is_root_access(user),
            readonly=not await self._can_manage_auth(user, target_type, request.id),
            permissions=permissions,
        )

    async def get_menu_permission(self, request: MenuPermissionRequest, user: TokenUser) -> PermissionVO:
        target_type = await self._infer_target_type(request.id, user.oid)
        await self._assert_target_in_scope(target_type, request.id, user)
        oid = await self._menu_grant_oid(target_type, user, request.id)
        grants = await self.repo.get_menu_point_grants(target_type, request.id, oid)
        permissions = [PermissionItem(id=menu_id, weight=1 if granted else 0) for menu_id, granted in grants.items()]
        return PermissionVO(
            root=self._is_root_access(user),
            readonly=not await self._can_manage_auth(user, target_type, request.id),
            permissions=permissions,
        )

    async def save_busi_per(self, editor: BusiPerEditor, user: TokenUser) -> None:
        self._validate_busi_flag(editor.flag)
        target_type = self._target_type_from_int(editor.type)
        await self._require_auth_manage_permission(user, target_type, editor.id)
        entries = [
            CoreResourceAcl(
                id=time.time_ns() + index,
                target_type=target_type,
                target_id=editor.id,
                resource_type=editor.flag,
                resource_id=int(item.id),
                weight=item.weight,
                ext=item.ext,
            )
            for index, item in enumerate(editor.permissions)
        ]
        if entries:
            await self.repo.save_resource_acl(entries)
        else:
            await self.repo.delete_resource_acl(target_type, editor.id, editor.flag)

    async def save_menu_per(self, editor: MenuPerEditor, user: TokenUser) -> None:
        target_type = await self._infer_target_type(editor.id, user.oid)
        await self._require_auth_manage_permission(user, target_type, editor.id)
        oid = await self._menu_grant_oid(target_type, user, editor.id)
        grants = [(int(item.id), True) for item in editor.permissions]
        await self.repo.save_menu_point_grants(target_type, editor.id, oid, grants)

    async def get_busi_target_permission(self, request: BusiPermissionRequest, user: TokenUser) -> PermissionVO:
        if self._is_root_access(user):
            return PermissionVO(root=True, readonly=False)

        self._validate_busi_flag(request.flag)
        stmt = (
            select(CoreResourceAcl)
            .where(
                CoreResourceAcl.resource_id == request.id,
                CoreResourceAcl.resource_type == request.flag,
            )
            .order_by(CoreResourceAcl.target_type.asc(), CoreResourceAcl.target_id.asc(), CoreResourceAcl.id.asc())
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        permissions = [
            PermissionItem(id=row.target_id, weight=row.weight, ext=row.ext)
            for row in rows
        ]
        origins = await self._build_target_origins(
            [(row.target_type, row.target_id, self._permission_item_from_target_acl(row)) for row in rows]
        )
        return PermissionVO(
            root=False,
            readonly=not await self._can_manage_auth(user),
            permissions=permissions,
            permission_origins=origins,
        )

    async def get_menu_target_permission(self, request: MenuPermissionRequest, user: TokenUser) -> PermissionVO:
        if self._is_root_access(user):
            return PermissionVO(root=True, readonly=False)

        point_ids = [point.id for point in await self.repo.get_permission_points_by_menu(request.id)]
        if not point_ids:
            return PermissionVO(
                root=False,
                readonly=not await self._can_manage_auth(user),
                permissions=[],
                permission_origins=[],
            )

        rows = await self._get_menu_target_rows(point_ids)
        permissions = [PermissionItem(id=row[1], weight=1 if row[2] else 0) for row in rows]
        origins = await self._build_target_origins(
            [(row[0], row[1], PermissionItem(id=row[1], weight=1 if row[2] else 0)) for row in rows]
        )
        return PermissionVO(
            root=False,
            readonly=not await self._can_manage_auth(user),
            permissions=permissions,
            permission_origins=origins,
        )

    async def save_busi_target_per(self, creator: BusiTargetPerCreator, user: TokenUser) -> None:
        await self._require_auth_manage_permission(user)
        self._validate_busi_flag(creator.flag)
        target_type = self._target_type_from_int(creator.type)

        for target_id in creator.ids:
            entries = [
                CoreResourceAcl(
                    id=time.time_ns() + index,
                    target_type=target_type,
                    target_id=target_id,
                    resource_type=creator.flag,
                    resource_id=int(item.id),
                    weight=item.weight,
                    ext=item.ext,
                )
                for index, item in enumerate(creator.permissions)
            ]
            if entries:
                await self.repo.save_resource_acl(entries)
            else:
                await self.repo.delete_resource_acl(target_type, target_id, creator.flag)

    async def save_menu_target_per(self, creator: MenuTargetPerCreator, user: TokenUser) -> None:
        await self._require_auth_manage_permission(user)

        for target_id in creator.ids:
            target_type = await self._infer_target_type(target_id, user.oid)
            oid = await self._menu_grant_oid(target_type, user, target_id)
            grants = [(int(item.id), True) for item in creator.permissions]
            await self.repo.save_menu_point_grants(target_type, target_id, oid, grants)

    async def _require_auth_manage_permission(
        self,
        user: TokenUser,
        target_type: str | None = None,
        target_id: int | None = None,
    ) -> None:
        if await self._can_manage_auth(user, target_type, target_id):
            return
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    def _target_type_from_int(self, type_int: int) -> str:
        return _target_type_str(type_int)

    async def _infer_target_type(self, target_id: int, oid: int) -> str:
        matches: list[str] = []

        role_exists = (
            await self.session.execute(select(CoreRole.id).where(CoreRole.id == target_id, CoreRole.oid.in_([0, oid])).limit(1))
        ).scalar_one_or_none()
        if role_exists is not None:
            matches.append("role")

        user_exists = (
            await self.session.execute(
                select(CoreUser.id)
                .join(CoreUserOrg, CoreUserOrg.user_id == CoreUser.id)
                .where(CoreUser.id == target_id, CoreUserOrg.org_id == oid)
                .limit(1)
            )
        ).scalar_one_or_none()
        if user_exists is not None:
            matches.append("user")

        org_exists = (
            await self.session.execute(select(CoreOrg.id).where(CoreOrg.id == target_id, CoreOrg.id == oid).limit(1))
        ).scalar_one_or_none()
        if org_exists is not None:
            matches.append("org")

        if len(matches) == 1:
            return matches[0]
        if role_exists is not None:
            return "role"
        if not matches:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ambiguous target type")

    async def _get_menu_target_rows(self, point_ids: list[int]) -> list[tuple[str, int, bool]]:
        role_rows = [
            ("role", int(role_id), granted)
            for role_id, granted in (
                await self.session.execute(
                    select(CoreRolePermission.role_id, CoreRolePermission.granted).where(
                        CoreRolePermission.permission_point_id.in_(point_ids)
                    )
                )
            ).all()
        ]
        user_rows = [
            ("user", int(user_id), granted)
            for user_id, granted in (
                await self.session.execute(
                    select(CoreUserPermission.user_id, CoreUserPermission.granted).where(
                        CoreUserPermission.permission_point_id.in_(point_ids)
                    )
                )
            ).all()
        ]
        org_rows = [
            ("org", int(org_id), granted)
            for org_id, granted in (
                await self.session.execute(
                    select(CoreOrgPermission.org_id, CoreOrgPermission.granted).where(
                        CoreOrgPermission.permission_point_id.in_(point_ids)
                    )
                )
            ).all()
        ]
        return [*role_rows, *user_rows, *org_rows]

    async def _build_target_origins(
        self,
        rows: list[tuple[str, int, PermissionItem]],
    ) -> list[PermissionOrigin]:
        grouped: dict[tuple[str, int], list[PermissionItem]] = {}
        for target_type, target_id, item in rows:
            grouped.setdefault((target_type, target_id), []).append(item)

        role_ids = [target_id for target_type, target_id in grouped if target_type == "role"]
        user_ids = [target_id for target_type, target_id in grouped if target_type == "user"]
        org_ids = [target_id for target_type, target_id in grouped if target_type == "org"]

        role_names = await self._load_name_map(CoreRole, role_ids)
        user_names = await self._load_name_map(CoreUser, user_ids, fallback_attr="account")
        org_names = await self._load_name_map(CoreOrg, org_ids)

        origins: list[PermissionOrigin] = []
        for target_type, target_id in sorted(grouped.keys(), key=lambda item: (item[0], item[1])):
            if target_type == "role":
                name = role_names.get(target_id, str(target_id))
            elif target_type == "user":
                name = user_names.get(target_id, str(target_id))
            else:
                name = org_names.get(target_id, str(target_id))
            origins.append(PermissionOrigin(id=target_id, name=name, permissions=grouped[(target_type, target_id)]))
        return origins

    async def _load_name_map(
        self,
        model: type[CoreRole] | type[CoreUser] | type[CoreOrg],
        ids: list[int],
        fallback_attr: str | None = None,
    ) -> dict[int, str]:
        if not ids:
            return {}
        result = await self.session.execute(select(model).where(model.id.in_(ids)))
        items = result.scalars().all()
        mapping: dict[int, str] = {}
        for item in items:
            name = getattr(item, "name", None) or (getattr(item, fallback_attr) if fallback_attr else None) or str(item.id)
            mapping[int(item.id)] = str(name)
        return mapping

    def _validate_busi_flag(self, flag: str) -> None:
        if flag not in _SUPPORTED_BUSI_FLAGS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported resource flag")

    def _menu_row_to_node(self, row: CoreMenu) -> dict[str, Any]:
        return {
            "id": _sid(row.id),
            "name": row.name or "",
            "pid": _sid(row.pid) if row.pid else "0",
            "leaf": bool(row.type != 1 or row.component),
            "extraFlag": 0,
        }

    def _filter_menu_rows(self, rows: Sequence[CoreMenu], user: TokenUser) -> list[CoreMenu]:
        del user
        return list(rows)

    def _permission_item_from_acl(self, entry: CoreResourceAcl) -> PermissionItem:
        return PermissionItem(id=entry.resource_id, weight=entry.weight, ext=entry.ext)

    def _permission_item_from_target_acl(self, entry: CoreResourceAcl) -> PermissionItem:
        return PermissionItem(id=entry.target_id, weight=entry.weight, ext=entry.ext)

    def _is_root_access(self, user: TokenUser) -> bool:
        return user.user_id == 1 or not get_settings().permission_enforcement_enabled

    async def _can_manage_auth(
        self,
        user: TokenUser,
        target_type: str | None = None,
        target_id: int | None = None,
    ) -> bool:
        if self._is_root_access(user):
            return True

        is_org_admin = (
            await self.session.execute(
                select(CoreRoleUser.id).where(
                    CoreRoleUser.user_id == user.user_id,
                    CoreRoleUser.role_id == _ORG_ADMIN_ROLE_ID,
                    CoreRoleUser.oid == user.oid,
                ).limit(1)
            )
        ).scalar_one_or_none()
        if is_org_admin is None:
            return False

        if target_type is None or target_id is None:
            return True

        return await self._is_target_manageable(target_type, target_id, user)

    async def _assert_target_in_scope(self, target_type: str, target_id: int, user: TokenUser) -> None:
        if self._is_root_access(user):
            return
        if not await self._is_target_in_scope(target_type, target_id, user):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")

    async def _is_target_in_scope(self, target_type: str, target_id: int, user: TokenUser) -> bool:
        if target_type == "role":
            return (
                await self.session.execute(
                    select(CoreRole.id).where(CoreRole.id == target_id, CoreRole.oid.in_([0, user.oid])).limit(1)
                )
            ).scalar_one_or_none() is not None

        if target_type == "user":
            return (
                await self.session.execute(
                    select(CoreUserOrg.id).where(CoreUserOrg.user_id == target_id, CoreUserOrg.org_id == user.oid).limit(1)
                )
            ).scalar_one_or_none() is not None

        if target_type == "org":
            return target_id == user.oid

        return False

    async def _is_target_manageable(self, target_type: str, target_id: int, user: TokenUser) -> bool:
        if target_type == "role":
            role_oid = (
                await self.session.execute(select(CoreRole.oid).where(CoreRole.id == target_id).limit(1))
            ).scalar_one_or_none()
            return role_oid == user.oid

        if target_type == "user":
            return (
                await self.session.execute(
                    select(CoreUserOrg.id).where(CoreUserOrg.user_id == target_id, CoreUserOrg.org_id == user.oid).limit(1)
                )
            ).scalar_one_or_none() is not None

        if target_type == "org":
            return target_id == user.oid

        return False

    async def _menu_grant_oid(self, target_type: str, user: TokenUser, target_id: int) -> int:
        if target_type != "role":
            return 0
        # Use the role's own oid, not the current user's oid.
        # Global roles (oid=0) store their grants with oid=0.
        role_oid = (
            await self.session.execute(select(CoreRole.oid).where(CoreRole.id == target_id).limit(1))
        ).scalar_one_or_none()
        return role_oid if role_oid is not None else user.oid


async def get_auth_permission_service(session: AsyncSession = Depends(get_db)) -> AuthPermissionService:
    return AuthPermissionService(session)
