from __future__ import annotations

from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.org_permission import CoreOrgPermission
from app.models.permission_point import CorePermissionPoint
from app.models.resource_acl import CoreResourceAcl
from app.models.role_permission import CoreRolePermission
from app.models.role_user import CoreRoleUser
from app.models.user_permission import CoreUserPermission
from app.schemas.auth import TokenUser
from app.settings.config import get_settings


_ACL_WEIGHT_BY_PERMISSION_TYPE = {
    "view": 1,
    "use": 2,
    "export": 4,
    "manage": 7,
    "authorize": 9,
}


@final
class PermissionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_effective_menu_ids(self, user_id: int, oid: int) -> set[int]:
        """Compute the effective set of menu IDs a user can see.

        Menu permissions are role-only per product documentation:
        only role-based grants (via core_role_permission) determine
        menu visibility.  User-direct and org-level grant/deny records
        are intentionally ignored for menu resolution.
        """
        # 1. Get role IDs
        role_stmt = select(CoreRoleUser.role_id).where(
            CoreRoleUser.user_id == user_id,
            CoreRoleUser.oid == oid,
        )
        role_result = await self.session.execute(role_stmt)
        role_ids = [row[0] for row in role_result.all()]

        menu_ids: set[int] = set()

        # 2. Role-based grants
        if role_ids:
            role_perm_stmt = (
                select(CorePermissionPoint.menu_id)
                .join(CoreRolePermission, CoreRolePermission.permission_point_id == CorePermissionPoint.id)
                .where(
                    CoreRolePermission.role_id.in_(role_ids),
                    CoreRolePermission.oid.in_([0, oid]),
                    CoreRolePermission.granted.is_(True),
                    CorePermissionPoint.menu_id.isnot(None),
                )
            )
            result = await self.session.execute(role_perm_stmt)
            menu_ids.update(row[0] for row in result.all() if row[0] is not None)

        # Menu permissions are role-only per product documentation.
        # Steps 3 (user-direct grants), 4 (user-direct denials), and
        # 5 (org-level grants) are intentionally skipped for menu resolution.

        return menu_ids

    async def has_resource_permission(self, user: TokenUser, resource_type: str, permission_type: str = "use") -> bool:
        """Check if a user has a specific resource permission."""
        if not self._enforcement_enabled():
            return True
        if user.user_id == 1:
            return True

        role_ids = await self._get_role_ids(user)

        # Find the permission point for this resource_type + permission_type
        point_stmt = select(CorePermissionPoint.id).where(
            CorePermissionPoint.resource_type == resource_type,
            CorePermissionPoint.permission_type == permission_type,
            CorePermissionPoint.menu_id.is_(None),
        )
        point_result = await self.session.execute(point_stmt)
        point_id = point_result.scalar_one_or_none()
        point_allowed, point_denied = await self._check_point_based_permission(point_id, user, role_ids)
        if point_allowed:
            return True
        if point_denied:
            return False

        return await self._check_resource_acl_fallback(user, role_ids, resource_type, permission_type)

    async def require_resource_access(self, user: TokenUser, resource_type: str, permission_type: str = "use") -> None:
        """Raise 403 if user lacks the specified resource permission."""
        if not self._enforcement_enabled():
            return
        if user.user_id == 1:
            return
        has = await self.has_resource_permission(user, resource_type, permission_type)
        if not has:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    async def has_menu_permission(self, user: TokenUser, permission_name: str) -> bool:
        """Check if a user has a specific menu permission point by name.

        Looks up the permission point by name (e.g. "menu:role-management:use"),
        then checks role-based, user-direct, and org-level grants.
        """
        if not self._enforcement_enabled():
            return True
        if user.user_id == 1:
            return True

        point_stmt = select(CorePermissionPoint.id).where(
            CorePermissionPoint.name == permission_name,
        )
        point_id = (await self.session.execute(point_stmt)).scalar_one_or_none()
        if point_id is None:
            return False

        role_ids = await self._get_role_ids(user)
        allowed, denied = await self._check_point_based_permission(point_id, user, role_ids)
        if allowed:
            return True
        if denied:
            return False

        return False

    async def require_menu_permission(self, user: TokenUser, permission_name: str) -> None:
        """Raise 403 if user lacks the specified menu permission."""
        if not self._enforcement_enabled():
            return
        if user.user_id == 1:
            return
        if not await self.has_menu_permission(user, permission_name):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    @staticmethod
    def _enforcement_enabled() -> bool:
        return get_settings().permission_enforcement_enabled

    async def _get_role_ids(self, user: TokenUser) -> list[int]:
        role_stmt = select(CoreRoleUser.role_id).where(
            CoreRoleUser.user_id == user.user_id,
            CoreRoleUser.oid == user.oid,
        )
        role_result = await self.session.execute(role_stmt)
        return [row[0] for row in role_result.all()]

    async def _check_point_based_permission(
        self,
        point_id: int | None,
        user: TokenUser,
        role_ids: list[int],
    ) -> tuple[bool, bool]:
        if point_id is None:
            return False, False

        if role_ids:
            role_perm_stmt = select(CoreRolePermission.id).where(
                CoreRolePermission.role_id.in_(role_ids),
                CoreRolePermission.permission_point_id == point_id,
                CoreRolePermission.oid.in_([0, user.oid]),
                CoreRolePermission.granted.is_(True),
            ).limit(1)
            if (await self.session.execute(role_perm_stmt)).scalar_one_or_none() is not None:
                return True, False

        user_grant_stmt = select(CoreUserPermission.id).where(
            CoreUserPermission.user_id == user.user_id,
            CoreUserPermission.permission_point_id == point_id,
            CoreUserPermission.granted.is_(True),
        ).limit(1)
        if (await self.session.execute(user_grant_stmt)).scalar_one_or_none() is not None:
            return True, False

        user_deny_stmt = select(CoreUserPermission.id).where(
            CoreUserPermission.user_id == user.user_id,
            CoreUserPermission.permission_point_id == point_id,
            CoreUserPermission.granted.is_(False),
        ).limit(1)
        if (await self.session.execute(user_deny_stmt)).scalar_one_or_none() is not None:
            return False, True

        org_grant_stmt = select(CoreOrgPermission.id).where(
            CoreOrgPermission.org_id == user.oid,
            CoreOrgPermission.permission_point_id == point_id,
            CoreOrgPermission.granted.is_(True),
        ).limit(1)
        if (await self.session.execute(org_grant_stmt)).scalar_one_or_none() is not None:
            return True, False

        return False, False

    async def _check_resource_acl_fallback(
        self,
        user: TokenUser,
        role_ids: list[int],
        resource_type: str,
        permission_type: str,
    ) -> bool:
        required_weight = _ACL_WEIGHT_BY_PERMISSION_TYPE.get(permission_type)
        if required_weight is None:
            return False

        if await self._has_resource_acl_grant(resource_type, required_weight, "user", [user.user_id]):
            return True
        if await self._has_resource_acl_grant(resource_type, required_weight, "org", [user.oid]):
            return True
        if role_ids and await self._has_resource_acl_grant(resource_type, required_weight, "role", role_ids):
            return True
        return False

    async def _has_resource_acl_grant(
        self,
        resource_type: str,
        required_weight: int,
        target_type: str,
        target_ids: list[int],
    ) -> bool:
        if not target_ids:
            return False

        stmt = select(CoreResourceAcl.id).where(
            CoreResourceAcl.target_type == target_type,
            CoreResourceAcl.target_id.in_(target_ids),
            CoreResourceAcl.resource_type == resource_type,
            CoreResourceAcl.weight >= required_weight,
        ).limit(1)
        return (await self.session.execute(stmt)).scalar_one_or_none() is not None


async def get_permission_service(session: AsyncSession = Depends(get_db)) -> PermissionService:
    return PermissionService(session)
