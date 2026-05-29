"""add core_resource_acl table

Revision ID: o2p3q4r5s6t7
Revises: n1o2p3q4r5s6
Create Date: 2026-05-29 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "o2p3q4r5s6t7"
down_revision = "n1o2p3q4r5s6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "core_resource_acl",
        sa.Column("id", sa.BigInteger(), autoincrement=False, nullable=False),
        sa.Column("target_type", sa.String(20), nullable=False, comment="role/user/org"),
        sa.Column("target_id", sa.BigInteger(), nullable=False, comment="Role ID, User ID, or Org ID"),
        sa.Column("resource_type", sa.String(45), nullable=False, comment="dashboard/screen/dataset/datasource"),
        sa.Column("resource_id", sa.BigInteger(), nullable=False, comment="Specific resource ID"),
        sa.Column("weight", sa.Integer(), nullable=False, server_default=sa.text("1"), comment="1=read, 2=use, 4=export, 7=manage, 9=authorize"),
        sa.Column("ext", sa.Integer(), nullable=False, server_default=sa.text("0"), comment="Extended permission weight"),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.Column("update_time", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_core_resource_acl")),
    )

    op.create_index(
        "ix_core_resource_acl_lookup",
        "core_resource_acl",
        ["target_type", "target_id", "resource_type"],
    )


def downgrade() -> None:
    op.drop_index("ix_core_resource_acl_lookup", table_name="core_resource_acl")
    op.drop_table("core_resource_acl")
