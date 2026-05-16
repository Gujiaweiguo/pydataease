"""add outer params tables

Revision ID: g1a2b3c4d5e6
Revises: f1a2b3c4d5e6
Create Date: 2026-05-16 12:00:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "g1a2b3c4d5e6"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- visualization_outer_params ---
    op.create_table(
        "visualization_outer_params",
        sa.Column("params_id", sa.String(50), nullable=False),
        sa.Column("visualization_id", sa.String(50), nullable=True),
        sa.Column("checked", sa.Boolean(), nullable=True),
        sa.Column("remark", sa.String(255), nullable=True),
        sa.Column("copy_from", sa.String(50), nullable=True),
        sa.Column("copy_id", sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint("params_id", name=op.f("pk_visualization_outer_params")),
    )

    # --- visualization_outer_params_info ---
    op.create_table(
        "visualization_outer_params_info",
        sa.Column("params_info_id", sa.String(50), nullable=False),
        sa.Column("params_id", sa.String(50), nullable=True),
        sa.Column("param_name", sa.String(255), nullable=True),
        sa.Column("checked", sa.Boolean(), nullable=True),
        sa.Column("required", sa.Boolean(), nullable=True),
        sa.Column("default_value", sa.String(2048), nullable=True),
        sa.Column("enabled_default", sa.Boolean(), nullable=True),
        sa.Column("copy_from", sa.String(50), nullable=True),
        sa.Column("copy_id", sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint(
            "params_info_id", name=op.f("pk_visualization_outer_params_info")
        ),
    )

    # --- visualization_outer_params_target_view_info ---
    op.create_table(
        "visualization_outer_params_target_view_info",
        sa.Column("target_id", sa.String(50), nullable=False),
        sa.Column("params_info_id", sa.String(50), nullable=True),
        sa.Column("target_view_id", sa.String(50), nullable=True),
        sa.Column("target_ds_id", sa.String(50), nullable=True),
        sa.Column("target_field_id", sa.String(50), nullable=True),
        sa.Column("copy_from", sa.String(50), nullable=True),
        sa.Column("copy_id", sa.String(50), nullable=True),
        sa.Column("match_mode", sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint(
            "target_id",
            name=op.f("pk_visualization_outer_params_target_view_info"),
        ),
    )

    # --- snapshot_visualization_outer_params ---
    op.create_table(
        "snapshot_visualization_outer_params",
        sa.Column("params_id", sa.String(50), nullable=False),
        sa.Column("visualization_id", sa.String(50), nullable=True),
        sa.Column("checked", sa.Boolean(), nullable=True),
        sa.Column("remark", sa.String(255), nullable=True),
        sa.Column("copy_from", sa.String(50), nullable=True),
        sa.Column("copy_id", sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint(
            "params_id", name=op.f("pk_snapshot_visualization_outer_params")
        ),
    )

    # --- snapshot_visualization_outer_params_info ---
    op.create_table(
        "snapshot_visualization_outer_params_info",
        sa.Column("params_info_id", sa.String(50), nullable=False),
        sa.Column("params_id", sa.String(50), nullable=True),
        sa.Column("param_name", sa.String(255), nullable=True),
        sa.Column("checked", sa.Boolean(), nullable=True),
        sa.Column("required", sa.Boolean(), nullable=True),
        sa.Column("default_value", sa.String(2048), nullable=True),
        sa.Column("enabled_default", sa.Boolean(), nullable=True),
        sa.Column("copy_from", sa.String(50), nullable=True),
        sa.Column("copy_id", sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint(
            "params_info_id", name=op.f("pk_snapshot_visualization_outer_params_info")
        ),
    )

    # --- snapshot_visualization_outer_params_target_view_info ---
    op.create_table(
        "snapshot_visualization_outer_params_target_view_info",
        sa.Column("target_id", sa.String(50), nullable=False),
        sa.Column("params_info_id", sa.String(50), nullable=True),
        sa.Column("target_view_id", sa.String(50), nullable=True),
        sa.Column("target_ds_id", sa.String(50), nullable=True),
        sa.Column("target_field_id", sa.String(50), nullable=True),
        sa.Column("copy_from", sa.String(50), nullable=True),
        sa.Column("copy_id", sa.String(50), nullable=True),
        sa.Column("match_mode", sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint(
            "target_id",
            name=op.f("pk_snapshot_visualization_outer_params_target_view_info"),
        ),
    )


def downgrade() -> None:
    op.drop_table("snapshot_visualization_outer_params_target_view_info")
    op.drop_table("snapshot_visualization_outer_params_info")
    op.drop_table("snapshot_visualization_outer_params")
    op.drop_table("visualization_outer_params_target_view_info")
    op.drop_table("visualization_outer_params_info")
    op.drop_table("visualization_outer_params")
