"""initial_schema

Revision ID: 9fabd277b7b0
Revises: 
Create Date: 2026-05-10 09:56:16.294713

"""
# pyright: reportUnusedCallResult=false, reportUnknownArgumentType=false

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql



# revision identifiers, used by Alembic.
revision = '9fabd277b7b0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'core_datasource',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('pid', sa.BigInteger(), nullable=True),
        sa.Column('edit_type', sa.String(length=50), nullable=True),
        sa.Column('configuration', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('create_time', sa.BigInteger(), nullable=False),
        sa.Column('update_time', sa.BigInteger(), nullable=False),
        sa.Column('update_by', sa.BigInteger(), nullable=True),
        sa.Column('create_by', sa.String(length=50), nullable=True),
        sa.Column('status', sa.Text(), nullable=True),
        sa.Column('qrtz_instance', sa.Text(), nullable=True),
        sa.Column('task_status', sa.String(length=50), nullable=True),
        sa.Column('enable_data_fill', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.ForeignKeyConstraint(['pid'], ['core_datasource.id']),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_core_datasource')),
    )
    op.create_table(
        'core_dataset_group',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=True),
        sa.Column('pid', sa.BigInteger(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True, server_default=sa.text('0')),
        sa.Column('node_type', sa.String(length=50), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('mode', sa.Integer(), nullable=True, server_default=sa.text('0')),
        sa.Column('info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('create_by', sa.String(length=50), nullable=True),
        sa.Column('create_time', sa.BigInteger(), nullable=True),
        sa.Column('qrtz_instance', sa.String(length=1024), nullable=True),
        sa.Column('sync_status', sa.String(length=45), nullable=True),
        sa.Column('update_by', sa.String(length=50), nullable=True),
        sa.Column('last_update_time', sa.BigInteger(), nullable=True, server_default=sa.text('0')),
        sa.Column('union_sql', sa.Text(), nullable=True),
        sa.Column('is_cross', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.ForeignKeyConstraint(['pid'], ['core_dataset_group.id']),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_core_dataset_group')),
    )
    op.create_table(
        'core_dataset_table',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=True),
        sa.Column('table_name', sa.String(length=128), nullable=True),
        sa.Column('datasource_id', sa.BigInteger(), nullable=True),
        sa.Column('dataset_group_id', sa.BigInteger(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('info', sa.Text(), nullable=True),
        sa.Column('sql_variable_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['dataset_group_id'], ['core_dataset_group.id']),
        sa.ForeignKeyConstraint(['datasource_id'], ['core_datasource.id']),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_core_dataset_table')),
    )
    op.create_table(
        'data_visualization_info',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('pid', sa.BigInteger(), nullable=True),
        sa.Column('org_id', sa.BigInteger(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('node_type', sa.String(length=255), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('canvas_style_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('component_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('mobile_layout', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.Column('status', sa.Integer(), nullable=True, server_default=sa.text('1')),
        sa.Column('self_watermark_status', sa.Integer(), nullable=True, server_default=sa.text('0')),
        sa.Column('sort', sa.Integer(), nullable=True, server_default=sa.text('0')),
        sa.Column('create_time', sa.BigInteger(), nullable=True),
        sa.Column('create_by', sa.String(length=255), nullable=True),
        sa.Column('update_time', sa.BigInteger(), nullable=True),
        sa.Column('update_by', sa.String(length=255), nullable=True),
        sa.Column('remark', sa.String(length=255), nullable=True),
        sa.Column('source', sa.String(length=255), nullable=True),
        sa.Column('delete_flag', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.Column('delete_time', sa.BigInteger(), nullable=True),
        sa.Column('delete_by', sa.String(length=255), nullable=True),
        sa.Column('version', sa.Integer(), nullable=True, server_default=sa.text('3')),
        sa.Column('content_id', sa.String(length=50), nullable=True, server_default=sa.text("'0'")),
        sa.Column('check_version', sa.String(length=50), nullable=True, server_default=sa.text("'1'")),
        sa.ForeignKeyConstraint(['pid'], ['data_visualization_info.id']),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_data_visualization_info')),
    )
    op.create_table(
        'core_datasource_task',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('ds_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('update_type', sa.String(length=50), nullable=False),
        sa.Column('start_time', sa.BigInteger(), nullable=True),
        sa.Column('sync_rate', sa.String(length=50), nullable=False),
        sa.Column('cron', sa.String(length=255), nullable=True),
        sa.Column('simple_cron_value', sa.BigInteger(), nullable=True),
        sa.Column('simple_cron_type', sa.String(length=50), nullable=True),
        sa.Column('end_time', sa.BigInteger(), nullable=True),
        sa.Column('create_time', sa.BigInteger(), nullable=True),
        sa.Column('last_exec_time', sa.BigInteger(), nullable=True),
        sa.Column('last_exec_status', sa.String(length=50), nullable=True),
        sa.Column('extra_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('task_status', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['ds_id'], ['core_datasource.id']),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_core_datasource_task')),
    )
    op.create_table(
        'core_de_engine',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=True),
        sa.Column('description', sa.String(length=50), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('configuration', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('create_time', sa.BigInteger(), nullable=True),
        sa.Column('update_time', sa.BigInteger(), nullable=True),
        sa.Column('create_by', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=45), nullable=True),
        sa.Column('enable_data_fill', sa.Boolean(), nullable=True, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_core_de_engine')),
    )
    op.create_table(
        'core_menu',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('pid', sa.BigInteger(), nullable=False),
        sa.Column('type', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=45), nullable=True),
        sa.Column('component', sa.String(length=45), nullable=True),
        sa.Column('menu_sort', sa.Integer(), nullable=True),
        sa.Column('icon', sa.String(length=45), nullable=True),
        sa.Column('path', sa.String(length=45), nullable=True),
        sa.Column('hidden', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('in_layout', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('auth', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.ForeignKeyConstraint(['pid'], ['core_menu.id']),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_core_menu')),
    )
    op.create_table(
        'xpack_share',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('creator', sa.BigInteger(), nullable=False),
        sa.Column('time', sa.BigInteger(), nullable=False),
        sa.Column('exp', sa.BigInteger(), nullable=True),
        sa.Column('uuid', sa.String(length=16), nullable=False),
        sa.Column('pwd', sa.String(length=255), nullable=True),
        sa.Column('resource_id', sa.BigInteger(), nullable=False),
        sa.Column('oid', sa.BigInteger(), nullable=False),
        sa.Column('type', sa.Integer(), nullable=False),
        sa.Column('auto_pwd', sa.Boolean(), nullable=True, server_default=sa.text('true')),
        sa.Column('ticket_require', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_xpack_share')),
    )
    op.create_table(
        'core_share_ticket',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('uuid', sa.String(length=255), nullable=False),
        sa.Column('ticket', sa.String(length=255), nullable=False),
        sa.Column('exp', sa.BigInteger(), nullable=True),
        sa.Column('args', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('access_time', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_core_share_ticket')),
    )
    op.create_table(
        'core_store',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('resource_id', sa.BigInteger(), nullable=False),
        sa.Column('uid', sa.BigInteger(), nullable=False),
        sa.Column('resource_type', sa.Integer(), nullable=False),
        sa.Column('time', sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_core_store')),
    )
    op.create_table(
        'core_export_task',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('file_name', sa.String(length=2048), nullable=True),
        sa.Column('file_size', sa.Double(), nullable=True),
        sa.Column('file_size_unit', sa.String(length=255), nullable=True),
        sa.Column('export_from', sa.BigInteger(), nullable=True),
        sa.Column('export_status', sa.String(length=255), nullable=True),
        sa.Column('export_from_type', sa.String(length=255), nullable=True),
        sa.Column('export_time', sa.BigInteger(), nullable=True),
        sa.Column('export_progress', sa.String(length=255), nullable=True),
        sa.Column('export_machine_name', sa.String(length=512), nullable=True),
        sa.Column('params', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('msg', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_core_export_task')),
    )
    op.create_table(
        'core_chart_view',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(length=1024), nullable=True),
        sa.Column('scene_id', sa.BigInteger(), nullable=False),
        sa.Column('table_id', sa.BigInteger(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('render', sa.String(length=50), nullable=True),
        sa.Column('result_count', sa.Integer(), nullable=True),
        sa.Column('result_mode', sa.String(length=50), nullable=True),
        sa.Column('x_axis', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('x_axis_ext', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('y_axis', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('y_axis_ext', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ext_stack', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ext_bubble', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ext_label', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ext_tooltip', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('custom_attr', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('custom_style', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('custom_filter', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('drill_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('senior', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('create_by', sa.String(length=50), nullable=True),
        sa.Column('create_time', sa.BigInteger(), nullable=True),
        sa.Column('update_time', sa.BigInteger(), nullable=True),
        sa.Column('snapshot', sa.Text(), nullable=True),
        sa.Column('style_priority', sa.String(length=255), nullable=True, server_default=sa.text("'panel'")),
        sa.Column('chart_type', sa.String(length=255), nullable=True, server_default=sa.text("'private'")),
        sa.Column('is_plugin', sa.Boolean(), nullable=True),
        sa.Column('data_from', sa.String(length=255), nullable=True, server_default=sa.text("'dataset'")),
        sa.Column('view_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('refresh_view_enable', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.Column('refresh_unit', sa.String(length=255), nullable=True, server_default=sa.text("'minute'")),
        sa.Column('refresh_time', sa.Integer(), nullable=True, server_default=sa.text('5')),
        sa.Column('linkage_active', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.Column('jump_active', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.Column('copy_from', sa.BigInteger(), nullable=True),
        sa.Column('copy_id', sa.BigInteger(), nullable=True),
        sa.Column('aggregate', sa.Boolean(), nullable=True),
        sa.Column('flow_map_start_name', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('flow_map_end_name', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ext_color', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('custom_attr_mobile', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('custom_style_mobile', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('sort_priority', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['scene_id'], ['data_visualization_info.id']),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_core_chart_view')),
    )
    op.create_table(
        'core_dataset_table_field',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('datasource_id', sa.BigInteger(), nullable=True),
        sa.Column('dataset_table_id', sa.BigInteger(), nullable=True),
        sa.Column('dataset_group_id', sa.BigInteger(), nullable=True),
        sa.Column('chart_id', sa.BigInteger(), nullable=True),
        sa.Column('origin_name', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('dataease_name', sa.String(length=255), nullable=True),
        sa.Column('field_short_name', sa.String(length=255), nullable=True),
        sa.Column('group_list', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('other_group', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('group_type', sa.String(length=50), nullable=True),
        sa.Column('type', sa.String(length=255), nullable=False),
        sa.Column('size', sa.Integer(), nullable=True),
        sa.Column('de_type', sa.Integer(), nullable=False),
        sa.Column('de_extract_type', sa.Integer(), nullable=False),
        sa.Column('ext_field', sa.Integer(), nullable=True),
        sa.Column('checked', sa.Boolean(), nullable=True, server_default=sa.text('true')),
        sa.Column('column_index', sa.Integer(), nullable=True),
        sa.Column('last_sync_time', sa.BigInteger(), nullable=True),
        sa.Column('accuracy', sa.Integer(), nullable=True, server_default=sa.text('0')),
        sa.Column('date_format', sa.String(length=255), nullable=True),
        sa.Column('date_format_type', sa.String(length=255), nullable=True),
        sa.Column('params', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('order_checked', sa.Boolean(), nullable=True, server_default=sa.text('false')),
        sa.ForeignKeyConstraint(['dataset_group_id'], ['core_dataset_group.id']),
        sa.ForeignKeyConstraint(['dataset_table_id'], ['core_dataset_table.id']),
        sa.ForeignKeyConstraint(['datasource_id'], ['core_datasource.id']),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_core_dataset_table_field')),
    )
    op.create_table(
        'core_datasource_task_log',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('ds_id', sa.BigInteger(), nullable=False),
        sa.Column('task_id', sa.BigInteger(), nullable=True),
        sa.Column('start_time', sa.BigInteger(), nullable=True),
        sa.Column('end_time', sa.BigInteger(), nullable=True),
        sa.Column('task_status', sa.String(length=50), nullable=False),
        sa.Column('table_name', sa.String(length=255), nullable=False),
        sa.Column('info', sa.Text(), nullable=True),
        sa.Column('create_time', sa.BigInteger(), nullable=True),
        sa.Column('trigger_type', sa.String(length=45), nullable=True),
        sa.ForeignKeyConstraint(['ds_id'], ['core_datasource.id']),
        sa.ForeignKeyConstraint(['task_id'], ['core_datasource_task.id']),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_core_datasource_task_log')),
    )
    op.create_index('idx_core_datasource_task_log_ds_id', 'core_datasource_task_log', ['ds_id'], unique=False)
    op.create_index('idx_core_datasource_task_log_task_id', 'core_datasource_task_log', ['task_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_core_datasource_task_log_task_id', table_name='core_datasource_task_log')
    op.drop_index('idx_core_datasource_task_log_ds_id', table_name='core_datasource_task_log')
    op.drop_table('core_datasource_task_log')
    op.drop_table('core_dataset_table_field')
    op.drop_table('core_chart_view')
    op.drop_table('core_export_task')
    op.drop_table('core_store')
    op.drop_table('core_share_ticket')
    op.drop_table('xpack_share')
    op.drop_table('core_menu')
    op.drop_table('core_de_engine')
    op.drop_table('core_datasource_task')
    op.drop_table('data_visualization_info')
    op.drop_table('core_dataset_table')
    op.drop_table('core_dataset_group')
    op.drop_table('core_datasource')
