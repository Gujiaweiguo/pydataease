"""seed admin console menu foundation

Revision ID: n1o2p3q4r5s6
Revises: m7n8o9p0q1r2
Create Date: 2026-05-28 00:00:00.000000

"""

from __future__ import annotations

import time

from alembic import op
import sqlalchemy as sa


revision = "n1o2p3q4r5s6"
down_revision = "m7n8o9p0q1r2"
branch_labels = None
depends_on = None

_CREATE_TIME = 1779900000000
_ADMIN_ROLE_ID = 1
_ADMIN_GRANT_OID = 0
_ADMIN_MENUS: list[tuple[str, int, int, str, int, str, str, bool, bool, bool, str, str]] = [
    ("org-management", 15, 2, "system/org", 2, "sys-org", "/org-management", False, True, True, "use", "menu:org-management:use"),
    ("user-management", 15, 2, "system/user", 3, "sys-user", "/user-management", False, True, True, "use", "menu:user-management:use"),
    ("role-management", 15, 2, "system/role", 4, "sys-role", "/role-management", False, True, True, "use", "menu:role-management:use"),
    ("permission-management", 15, 2, "system/permission", 5, "sys-auth", "/permission-management", False, True, True, "use", "menu:permission-management:use"),
]


def _next_bigint(bind: sa.Connection, table_name: str, floor: int | None = None) -> int:
    current = bind.execute(sa.text(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}")).scalar_one()
    base = max(int(current), floor or 0)
    generated = time.time_ns()
    return generated if generated > base else base + 1


def upgrade() -> None:
    bind = op.get_bind()
    menu_table = sa.table(
        "core_menu",
        sa.column("id", sa.BigInteger()),
        sa.column("pid", sa.BigInteger()),
        sa.column("type", sa.Integer()),
        sa.column("name", sa.String(length=45)),
        sa.column("component", sa.String(length=45)),
        sa.column("menu_sort", sa.Integer()),
        sa.column("icon", sa.String(length=45)),
        sa.column("path", sa.String(length=45)),
        sa.column("hidden", sa.Boolean()),
        sa.column("in_layout", sa.Boolean()),
        sa.column("auth", sa.Boolean()),
    )
    point_table = sa.table(
        "core_permission_point",
        sa.column("id", sa.BigInteger()),
        sa.column("menu_id", sa.BigInteger()),
        sa.column("resource_type", sa.String(length=45)),
        sa.column("permission_type", sa.String(length=20)),
        sa.column("name", sa.String(length=100)),
        sa.column("create_time", sa.BigInteger()),
    )
    role_permission_table = sa.table(
        "core_role_permission",
        sa.column("id", sa.BigInteger()),
        sa.column("role_id", sa.BigInteger()),
        sa.column("permission_point_id", sa.BigInteger()),
        sa.column("oid", sa.BigInteger()),
        sa.column("granted", sa.Boolean()),
        sa.column("create_time", sa.BigInteger()),
    )

    inserted_menu_names: list[str] = []

    for (
        menu_name,
        pid,
        menu_type,
        component,
        menu_sort,
        icon,
        path,
        hidden,
        in_layout,
        auth,
        permission_type,
        permission_name,
    ) in _ADMIN_MENUS:
        existing_menu_id = bind.execute(
            sa.text("SELECT id FROM core_menu WHERE name = :name LIMIT 1"),
            {"name": menu_name},
        ).scalar_one_or_none()

        if existing_menu_id is None:
            menu_id = _next_bigint(bind, "core_menu", floor=16)
            op.bulk_insert(
                menu_table,
                [
                    {
                        "id": menu_id,
                        "pid": pid,
                        "type": menu_type,
                        "name": menu_name,
                        "component": component,
                        "menu_sort": menu_sort,
                        "icon": icon,
                        "path": path,
                        "hidden": hidden,
                        "in_layout": in_layout,
                        "auth": auth,
                    }
                ],
            )
            inserted_menu_names.append(menu_name)
        else:
            menu_id = int(existing_menu_id)

        existing_point_id = bind.execute(
            sa.text("SELECT id FROM core_permission_point WHERE name = :name LIMIT 1"),
            {"name": permission_name},
        ).scalar_one_or_none()

        if existing_point_id is None:
            point_id = _next_bigint(bind, "core_permission_point", floor=10009)
            op.bulk_insert(
                point_table,
                [
                    {
                        "id": point_id,
                        "menu_id": menu_id,
                        "resource_type": None,
                        "permission_type": permission_type,
                        "name": permission_name,
                        "create_time": _CREATE_TIME,
                    }
                ],
            )
        else:
            point_id = int(existing_point_id)

        existing_role_grant = bind.execute(
            sa.text(
                """
                SELECT id
                FROM core_role_permission
                WHERE role_id = :role_id AND permission_point_id = :permission_point_id AND oid = :oid
                LIMIT 1
                """
            ),
            {
                "role_id": _ADMIN_ROLE_ID,
                "permission_point_id": point_id,
                "oid": _ADMIN_GRANT_OID,
            },
        ).scalar_one_or_none()
        if existing_role_grant is None:
            role_permission_id = _next_bigint(bind, "core_role_permission", floor=20009)
            op.bulk_insert(
                role_permission_table,
                [
                    {
                        "id": role_permission_id,
                        "role_id": _ADMIN_ROLE_ID,
                        "permission_point_id": point_id,
                        "oid": _ADMIN_GRANT_OID,
                        "granted": True,
                        "create_time": _CREATE_TIME,
                    }
                ],
            )

    if inserted_menu_names:
        bind.execute(
            sa.text(
                "UPDATE core_menu SET hidden = false WHERE name IN ('org-management', 'user-management', 'role-management', 'permission-management')"
            )
        )


def downgrade() -> None:
    bind = op.get_bind()
    permission_names = [menu[11] for menu in _ADMIN_MENUS]
    menu_names = [menu[0] for menu in _ADMIN_MENUS]

    point_rows = bind.execute(
        sa.text("SELECT id FROM core_permission_point WHERE name = ANY(:names)"),
        {"names": permission_names},
    ).all()
    point_ids = [int(row[0]) for row in point_rows]

    if point_ids:
        bind.execute(
            sa.text("DELETE FROM core_role_permission WHERE permission_point_id = ANY(:point_ids)"),
            {"point_ids": point_ids},
        )
        bind.execute(
            sa.text("DELETE FROM core_user_permission WHERE permission_point_id = ANY(:point_ids)"),
            {"point_ids": point_ids},
        )
        bind.execute(
            sa.text("DELETE FROM core_org_permission WHERE permission_point_id = ANY(:point_ids)"),
            {"point_ids": point_ids},
        )
        bind.execute(
            sa.text("DELETE FROM core_permission_point WHERE id = ANY(:point_ids)"),
            {"point_ids": point_ids},
        )

    bind.execute(sa.text("DELETE FROM core_menu WHERE name = ANY(:names)"), {"names": menu_names})
