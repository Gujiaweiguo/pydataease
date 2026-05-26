"""seed official demo data (tea shop dashboard)

Revision ID: l6m7n8o9p0q1
Revises: 8c54f4f57d7a
Create Date: 2026-05-26 20:00:00.000000

"""
import subprocess

from alembic import op

revision = "l6m7n8o9p0q1"
down_revision = "8c54f4f57d7a"
branch_labels = None
depends_on = None

SEED_SCRIPT = "scripts/seed_demo_data.py"


def _run_seed():
    import pathlib
    script = pathlib.Path(__file__).resolve().parents[4] / SEED_SCRIPT
    if not script.exists():
        raise FileNotFoundError(f"Seed script not found: {script}")
    result = subprocess.run(
        ["python3", str(script)],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Seed script failed:\n{result.stderr[:1000]}")


def upgrade() -> None:
    _run_seed()


def downgrade() -> None:
    import sqlalchemy as sa
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM core_chart_view WHERE scene_id = 985192741891870720"))
    conn.execute(sa.text("DELETE FROM data_visualization_info WHERE id IN (985247460244983808, 985192741891870720)"))
    conn.execute(sa.text("DELETE FROM core_dataset_table_field WHERE dataset_group_id IN (985189703189925888, 985189053949415424)"))
    conn.execute(sa.text("DELETE FROM core_dataset_table WHERE id IN (7193457660727922688, 7193537020143079424)"))
    conn.execute(sa.text("DELETE FROM core_dataset_group WHERE id IN (985189269226262528, 985189703189925888, 985189053949415424)"))
    conn.execute(sa.text("DELETE FROM core_datasource WHERE id = 985188400292302848"))
