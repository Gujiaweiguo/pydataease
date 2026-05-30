"""add data filing tables

Revision ID: 7aafbb0a9ea0
Revises: 17d82096d309
Create Date: 2026-05-30 16:59:33.316354

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '7aafbb0a9ea0'
down_revision = '17d82096d309'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('core_filing_audit',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('filing_id', sa.BigInteger(), nullable=False, comment='Reference to FilingConfig'),
    sa.Column('submission_id', sa.BigInteger(), nullable=True, comment='Reference to FilingSubmission'),
    sa.Column('action', sa.String(length=30), nullable=False, comment='submit, publish, disable, retry, config_update'),
    sa.Column('actor_uid', sa.BigInteger(), nullable=True, comment='User who performed the action'),
    sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Action details'),
    sa.Column('outcome', sa.String(length=20), nullable=False, comment='success, failure'),
    sa.Column('error_code', sa.String(length=50), nullable=True, comment='Error code if failed'),
    sa.Column('create_time', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_core_filing_audit'))
    )
    op.create_index(op.f('ix_core_filing_audit_filing_id'), 'core_filing_audit', ['filing_id'], unique=False)
    op.create_table('core_filing_config',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False, comment='Filing form name'),
    sa.Column('status', sa.String(length=20), nullable=False, comment='draft, published, disabled'),
    sa.Column('target_datasource_id', sa.BigInteger(), nullable=True, comment='Target datasource for writes'),
    sa.Column('target_table', sa.String(length=200), nullable=True, comment='Target table name'),
    sa.Column('form_schema', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Form field definitions and validation rules'),
    sa.Column('field_mapping', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Mapping from form fields to target table columns'),
    sa.Column('idempotency_window_seconds', sa.BigInteger(), nullable=False, comment='Idempotency window in seconds'),
    sa.Column('oid', sa.BigInteger(), nullable=True, comment='Org scope'),
    sa.Column('creator_uid', sa.BigInteger(), nullable=True, comment='Creator user ID'),
    sa.Column('create_time', sa.DateTime(), nullable=False),
    sa.Column('update_time', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_core_filing_config'))
    )
    op.create_table('core_filing_submission',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('filing_id', sa.BigInteger(), nullable=False, comment='Reference to FilingConfig'),
    sa.Column('payload_hash', sa.String(length=64), nullable=True, comment='SHA-256 hash of payload for idempotency'),
    sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='Submitted data'),
    sa.Column('status', sa.String(length=20), nullable=False, comment='pending, success, failed, retrying'),
    sa.Column('error_message', sa.Text(), nullable=True, comment='Error details if failed'),
    sa.Column('submitter_uid', sa.BigInteger(), nullable=True, comment='Submitting user ID'),
    sa.Column('retry_count', sa.BigInteger(), nullable=False),
    sa.Column('create_time', sa.DateTime(), nullable=False),
    sa.Column('update_time', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_core_filing_submission'))
    )
    op.create_index(op.f('ix_core_filing_submission_filing_id'), 'core_filing_submission', ['filing_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_core_filing_submission_filing_id'), table_name='core_filing_submission')
    op.drop_table('core_filing_submission')
    op.drop_table('core_filing_config')
    op.drop_index(op.f('ix_core_filing_audit_filing_id'), table_name='core_filing_audit')
    op.drop_table('core_filing_audit')
