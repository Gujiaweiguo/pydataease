"""seed builtin role permissions for org-admin and regular-user

Grant menu and resource permissions to the three built-in roles according to
the standard permission template:

  系统管理员 (role_id=1, oid=0) — already granted in prior migrations; no changes.
  组织管理员 (role_id=2, oid=1) — all menu/resource permissions except system-level settings.
  普通用户   (role_id=3, oid=1) — basic BI usage only (no datasource, no admin menus).

This migration is idempotent: existing grants are left untouched, missing grants
are inserted, and stale grants that contradict the template are removed.

Revision ID: r5s6t7u8v9w0
Revises: q4r5s6t7u8v9
Create Date: 2026-06-06 00:00:00.000000

"""

from __future__ import annotations

import time

from alembic import op
import sqlalchemy as sa


revision = "r5s6t7u8v9w0"
down_revision = "q4r5s6t7u8v9"
branch_labels = None
depends_on = None

_CREATE_TIME = int(time.time_ns())

# ---------------------------------------------------------------------------
# Permission template
# ---------------------------------------------------------------------------
# Maps (role_id, oid) → list of permission-point names to grant.
# Any role_permission row for that role whose permission_point is NOT in this
# list will be removed (stale cleanup).
# ---------------------------------------------------------------------------

_ORG_ADMIN_PERMS: list[str] = [
    # Menu permissions
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
    # Resource permissions
    "resource:dashboard:use",
    "resource:screen:use",
    "resource:dataset:use",
    "resource:datasource:use",
]

_REGULAR_USER_PERMS: list[str] = [
    # Menu permissions
    "menu:workbranch:use",
    "menu:panel:use",
    "menu:screen:use",
    "menu:dataset:use",
    "menu:data-filing:use",
    # Resource permissions
    "resource:dashboard:use",
    "resource:screen:use",
    "resource:dataset:use",
]

_TEMPLATE: list[tuple[int, int, list[str]]] = [
    (2, 1, _ORG_ADMIN_PERMS),
    (3, 1, _REGULAR_USER_PERMS),
]


def upgrade() -> None:
    bind = op.get_bind()

    for role_id, oid, perm_names in _TEMPLATE:
        # Resolve permission point names → ids
        rows = bind.execute(
            sa.text("SELECT id, name FROM core_permission_point WHERE name = ANY(:names)"),
            {"names": perm_names},
        ).fetchall()
        name_to_id: dict[str, int] = {str(r[1]): int(r[0]) for r in rows}

        # Validate all names resolved
        missing = set(perm_names) - set(name_to_id)
        if missing:
            raise RuntimeError(f"Permission points not found for role_id={role_id}: {missing}")

        # --- Remove stale grants (permission points NOT in template for this role) ---
        valid_point_ids = list(name_to_id.values())
        bind.execute(
            sa.text(
                "DELETE FROM core_role_permission "
                "WHERE role_id = :role_id AND oid = :oid "
                "AND permission_point_id != ALL(:valid_ids)"
            ),
            {"role_id": role_id, "oid": oid, "valid_ids": valid_point_ids},
        )

        # --- Insert missing grants ---
        for perm_name in perm_names:
            point_id = name_to_id[perm_name]
            exists = bind.execute(
                sa.text(
                    "SELECT 1 FROM core_role_permission "
                    "WHERE role_id = :role_id AND permission_point_id = :pp_id AND oid = :oid "
                    "LIMIT 1"
                ),
                {"role_id": role_id, "pp_id": point_id, "oid": oid},
            ).scalar_one_or_none()

            if exists is None:
                bind.execute(
                    sa.text(
                        "INSERT INTO core_role_permission (id, role_id, permission_point_id, oid, granted, create_time) "
                        "VALUES (:id, :role_id, :pp_id, :oid, TRUE, :ct)"
                    ),
                    {
                        "id": time.time_ns(),
                        "role_id": role_id,
                        "pp_id": point_id,
                        "oid": oid,
                        "ct": _CREATE_TIME,
                    },
                )


def downgrade() -> None:
    bind = op.get_bind()

    for role_id, oid, perm_names in _TEMPLATE:
        rows = bind.execute(
            sa.text("SELECT id FROM core_permission_point WHERE name = ANY(:names)"),
            {"names": perm_names},
        ).fetchall()
        point_ids = [int(r[0]) for r in rows]

        if point_ids:
            bind.execute(
                sa.text(
                    "DELETE FROM core_role_permission "
                    "WHERE role_id = :role_id AND oid = :oid "
                    "AND permission_point_id = ANY(:point_ids)"
                ),
                {"role_id": role_id, "oid": oid, "point_ids": point_ids},
            )
