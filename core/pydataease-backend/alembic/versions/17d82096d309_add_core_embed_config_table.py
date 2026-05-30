"""add core_embed_config table

Revision ID: 17d82096d309
Revises: 36d43ebe125d
Create Date: 2026-05-30 16:50:06.358270

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '17d82096d309'
down_revision = '36d43ebe125d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('core_embed_config',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('resource_type', sa.String(length=30), nullable=False, comment='dashboard, chart, datav, dataFiling'),
    sa.Column('embed_enabled', sa.Boolean(), nullable=False, comment='Allow embedding for this resource type'),
    sa.Column('allowed_domains', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='List of allowed domains, empty = all'),
    sa.Column('password_required', sa.Boolean(), nullable=False, comment='Require password for embedded access'),
    sa.Column('ticket_required', sa.Boolean(), nullable=False, comment='Require ticket for embedded access'),
    sa.Column('max_expiry_hours', sa.BigInteger(), nullable=True, comment='Max embed link expiry in hours, null = unlimited'),
    sa.Column('extra_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Future extension config'),
    sa.Column('create_time', sa.DateTime(), nullable=False),
    sa.Column('update_time', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_core_embed_config')),
    sa.UniqueConstraint('resource_type', name=op.f('uq_core_embed_config_resource_type'))
    )


def downgrade() -> None:
    op.drop_table('core_embed_config')
