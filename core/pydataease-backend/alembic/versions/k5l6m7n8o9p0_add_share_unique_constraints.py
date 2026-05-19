"""add unique constraints on xpack_share

Revision ID: k5l6m7n8o9p0
Revises: j4k5l6m7n8o9
Create Date: 2026-05-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "k5l6m7n8o9p0"
down_revision = "j4k5l6m7n8o9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq_xpack_share_uuid", "xpack_share", ["uuid"])
    op.create_unique_constraint("uq_xpack_share_resource_id", "xpack_share", ["resource_id"])


def downgrade() -> None:
    op.drop_constraint("uq_xpack_share_resource_id", "xpack_share", type_="unique")
    op.drop_constraint("uq_xpack_share_uuid", "xpack_share", type_="unique")
