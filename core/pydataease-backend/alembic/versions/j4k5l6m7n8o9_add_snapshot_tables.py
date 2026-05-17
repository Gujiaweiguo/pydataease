"""add snapshot tables

Revision ID: j4k5l6m7n8o9
Revises: a2b3c4d5e6f7
Create Date: 2026-05-17 10:00:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "j4k5l6m7n8o9"
down_revision = "a2b3c4d5e6f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- snapshot_data_visualization_info ---
    op.create_table(
        "snapshot_data_visualization_info",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("pid", sa.BigInteger(), nullable=True),
        sa.Column("org_id", sa.BigInteger(), nullable=True),
        sa.Column("level", sa.Integer(), nullable=True),
        sa.Column("node_type", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("canvas_style_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("component_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("mobile_layout", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("status", sa.Integer(), nullable=True, server_default=sa.text("1")),
        sa.Column("self_watermark_status", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column("sort", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.Column("create_by", sa.String(length=255), nullable=True),
        sa.Column("update_time", sa.BigInteger(), nullable=True),
        sa.Column("update_by", sa.String(length=255), nullable=True),
        sa.Column("remark", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("delete_flag", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("delete_time", sa.BigInteger(), nullable=True),
        sa.Column("delete_by", sa.String(length=255), nullable=True),
        sa.Column("version", sa.Integer(), nullable=True, server_default=sa.text("3")),
        sa.Column("content_id", sa.String(length=50), nullable=True, server_default=sa.text("'0'")),
        sa.Column("check_version", sa.String(length=50), nullable=True, server_default=sa.text("'1'")),
        sa.ForeignKeyConstraint(["pid"], ["snapshot_data_visualization_info.id"]),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_snapshot_data_visualization_info")),
    )

    # --- snapshot_core_chart_view ---
    op.create_table(
        "snapshot_core_chart_view",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=1024), nullable=True),
        sa.Column("scene_id", sa.BigInteger(), nullable=False),
        sa.Column("table_id", sa.BigInteger(), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=True),
        sa.Column("render", sa.String(length=50), nullable=True),
        sa.Column("result_count", sa.Integer(), nullable=True),
        sa.Column("result_mode", sa.String(length=50), nullable=True),
        sa.Column("x_axis", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("x_axis_ext", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("y_axis", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("y_axis_ext", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ext_stack", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ext_bubble", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ext_label", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ext_tooltip", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("custom_attr", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("custom_style", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("custom_filter", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("drill_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("senior", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("create_by", sa.String(length=50), nullable=True),
        sa.Column("create_time", sa.BigInteger(), nullable=True),
        sa.Column("update_time", sa.BigInteger(), nullable=True),
        sa.Column("snapshot", sa.Text(), nullable=True),
        sa.Column("style_priority", sa.String(length=255), nullable=True, server_default=sa.text("'panel'")),
        sa.Column("chart_type", sa.String(length=255), nullable=True, server_default=sa.text("'private'")),
        sa.Column("is_plugin", sa.Boolean(), nullable=True),
        sa.Column("data_from", sa.String(length=255), nullable=True, server_default=sa.text("'dataset'")),
        sa.Column("view_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("refresh_view_enable", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("refresh_unit", sa.String(length=255), nullable=True, server_default=sa.text("'minute'")),
        sa.Column("refresh_time", sa.Integer(), nullable=True, server_default=sa.text("5")),
        sa.Column("linkage_active", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("jump_active", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("copy_from", sa.BigInteger(), nullable=True),
        sa.Column("copy_id", sa.BigInteger(), nullable=True),
        sa.Column("aggregate", sa.Boolean(), nullable=True),
        sa.Column("flow_map_start_name", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("flow_map_end_name", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ext_color", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("custom_attr_mobile", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("custom_style_mobile", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("sort_priority", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(["scene_id"], ["snapshot_data_visualization_info.id"]),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_snapshot_core_chart_view")),
    )

    # --- snapshot_visualization_link_jump ---
    op.create_table(
        "snapshot_visualization_link_jump",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("source_dv_id", sa.BigInteger(), nullable=True),
        sa.Column("source_view_id", sa.BigInteger(), nullable=True),
        sa.Column("link_jump_info", sa.String(255), nullable=True),
        sa.Column("checked", sa.Boolean(), nullable=True),
        sa.Column("copy_from", sa.BigInteger(), nullable=True),
        sa.Column("copy_id", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_snapshot_visualization_link_jump")),
    )

    # --- snapshot_visualization_link_jump_info ---
    op.create_table(
        "snapshot_visualization_link_jump_info",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("link_jump_id", sa.BigInteger(), nullable=True),
        sa.Column("link_type", sa.String(255), nullable=True),
        sa.Column("jump_type", sa.String(255), nullable=True),
        sa.Column("window_size", sa.String(255), nullable=True),
        sa.Column("target_dv_id", sa.BigInteger(), nullable=True),
        sa.Column("source_field_id", sa.BigInteger(), nullable=True),
        sa.Column("content", sa.String(2048), nullable=True),
        sa.Column("checked", sa.Boolean(), nullable=True),
        sa.Column("attach_params", sa.Boolean(), nullable=True),
        sa.Column("copy_from", sa.BigInteger(), nullable=True),
        sa.Column("copy_id", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_snapshot_visualization_link_jump_info")),
    )

    # --- snapshot_visualization_link_jump_target_view_info ---
    op.create_table(
        "snapshot_visualization_link_jump_target_view_info",
        sa.Column("target_id", sa.BigInteger(), nullable=False),
        sa.Column("link_jump_info_id", sa.BigInteger(), nullable=True),
        sa.Column("source_field_active_id", sa.BigInteger(), nullable=True),
        sa.Column("target_view_id", sa.String(255), nullable=True),
        sa.Column("target_field_id", sa.String(255), nullable=True),
        sa.Column("copy_from", sa.BigInteger(), nullable=True),
        sa.Column("copy_id", sa.BigInteger(), nullable=True),
        sa.Column("target_type", sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint(
            "target_id",
            name=op.f("pk_snapshot_visualization_link_jump_target_view_info"),
        ),
    )


def downgrade() -> None:
    op.drop_table("snapshot_visualization_link_jump_target_view_info")
    op.drop_table("snapshot_visualization_link_jump_info")
    op.drop_table("snapshot_visualization_link_jump")
    op.drop_table("snapshot_core_chart_view")
    op.drop_table("snapshot_data_visualization_info")
