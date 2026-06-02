"""restructure admin menus into org-mgmt and sys-mgmt groups

Split the flat children of sys-setting (id=15) into two logical groups:
- 组织管理 (org-mgmt-group): org-management, user-management, role-management, permission-management
- 系统管理 (sys-mgmt-group): parameter, auth-provider, data-filing, watermark, sys-variable

The gear icon still navigates to /sys-setting. The left sidebar now shows
two sub-groups instead of a flat list.

Revision ID: g0h1i2j3k4l5
Revises: f1a2b3c4d5e7
Create Date: 2026-06-02 10:30:00.000000

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "g0h1i2j3k4l5"
down_revision = "f1a2b3c4d5e7"
branch_labels = None
depends_on = None

_ORG_GROUP_ID = 1790000000000000001
_SYS_GROUP_ID = 1790000000000000002


def upgrade() -> None:
    bind = op.get_bind()

    # Idempotency: check if groups already exist
    existing = bind.execute(
        sa.text("SELECT id FROM core_menu WHERE name IN ('org-mgmt-group', 'sys-mgmt-group')")
    ).fetchall()
    if existing:
        return

    bind.execute(
        sa.text(
            "INSERT INTO core_menu (id, pid, type, name, component, menu_sort, icon, path, hidden, in_layout, auth) "
            "VALUES (:id, :pid, :type, :name, :component, :sort, :icon, :path, :hidden, :in_layout, :auth)"
        ),
        [
            {
                "id": _ORG_GROUP_ID,
                "pid": 15,
                "type": 1,
                "name": "org-mgmt-group",
                "component": None,
                "sort": 1,
                "icon": None,
                "path": "org-mgmt-group",
                "hidden": False,
                "in_layout": False,
                "auth": False,
            },
            {
                "id": _SYS_GROUP_ID,
                "pid": 15,
                "type": 1,
                "name": "sys-mgmt-group",
                "component": None,
                "sort": 2,
                "icon": None,
                "path": "sys-mgmt-group",
                "hidden": False,
                "in_layout": False,
                "auth": False,
            },
        ],
    )

    bind.execute(
        sa.text(
            "UPDATE core_menu SET pid = :new_pid, menu_sort = :sort "
            "WHERE name = :name AND pid = 15"
        ),
        [
            {"new_pid": _ORG_GROUP_ID, "sort": 1, "name": "org-management"},
            {"new_pid": _ORG_GROUP_ID, "sort": 2, "name": "user-management"},
            {"new_pid": _ORG_GROUP_ID, "sort": 3, "name": "role-management"},
            {"new_pid": _ORG_GROUP_ID, "sort": 4, "name": "permission-management"},
            {"new_pid": _SYS_GROUP_ID, "sort": 1, "name": "parameter"},
            {"new_pid": _SYS_GROUP_ID, "sort": 2, "name": "auth-provider"},
            {"new_pid": 4, "sort": 3, "name": "data-filing"},
            {"new_pid": _SYS_GROUP_ID, "sort": 3, "name": "watermark"},
            {"new_pid": _SYS_GROUP_ID, "sort": 5, "name": "sys-variable"},
        ],
    )

    bind.execute(
        sa.text(
            f"SELECT setval('core_menu_id_seq', GREATEST((SELECT COALESCE(MAX(id), 0) FROM core_menu) + 1, {_SYS_GROUP_ID} + 1))"
        )
    )


def downgrade() -> None:
    bind = op.get_bind()

    group_children = bind.execute(
        sa.text("SELECT id FROM core_menu WHERE pid IN (:org, :sys)"),
        {"org": _ORG_GROUP_ID, "sys": _SYS_GROUP_ID},
    ).fetchall()
    child_ids = [row[0] for row in group_children]

    if child_ids:
        bind.execute(
            sa.text("UPDATE core_menu SET pid = 15 WHERE id = ANY(:ids)"),
            {"ids": child_ids},
        )

    bind.execute(
        sa.text("DELETE FROM core_menu WHERE id IN (:org, :sys)"),
        {"org": _ORG_GROUP_ID, "sys": _SYS_GROUP_ID},
    )
