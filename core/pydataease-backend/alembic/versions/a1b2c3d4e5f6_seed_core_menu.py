"""seed core_menu with community menu items

Revision ID: a1b2c3d4e5f6
Revises: 69eb0d5df3f8
Create Date: 2026-05-10 00:00:00.000000

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "69eb0d5df3f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    core_menu = sa.table(
        "core_menu",
        sa.column("id", sa.BigInteger()),
        sa.column("pid", sa.BigInteger()),
        sa.column("type", sa.Integer()),
        sa.column("name", sa.String(length=45)),
        sa.column("component", sa.String(length=45)),
        sa.column("menu_sort", sa.Integer()),
        sa.column("icon", sa.String(length=45)),
        sa.column("path", sa.String(length=45)),
        sa.column("hidden", sa.Boolean()),
        sa.column("in_layout", sa.Boolean()),
        sa.column("auth", sa.Boolean()),
    )
    # Disable FK checks — root menu items use pid=0 (no id=0 row exists).
    # This is the Java tree convention where 0 means "no parent".
    op.execute("SET session_replication_role = 'replica';")
    op.bulk_insert(
        core_menu,
        [
            # (id, pid, type, name, component, menu_sort, icon, path, hidden, in_layout, auth)
            {"id": 1, "pid": 0, "type": 2, "name": "workbranch", "component": "workbranch", "menu_sort": 1, "icon": None, "path": "/workbranch", "hidden": False, "in_layout": True, "auth": True},
            {"id": 2, "pid": 0, "type": 2, "name": "panel", "component": "visualized/view/panel", "menu_sort": 2, "icon": None, "path": "/panel", "hidden": False, "in_layout": True, "auth": True},
            {"id": 3, "pid": 0, "type": 2, "name": "screen", "component": "visualized/view/screen", "menu_sort": 3, "icon": None, "path": "/screen", "hidden": False, "in_layout": True, "auth": True},
            {"id": 4, "pid": 0, "type": 1, "name": "data", "component": None, "menu_sort": 4, "icon": None, "path": "/data", "hidden": False, "in_layout": True, "auth": False},
            {"id": 5, "pid": 4, "type": 2, "name": "dataset", "component": "visualized/data/dataset", "menu_sort": 1, "icon": None, "path": "/dataset", "hidden": False, "in_layout": True, "auth": True},
            {"id": 6, "pid": 4, "type": 2, "name": "datasource", "component": "visualized/data/datasource", "menu_sort": 2, "icon": None, "path": "/datasource", "hidden": False, "in_layout": True, "auth": True},
            {"id": 11, "pid": 0, "type": 2, "name": "dataset-form", "component": "visualized/data/dataset/form", "menu_sort": 7, "icon": None, "path": "/dataset-form", "hidden": True, "in_layout": False, "auth": False},
            {"id": 12, "pid": 0, "type": 2, "name": "datasource-form", "component": "visualized/data/datasource/form", "menu_sort": 7, "icon": None, "path": "/ds-form", "hidden": True, "in_layout": False, "auth": False},
            {"id": 15, "pid": 0, "type": 1, "name": "sys-setting", "component": None, "menu_sort": 6, "icon": None, "path": "/sys-setting", "hidden": True, "in_layout": True, "auth": False},
            {"id": 16, "pid": 15, "type": 2, "name": "parameter", "component": "system/parameter", "menu_sort": 1, "icon": "sys-parameter", "path": "/parameter", "hidden": False, "in_layout": True, "auth": False},
        ],
    )
    op.execute("SET session_replication_role = 'origin';")


def downgrade() -> None:
    op.execute("DELETE FROM core_menu WHERE id IN (1, 2, 3, 4, 5, 6, 11, 12, 15, 16)")
