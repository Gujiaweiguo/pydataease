"""add link jump tables

Revision ID: a2b3c4d5e6f7
Revises: i3c4d5e6f7a8
Create Date: 2026-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a2b3c4d5e6f7"
down_revision: Union[str, None] = "i3c4d5e6f7a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- visualization_link_jump ---
    op.create_table(
        "visualization_link_jump",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("source_dv_id", sa.BigInteger(), nullable=True),
        sa.Column("source_view_id", sa.BigInteger(), nullable=True),
        sa.Column("link_jump_info", sa.String(255), nullable=True),
        sa.Column("checked", sa.Boolean(), nullable=True),
        sa.Column("copy_from", sa.BigInteger(), nullable=True),
        sa.Column("copy_id", sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_visualization_link_jump")),
    )

    # --- visualization_link_jump_info ---
    op.create_table(
        "visualization_link_jump_info",
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_visualization_link_jump_info")),
    )

    # --- visualization_link_jump_target_view_info ---
    op.create_table(
        "visualization_link_jump_target_view_info",
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
            name=op.f("pk_visualization_link_jump_target_view_info"),
        ),
    )


def downgrade() -> None:
    op.drop_table("visualization_link_jump_target_view_info")
    op.drop_table("visualization_link_jump_info")
    op.drop_table("visualization_link_jump")
