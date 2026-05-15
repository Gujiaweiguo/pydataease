"""add core org tables

Revision ID: e1f2a3b4c5d6
Revises: d5e6f7a8b9c0
Create Date: 2026-05-15 00:00:00.000000
"""

from __future__ import annotations

import time

from alembic import op
import sqlalchemy as sa


revision = "e1f2a3b4c5d6"
down_revision = "d5e6f7a8b9c0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "core_org",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("pid", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.Column("update_time", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_core_org")),
    )

    op.create_table(
        "core_user_org",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("org_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["core_org.id"], name=op.f("fk_core_user_org_org_id_core_org")),
        sa.ForeignKeyConstraint(["user_id"], ["core_user.id"], name=op.f("fk_core_user_org_user_id_core_user")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_core_user_org")),
        sa.UniqueConstraint("user_id", "org_id", name="uq_core_user_org_user_org"),
    )

    create_time = int(time.time_ns())
    update_time = int(time.time_ns())
    membership_id = int(time.time_ns())
    op.execute(
        f"INSERT INTO core_org (id, pid, name, create_time, update_time) "
        f"VALUES (1, 0, '默认组织', {create_time}, {update_time})"
    )
    op.execute(
        f"INSERT INTO core_user_org (id, user_id, org_id) "
        f"VALUES ({membership_id}, 1, 1)"
    )


def downgrade() -> None:
    op.drop_table("core_user_org")
    op.drop_table("core_org")
