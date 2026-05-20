"""add sys_variable and sys_variable_value tables

Revision ID: 8c54f4f57d7a
Revises: k5l6m7n8o9p0
Create Date: 2026-05-21 07:11:44.874463

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '8c54f4f57d7a'
down_revision = 'k5l6m7n8o9p0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('core_sys_variable',
    sa.Column('id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('alias', sa.String(length=255), nullable=True),
    sa.Column('type', sa.String(length=100), nullable=True),
    sa.Column('remark', sa.Text(), nullable=True),
    sa.Column('dataset_group_id', sa.BigInteger(), nullable=True),
    sa.Column('dataset_table_id', sa.BigInteger(), nullable=True),
    sa.Column('create_time', sa.BigInteger(), nullable=True),
    sa.Column('update_time', sa.BigInteger(), nullable=True),
    sa.Column('create_by', sa.BigInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_core_sys_variable'))
    )
    op.create_table('core_sys_variable_value',
    sa.Column('id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('variable_id', sa.BigInteger(), nullable=False),
    sa.Column('value', sa.Text(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('remark', sa.Text(), nullable=True),
    sa.Column('create_time', sa.BigInteger(), nullable=True),
    sa.Column('update_time', sa.BigInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_core_sys_variable_value'))
    )


def downgrade() -> None:
    op.drop_table('core_sys_variable_value')
    op.drop_table('core_sys_variable')
