"""Tests for the menu-permission guard (require_menu_permission).

Tests at the PermissionService level using the real database to verify:
  - Admin (user_id=1) always passes menu permission checks.
  - Permission lookup works correctly against seeded permission points.
  - Enforcement toggle works correctly.
  - require_menu_permission raises 403 for unauthorized users.
  - The dependency factory produces correctly named guard functions.

Requires a running PostgreSQL (db_session fixture).
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.permission import require_menu_permission  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.services.permission_service import PermissionService  # pyright: ignore[reportImplicitRelativeImport]


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------


class TestPermissionServiceMenuCheck:
    """Unit tests for PermissionService.has_menu_permission / require_menu_permission."""

    @pytest.mark.asyncio
    async def test_admin_always_passes(self, db_session: AsyncSession) -> None:
        svc = PermissionService(db_session)
        admin = TokenUser(user_id=1, oid=0, language="zh-CN")
        assert await svc.has_menu_permission(admin, "menu:role-management:use") is True
        await svc.require_menu_permission(admin, "menu:role-management:use")

    @pytest.mark.asyncio
    async def test_bypass_when_enforcement_disabled(self, db_session: AsyncSession) -> None:
        svc = PermissionService(db_session)
        user = TokenUser(user_id=999, oid=99, language="zh-CN")
        with patch.object(svc, "_enforcement_enabled", return_value=False):
            assert await svc.has_menu_permission(user, "menu:role-management:use") is True
            await svc.require_menu_permission(user, "menu:role-management:use")

    @pytest.mark.asyncio
    async def test_unknown_permission_point_returns_false(self, db_session: AsyncSession) -> None:
        svc = PermissionService(db_session)
        user = TokenUser(user_id=999, oid=99, language="zh-CN")
        assert await svc.has_menu_permission(user, "menu:nonexistent:use") is False

    @pytest.mark.asyncio
    async def test_require_raises_403_for_unauthorized(self, db_session: AsyncSession) -> None:
        svc = PermissionService(db_session)
        user = TokenUser(user_id=999, oid=1, language="zh-CN")
        with pytest.raises(HTTPException) as exc_info:
            await svc.require_menu_permission(user, "menu:role-management:use")
        assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# Integration tests with seed data (real DB)
# ---------------------------------------------------------------------------


# The seed data user bound to role_id=3 (普通用户) in oid=1.
_SEED_REGULAR_USER_ID = 1780033653117563687


class TestMenuPermissionWithSeedData:
    """Verify that seeded permission points are correctly resolved."""

    @pytest.mark.asyncio
    async def test_admin_has_all_management_permissions(self, db_session: AsyncSession) -> None:
        svc = PermissionService(db_session)
        admin = TokenUser(user_id=1, oid=0, language="zh-CN")
        for perm in [
            "menu:role-management:use",
            "menu:user-management:use",
            "menu:org-management:use",
            "menu:permission-management:use",
            "menu:parameter:use",
            "menu:auth-provider:use",
            "menu:watermark:use",
            "menu:sys-variable:use",
        ]:
            assert await svc.has_menu_permission(admin, perm) is True

    @pytest.mark.asyncio
    async def test_seed_user_with_regular_role_lacks_management(self, db_session: AsyncSession) -> None:
        svc = PermissionService(db_session)
        user = TokenUser(user_id=_SEED_REGULAR_USER_ID, oid=1, language="zh-CN")
        for perm in [
            "menu:role-management:use",
            "menu:user-management:use",
            "menu:org-management:use",
            "menu:permission-management:use",
            "menu:parameter:use",
            "menu:auth-provider:use",
        ]:
            assert await svc.has_menu_permission(user, perm) is False, f"Should lack {perm}"

    @pytest.mark.asyncio
    async def test_seed_user_with_regular_role_has_basic_menus(self, db_session: AsyncSession) -> None:
        svc = PermissionService(db_session)
        user = TokenUser(user_id=_SEED_REGULAR_USER_ID, oid=1, language="zh-CN")
        for perm in [
            "menu:workbranch:use",
            "menu:panel:use",
            "menu:screen:use",
            "menu:dataset:use",
            "menu:data-filing:use",
        ]:
            assert await svc.has_menu_permission(user, perm) is True, f"Should have {perm}"

    @pytest.mark.asyncio
    async def test_seed_user_with_regular_role_lacks_datasource(self, db_session: AsyncSession) -> None:
        svc = PermissionService(db_session)
        user = TokenUser(user_id=_SEED_REGULAR_USER_ID, oid=1, language="zh-CN")
        assert await svc.has_menu_permission(user, "menu:datasource:use") is False
        assert await svc.has_menu_permission(user, "resource:datasource:use") is False


# ---------------------------------------------------------------------------
# Dependency factory tests
# ---------------------------------------------------------------------------


class TestDependencyFactory:
    """Test that the dependency factory creates correctly named guards."""

    def test_factory_creates_callable(self) -> None:
        guard = require_menu_permission("menu:role-management:use")
        assert callable(guard)
        assert "role_management" in guard.__name__

    def test_factory_creates_unique_names(self) -> None:
        g1 = require_menu_permission("menu:role-management:use")
        g2 = require_menu_permission("menu:user-management:use")
        assert g1.__name__ != g2.__name__
