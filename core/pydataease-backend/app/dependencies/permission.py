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
