"""add core role tables

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-05-15 00:00:00.000000
"""

from __future__ import annotations

import time

from alembic import op
import sqlalchemy as sa


revision = "f2a3b4c5d6e7"
down_revision = "e1f2a3b4c5d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "core_role",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.Column("type", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.Column("update_time", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_core_role")),
    )

    op.create_table(
        "core_role_user",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("role_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("oid", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["core_role.id"], name=op.f("fk_core_role_user_role_id_core_role")),
        sa.ForeignKeyConstraint(["user_id"], ["core_user.id"], name=op.f("fk_core_role_user_user_id_core_user")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_core_role_user")),
        sa.UniqueConstraint("role_id", "user_id", "oid", name="uq_core_role_user_binding"),
    )

    timestamp = int(time.time_ns())
    op.execute(
        sa.text(
            """
            INSERT INTO core_role (id, name, description, oid, type, create_time, update_time)
            VALUES
                (1, '系统管理员', 'System administrator with full access', 0, 0, :timestamp, :timestamp),
                (2, '组织管理员', 'Organization administrator', 1, 0, :timestamp, :timestamp),
                (3, '普通用户', 'Default organization user', 1, 0, :timestamp, :timestamp)
            """
        ).bindparams(timestamp=timestamp)
    )
    op.execute(
        sa.text(
            """
            INSERT INTO core_role_user (id, role_id, user_id, oid)
            VALUES (1001, 1, 1, 0)
            """
        )
    )

    op.alter_column("core_role", "type", server_default=None)


def downgrade() -> None:
    op.drop_table("core_role_user")
    op.drop_table("core_role")
