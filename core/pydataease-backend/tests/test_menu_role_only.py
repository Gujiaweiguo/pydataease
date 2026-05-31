# pyright: reportAttributeAccessIssue=false

"""Tests that menu visibility is determined solely by role-based grants."""

from __future__ import annotations

from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.permission_service import PermissionService  # pyright: ignore[reportImplicitRelativeImport]


class _FakeAllResult:
    """Result whose .all() returns a list of row tuples."""

    def __init__(self, rows: list[Any]) -> None:
        self._rows = rows

    def all(self) -> list[Any]:
        return list(self._rows)


class _FakeSession:
    """Minimal async session that returns pre-loaded results from execute()."""

    def __init__(self, results: list[Any]) -> None:
        self._results = list(results)

    async def execute(self, _stmt: Any) -> Any:
        return self._results.pop(0)


# ---------------------------------------------------------------------------
# 1. Menu visibility comes from role grants only
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_menu_ids_from_role_grants_only() -> None:
    """Two queries: role_ids → role_permissions. Result should be {100, 200}."""
    role_id_rows = [(10,)]  # user has role 10
    menu_rows = [(100,), (200,)]  # role 10 grants menus 100, 200
    session = _FakeSession([_FakeAllResult(role_id_rows), _FakeAllResult(menu_rows)])
    svc = PermissionService(cast(AsyncSession, cast(object, session)))

    result = await svc.get_effective_menu_ids(user_id=7, oid=1)

    assert result == {100, 200}


# ---------------------------------------------------------------------------
# 2. User-level denials do NOT remove menu visibility
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_user_level_denials_ignored() -> None:
    """Even if user-direct deny rows existed before, only role grants matter."""
    role_id_rows = [(10,)]
    menu_rows = [(300,)]
    session = _FakeSession([_FakeAllResult(role_id_rows), _FakeAllResult(menu_rows)])
    svc = PermissionService(cast(AsyncSession, cast(object, session)))

    result = await svc.get_effective_menu_ids(user_id=7, oid=1)

    # Only role-granted menus appear; no deny step removes them
    assert result == {300}


# ---------------------------------------------------------------------------
# 3. Org-level grants do NOT add menu visibility
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_org_level_grants_ignored() -> None:
    """Org-level grants are not queried — only two DB calls total."""
    role_id_rows = [(10,)]
    menu_rows = [(400,)]
    session = _FakeSession([_FakeAllResult(role_id_rows), _FakeAllResult(menu_rows)])
    svc = PermissionService(cast(AsyncSession, cast(object, session)))

    result = await svc.get_effective_menu_ids(user_id=7, oid=1)

    assert result == {400}
    # Verify only 2 execute() calls were consumed (role_ids + role_perms)
    assert len(session._results) == 0


# ---------------------------------------------------------------------------
# 4. No roles → empty menu set (admin handling is at caller level)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_no_roles_means_no_menus() -> None:
    """User with no role assignments sees no menus."""
    session = _FakeSession([_FakeAllResult([])])  # no role_ids
    svc = PermissionService(cast(AsyncSession, cast(object, session)))

    result = await svc.get_effective_menu_ids(user_id=99, oid=1)

    assert result == set()
