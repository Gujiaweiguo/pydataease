from __future__ import annotations

from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.org_permission import CoreOrgPermission
from app.models.permission_point import CorePermissionPoint
from app.models.role_permission import CoreRolePermission
from app.models.role_user import CoreRoleUser
from app.models.user_permission import CoreUserPermission
from app.schemas.auth import TokenUser
from app.settings.config import get_settings


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

        # Find the permission point for this resource_type + permission_type
        point_stmt = select(CorePermissionPoint.id).where(
            CorePermissionPoint.resource_type == resource_type,
            CorePermissionPoint.permission_type == permission_type,
            CorePermissionPoint.menu_id.is_(None),
        )
        point_result = await self.session.execute(point_stmt)
        point_id = point_result.scalar_one_or_none()
        if point_id is None:
            # BUG-008 fix: No permission point defined means no access (fail-closed)
            # Admin users (uid=1) are already handled above
            return False

        # Check role-based grants
        role_stmt = select(CoreRoleUser.role_id).where(
            CoreRoleUser.user_id == user.user_id,
            CoreRoleUser.oid == user.oid,
        )
        role_result = await self.session.execute(role_stmt)
        role_ids = [row[0] for row in role_result.all()]

        if role_ids:
            role_perm_stmt = select(CoreRolePermission.id).where(
                CoreRolePermission.role_id.in_(role_ids),
                CoreRolePermission.permission_point_id == point_id,
                CoreRolePermission.oid.in_([0, user.oid]),
                CoreRolePermission.granted.is_(True),
            ).limit(1)
            if (await self.session.execute(role_perm_stmt)).scalar_one_or_none() is not None:
                return True

        # Check user-direct grants
        user_grant_stmt = select(CoreUserPermission.id).where(
            CoreUserPermission.user_id == user.user_id,
            CoreUserPermission.permission_point_id == point_id,
            CoreUserPermission.granted.is_(True),
        ).limit(1)
        if (await self.session.execute(user_grant_stmt)).scalar_one_or_none() is not None:
            return True

        # Check user-direct denials (explicit denial overrides everything)
        user_deny_stmt = select(CoreUserPermission.id).where(
            CoreUserPermission.user_id == user.user_id,
            CoreUserPermission.permission_point_id == point_id,
            CoreUserPermission.granted.is_(False),
        ).limit(1)
        if (await self.session.execute(user_deny_stmt)).scalar_one_or_none() is not None:
            return False

        # Check org-level grants
        org_grant_stmt = select(CoreOrgPermission.id).where(
            CoreOrgPermission.org_id == user.oid,
            CoreOrgPermission.permission_point_id == point_id,
            CoreOrgPermission.granted.is_(True),
        ).limit(1)
        if (await self.session.execute(org_grant_stmt)).scalar_one_or_none() is not None:
            return True

        return False

    async def require_resource_access(self, user: TokenUser, resource_type: str, permission_type: str = "use") -> None:
        """Raise 403 if user lacks the specified resource permission."""
        if not self._enforcement_enabled():
            return
        if user.user_id == 1:
            return
        has = await self.has_resource_permission(user, resource_type, permission_type)
        if not has:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    @staticmethod
    def _enforcement_enabled() -> bool:
        return get_settings().permission_enforcement_enabled


async def get_permission_service(session: AsyncSession = Depends(get_db)) -> PermissionService:
    return PermissionService(session)
