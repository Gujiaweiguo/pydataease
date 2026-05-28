"""seed demo big-screen (大屏) data

Revision ID: m7n8o9p0q1r2
Revises: l6m7n8o9p0q1
Create Date: 2026-05-28 10:00:00.000000

"""
import subprocess
import pathlib

from alembic import op

revision = "m7n8o9p0q1r2"
down_revision = "l6m7n8o9p0q1"
branch_labels = None
depends_on = None

SEED_SCRIPT = "scripts/seed_demo_data.py"


def _run_screen_seed():
    script = pathlib.Path(__file__).resolve().parents[4] / SEED_SCRIPT
    if not script.exists():
        raise FileNotFoundError(f"Seed script not found: {script}")
    result = subprocess.run(
        ["python3", str(script), "--screen-only"],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Screen seed script failed:\n{result.stderr[:1000]}")


def upgrade() -> None:
    _run_screen_seed()


def downgrade() -> None:
    import sqlalchemy as sa
    conn = op.get_bind()
    conn.execute(sa.text(
        "DELETE FROM core_chart_view WHERE scene_id = 995100000000000002"
    ))
    conn.execute(sa.text(
        "DELETE FROM data_visualization_info "
        "WHERE id IN (995100000000000001, 995100000000000002)"
    ))
