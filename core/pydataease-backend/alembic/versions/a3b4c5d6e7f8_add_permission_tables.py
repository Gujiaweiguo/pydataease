"""add permission tables

Revision ID: a3b4c5d6e7f8
Revises: f2a3b4c5d6e7
Create Date: 2026-05-15 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "a3b4c5d6e7f8"
down_revision = "f2a3b4c5d6e7"
branch_labels = None
depends_on = None

# Deterministic timestamps and IDs
_CREATE_TIME = 1778830000000
_PP_ID_START = 10001
_RP_ID_START = 20001

# Menu permission points: menus with auth=True
_MENU_POINTS = [
    {"menu_id": 1, "resource_type": None, "permission_type": "use", "name": "menu:workbranch:use"},
    {"menu_id": 2, "resource_type": None, "permission_type": "use", "name": "menu:panel:use"},
    {"menu_id": 3, "resource_type": None, "permission_type": "use", "name": "menu:screen:use"},
    {"menu_id": 5, "resource_type": None, "permission_type": "use", "name": "menu:dataset:use"},
    {"menu_id": 6, "resource_type": None, "permission_type": "use", "name": "menu:datasource:use"},
]

# Resource-type permission points
_RESOURCE_POINTS = [
    {"menu_id": None, "resource_type": "dashboard", "permission_type": "use", "name": "resource:dashboard:use"},
    {"menu_id": None, "resource_type": "screen", "permission_type": "use", "name": "resource:screen:use"},
    {"menu_id": None, "resource_type": "dataset", "permission_type": "use", "name": "resource:dataset:use"},
    {"menu_id": None, "resource_type": "datasource", "permission_type": "use", "name": "resource:datasource:use"},
]


def upgrade() -> None:
    # --- Create tables ---
    op.create_table(
        "core_permission_point",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("menu_id", sa.BigInteger(), nullable=True, comment="FK to core_menu.id, NULL for resource-type points"),
        sa.Column("resource_type", sa.String(length=45), nullable=True, comment="dashboard/screen/dataset/datasource"),
        sa.Column("permission_type", sa.String(length=20), nullable=False, comment="use/manage/authorize/view/export"),
        sa.Column("name", sa.String(length=100), nullable=True, comment="Human-readable name"),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_core_permission_point")),
    )

    op.create_table(
        "core_role_permission",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("role_id", sa.BigInteger(), nullable=False),
        sa.Column("permission_point_id", sa.BigInteger(), nullable=False),
        sa.Column("oid", sa.BigInteger(), nullable=False, server_default="0", comment="Org scope, 0=global"),
        sa.Column("granted", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_core_role_permission")),
    )

    op.create_table(
        "core_user_permission",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("permission_point_id", sa.BigInteger(), nullable=False),
        sa.Column("granted", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_core_user_permission")),
    )

    op.create_table(
        "core_org_permission",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("org_id", sa.BigInteger(), nullable=False),
        sa.Column("permission_point_id", sa.BigInteger(), nullable=False),
        sa.Column("granted", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_core_org_permission")),
    )

    # --- Seed permission points ---
    all_points = _MENU_POINTS + _RESOURCE_POINTS
    point_rows = [
        {
            "id": _PP_ID_START + i,
            "menu_id": p["menu_id"],
            "resource_type": p["resource_type"],
            "permission_type": p["permission_type"],
            "name": p["name"],
            "create_time": _CREATE_TIME,
        }
        for i, p in enumerate(all_points)
    ]
    op.bulk_insert(
        sa.table(
            "core_permission_point",
            sa.column("id", sa.BigInteger()),
            sa.column("menu_id", sa.BigInteger()),
            sa.column("resource_type", sa.String()),
            sa.column("permission_type", sa.String()),
            sa.column("name", sa.String()),
            sa.column("create_time", sa.BigInteger()),
        ),
        point_rows,
    )

    # --- Grant all points to system-admin role (role_id=1) ---
    role_perm_rows = [
        {
            "id": _RP_ID_START + i,
            "role_id": 1,
            "permission_point_id": _PP_ID_START + i,
            "oid": 0,
            "granted": True,
            "create_time": _CREATE_TIME,
        }
        for i in range(len(all_points))
    ]
    op.bulk_insert(
        sa.table(
            "core_role_permission",
            sa.column("id", sa.BigInteger()),
            sa.column("role_id", sa.BigInteger()),
            sa.column("permission_point_id", sa.BigInteger()),
            sa.column("oid", sa.BigInteger()),
            sa.column("granted", sa.Boolean()),
            sa.column("create_time", sa.BigInteger()),
        ),
        role_perm_rows,
    )

    # Remove server defaults that were only needed for the insert
    op.alter_column("core_role_permission", "oid", server_default=None)
    op.alter_column("core_role_permission", "granted", server_default=None)
    op.alter_column("core_user_permission", "granted", server_default=None)
    op.alter_column("core_org_permission", "granted", server_default=None)


def downgrade() -> None:
    op.drop_table("core_org_permission")
    op.drop_table("core_user_permission")
    op.drop_table("core_role_permission")
    op.drop_table("core_permission_point")
