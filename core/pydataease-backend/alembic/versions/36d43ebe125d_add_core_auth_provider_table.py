"""add core_auth_provider table

Revision ID: 36d43ebe125d
Revises: p3q4r5s6t7u8
Create Date: 2026-05-30 16:28:37.345048

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '36d43ebe125d'
down_revision = 'p3q4r5s6t7u8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('core_auth_provider',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False, comment='Human-readable provider name'),
    sa.Column('type', sa.String(length=20), nullable=False, comment='Provider type: ldap, oidc, cas, mock'),
    sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Provider-specific configuration'),
    sa.Column('claim_mapping', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Declarative claim mapping rules'),
    sa.Column('enabled', sa.Boolean(), nullable=False),
    sa.Column('is_default', sa.Boolean(), nullable=False, comment='This provider is the default login method'),
    sa.Column('oid', sa.BigInteger(), nullable=True, comment='Org scope, null=global'),
    sa.Column('create_time', sa.DateTime(), nullable=False),
    sa.Column('update_time', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_core_auth_provider'))
    )


def downgrade() -> None:
    op.drop_table('core_auth_provider')
