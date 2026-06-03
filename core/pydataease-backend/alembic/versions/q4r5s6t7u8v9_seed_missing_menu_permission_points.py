"""seed missing menu permission points

Revision ID: q4r5s6t7u8v9
Revises: g0h1i2j3k4l5
Create Date: 2026-06-03 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "q4r5s6t7u8v9"
down_revision = "g0h1i2j3k4l5"
branch_labels = None
depends_on = None

_CREATE_TIME = 1778830000000


def upgrade() -> None:
    """Add permission points for menus that were created after the initial seed."""
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
        [
            {
                "id": 10010,
                "menu_id": 1780136996351725192,
                "resource_type": None,
                "permission_type": "use",
                "name": "menu:data-filing:use",
                "create_time": _CREATE_TIME,
            },
            {
                "id": 10011,
                "menu_id": 1780136996351725191,
                "resource_type": None,
                "permission_type": "use",
                "name": "menu:auth-provider:use",
                "create_time": _CREATE_TIME,
            },
            {
                "id": 10012,
                "menu_id": 1780136996351725193,
                "resource_type": None,
                "permission_type": "use",
                "name": "menu:watermark:use",
                "create_time": _CREATE_TIME,
            },
        ],
    )

    # Grant these new points to system-admin role (role_id=1)
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
        [
            {"id": 20010, "role_id": 1, "permission_point_id": 10010, "oid": 0, "granted": True, "create_time": _CREATE_TIME},
            {"id": 20011, "role_id": 1, "permission_point_id": 10011, "oid": 0, "granted": True, "create_time": _CREATE_TIME},
            {"id": 20012, "role_id": 1, "permission_point_id": 10012, "oid": 0, "granted": True, "create_time": _CREATE_TIME},
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM core_role_permission WHERE id IN (20010, 20011, 20012)")
    op.execute("DELETE FROM core_permission_point WHERE id IN (10010, 10011, 10012)")
