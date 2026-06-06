"""Tests for the r5s6t7u8v9w0 seed_builtin_role_permissions migration.

Verifies that:
  - Each built-in role has exactly the expected number of permission grants.
  - The migration is idempotent: re-running upgrade after downgrade produces
    identical results with no duplicate rows.

Requires a running PostgreSQL (db_session fixture from db_fixtures.py).
"""

from __future__ import annotations

import pytest
from sqlalchemy import func, select, text

from app.models.role_permission import CoreRolePermission  # pyright: ignore[reportImplicitRelativeImport]

# ---------------------------------------------------------------------------
# Expected permission counts per role (from the permission template).
# ---------------------------------------------------------------------------

_EXPECTED: dict[int, tuple[int, int]] = {
    # role_id: (oid, expected_permission_count)
    1: (0, 18),  # 系统管理员 — all 14 menu + 4 resource points
    2: (1, 14),  # 组织管理员 — 10 menu + 4 resource (no system-level settings)
    3: (1, 8),   # 普通用户   — 5 menu + 3 resource (no datasource menu/resource)
}

# Permission-point names that MUST be present for each role.
_ROLE_PERM_NAMES: dict[int, set[str]] = {
    2: {
        "menu:workbranch:use",
        "menu:panel:use",
        "menu:screen:use",
        "menu:dataset:use",
        "menu:datasource:use",
        "menu:data-filing:use",
        "menu:org-management:use",
        "menu:user-management:use",
        "menu:role-management:use",
        "menu:permission-management:use",
        "resource:dashboard:use",
        "resource:screen:use",
        "resource:dataset:use",
        "resource:datasource:use",
    },
    3: {
        "menu:workbranch:use",
        "menu:panel:use",
        "menu:screen:use",
        "menu:dataset:use",
        "menu:data-filing:use",
        "resource:dashboard:use",
        "resource:screen:use",
        "resource:dataset:use",
    },
}

# Names that MUST NOT appear for each role.
_FORBIDDEN_PERM_NAMES: dict[int, set[str]] = {
    2: {
        "menu:auth-provider:use",
        "menu:parameter:use",
        "menu:watermark:use",
        "menu:sys-variable:use",
    },
    3: {
        "menu:datasource:use",
        "resource:datasource:use",
        "menu:org-management:use",
        "menu:user-management:use",
        "menu:role-management:use",
        "menu:permission-management:use",
        "menu:auth-provider:use",
        "menu:parameter:use",
        "menu:watermark:use",
        "menu:sys-variable:use",
    },
}


async def _count_role_permissions(session, role_id: int, oid: int) -> int:
    result = await session.execute(
        select(func.count()).select_from(CoreRolePermission).where(
            CoreRolePermission.role_id == role_id,
            CoreRolePermission.oid == oid,
        )
    )
    return int(result.scalar_one())


async def _get_perm_names_for_role(session, role_id: int, oid: int) -> set[str]:
    rows = await session.execute(
        text(
            "SELECT pp.name FROM core_role_permission rp "
            "JOIN core_permission_point pp ON rp.permission_point_id = pp.id "
            "WHERE rp.role_id = :rid AND rp.oid = :oid"
        ),
        {"rid": role_id, "oid": oid},
    )
    return {str(r[0]) for r in rows.fetchall()}


@pytest.mark.asyncio
async def test_builtin_roles_have_expected_permission_counts(db_session) -> None:
    """Verify each built-in role has exactly the expected number of permission rows."""
    for role_id, (oid, expected_count) in _EXPECTED.items():
        actual = await _count_role_permissions(db_session, role_id, oid)
        assert actual == expected_count, (
            f"role_id={role_id} (oid={oid}): expected {expected_count} permissions, got {actual}"
        )


@pytest.mark.asyncio
async def test_org_admin_has_correct_permission_names(db_session) -> None:
    """Verify org-admin role has exactly the right permission-point names."""
    actual = await _get_perm_names_for_role(db_session, 2, 1)
    assert actual == _ROLE_PERM_NAMES[2]


@pytest.mark.asyncio
async def test_regular_user_has_correct_permission_names(db_session) -> None:
    """Verify regular-user role has exactly the right permission-point names."""
    actual = await _get_perm_names_for_role(db_session, 3, 1)
    assert actual == _ROLE_PERM_NAMES[3]


@pytest.mark.asyncio
async def test_no_forbidden_permissions_granted(db_session) -> None:
    """Verify forbidden permission names are absent for each role."""
    for role_id, forbidden in _FORBIDDEN_PERM_NAMES.items():
        actual = await _get_perm_names_for_role(db_session, role_id, 1)
        violations = actual & forbidden
        assert not violations, (
            f"role_id={role_id} has forbidden permissions: {violations}"
        )


@pytest.mark.asyncio
async def test_migration_is_idempotent(db_session) -> None:
    """Downgrade → upgrade should produce the same permission counts, no duplicates.

    We snapshot permissions, run downgrade+upgrade, and verify counts match.
    """
    # Snapshot before
    before_counts: dict[int, int] = {}
    for role_id, (oid, _) in _EXPECTED.items():
        before_counts[role_id] = await _count_role_permissions(db_session, role_id, oid)

    # Run downgrade then upgrade
    import subprocess
    result = subprocess.run(
        ["uv", "run", "alembic", "downgrade", "q4r5s6t7u8v9"],
        capture_output=True, text=True,
        cwd=__file__.rsplit("/", 1)[0].rsplit("/", 1)[0],  # project root
    )
    assert result.returncode == 0, f"Downgrade failed: {result.stderr[:500]}"

    result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        capture_output=True, text=True,
        cwd=__file__.rsplit("/", 1)[0].rsplit("/", 1)[0],
    )
    assert result.returncode == 0, f"Upgrade failed: {result.stderr[:500]}"

    # Verify counts match exactly
    for role_id, (oid, _) in _EXPECTED.items():
        after = await _count_role_permissions(db_session, role_id, oid)
        assert after == before_counts[role_id], (
            f"role_id={role_id}: count changed after downgrade+upgrade "
            f"({before_counts[role_id]} → {after})"
        )
