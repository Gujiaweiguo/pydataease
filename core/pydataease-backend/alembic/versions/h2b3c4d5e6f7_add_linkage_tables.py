"""add visualization linkage tables

Revision ID: h2b3c4d5e6f7
Revises: g1a2b3c4d5e6
Create Date: 2026-05-16 14:00:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "h2b3c4d5e6f7"
down_revision = "g1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- visualization_linkage ---
    op.create_table(
        "visualization_linkage",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column("dv_id", sa.BigInteger(), nullable=True),
        sa.Column("source_view_id", sa.BigInteger(), nullable=True),
        sa.Column("target_view_id", sa.BigInteger(), nullable=True),
        sa.Column("update_time", sa.BigInteger(), nullable=True),
        sa.Column("update_people", sa.String(255), nullable=True),
        sa.Column("linkage_active", sa.Boolean(), nullable=True),
        sa.Column("ext1", sa.String(255), nullable=True),
        sa.Column("ext2", sa.String(255), nullable=True),
        sa.Column("copy_from", sa.BigInteger(), nullable=True),
        sa.Column("copy_id", sa.BigInteger(), nullable=True),
    )

    op.create_index(
        "ix_visualization_linkage_dv_source",
        "visualization_linkage",
        ["dv_id", "source_view_id"],
    )

    # --- visualization_linkage_field ---
    op.create_table(
        "visualization_linkage_field",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column("linkage_id", sa.BigInteger(), nullable=True),
        sa.Column("source_field", sa.BigInteger(), nullable=True),
        sa.Column("target_field", sa.BigInteger(), nullable=True),
        sa.Column("update_time", sa.BigInteger(), nullable=True),
        sa.Column("copy_from", sa.BigInteger(), nullable=True),
        sa.Column("copy_id", sa.BigInteger(), nullable=True),
    )

    op.create_index(
        "ix_visualization_linkage_field_linkage_id",
        "visualization_linkage_field",
        ["linkage_id"],
    )

    # --- snapshot_visualization_linkage ---
    op.create_table(
        "snapshot_visualization_linkage",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column("dv_id", sa.BigInteger(), nullable=True),
        sa.Column("source_view_id", sa.BigInteger(), nullable=True),
        sa.Column("target_view_id", sa.BigInteger(), nullable=True),
        sa.Column("update_time", sa.BigInteger(), nullable=True),
        sa.Column("update_people", sa.String(255), nullable=True),
        sa.Column("linkage_active", sa.Boolean(), nullable=True),
        sa.Column("ext1", sa.String(255), nullable=True),
        sa.Column("ext2", sa.String(255), nullable=True),
        sa.Column("copy_from", sa.BigInteger(), nullable=True),
        sa.Column("copy_id", sa.BigInteger(), nullable=True),
    )

    op.create_index(
        "ix_snapshot_visualization_linkage_dv_source",
        "snapshot_visualization_linkage",
        ["dv_id", "source_view_id"],
    )

    # --- snapshot_visualization_linkage_field ---
    op.create_table(
        "snapshot_visualization_linkage_field",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=False),
        sa.Column("linkage_id", sa.BigInteger(), nullable=True),
        sa.Column("source_field", sa.BigInteger(), nullable=True),
        sa.Column("target_field", sa.BigInteger(), nullable=True),
        sa.Column("update_time", sa.BigInteger(), nullable=True),
        sa.Column("copy_from", sa.BigInteger(), nullable=True),
        sa.Column("copy_id", sa.BigInteger(), nullable=True),
    )

    op.create_index(
        "ix_snapshot_visualization_linkage_field_linkage_id",
        "snapshot_visualization_linkage_field",
        ["linkage_id"],
    )


def downgrade() -> None:
    op.drop_table("snapshot_visualization_linkage_field")
    op.drop_table("snapshot_visualization_linkage")
    op.drop_table("visualization_linkage_field")
    op.drop_table("visualization_linkage")
