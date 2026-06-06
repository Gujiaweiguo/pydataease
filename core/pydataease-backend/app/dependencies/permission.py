from __future__ import annotations

from fastapi import Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.services.permission_service import PermissionService, get_permission_service


def require_resource(resource_type: str, permission_type: str = "use"):
    """FastAPI dependency that enforces resource-level permission."""

    async def checker(
        user: TokenUser = Depends(get_current_user),
        service: PermissionService = Depends(get_permission_service),
    ) -> TokenUser:
        await service.require_resource_access(user, resource_type, permission_type)
        return user

    return checker


def require_menu_permission(permission_name: str):
    """FastAPI dependency that enforces menu-level permission by permission-point name.

    Raises 403 if the current user does not hold *permission_name* (e.g.
    ``"menu:role-management:use"``) through role, user-direct, or org grants.
    """

    async def _guard(
        user: TokenUser = Depends(get_current_user),
        service: PermissionService = Depends(get_permission_service),
    ) -> None:
        await service.require_menu_permission(user, permission_name)

    _guard.__name__ = f"require_menu_permission_{permission_name.replace(':', '_').replace('-', '_')}"
    return _guard
