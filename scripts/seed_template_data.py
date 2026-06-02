#!/usr/bin/env python3
"""Seed template data for PyDataEase.

Creates 4 built-in templates (2 dashboard + 2 screen) with categories,
so the Template Center shows content out of the box.

Usage:
  python scripts/seed_template_data.py

Requires: docker container `postgres16` running, or SEED_PG_HOST set.
"""

import json
import os
import subprocess
import sys

# ── Connection ───────────────────────────────────────────────────────
PG_HOST = os.getenv("SEED_PG_HOST")
PG_PORT = os.getenv("SEED_PG_PORT", "5432")
PG_USER = os.getenv("SEED_PG_USER", "dataease")
PG_PASS = os.getenv("SEED_PG_PASS", "dataease")
PG_DB = os.getenv("SEED_PG_DB", "dataease")

USE_DIRECT_TCP = bool(PG_HOST)

# ── Fixed IDs (deterministic, won't collide) ─────────────────────────
CAT_DASHBOARD = "900000000000000001"
CAT_SCREEN = "900000000000000002"

TEMPLATES = [
    {
        "id": "900000000000000010",
        "name": "销售分析仪表板",
        "pid": CAT_DASHBOARD,
        "level": 2,
        "dv_type": "PANEL",
        "node_type": "template",
        "template_type": "self",
        "category_id": CAT_DASHBOARD,
    },
    {
        "id": "900000000000000011",
        "name": "运营数据概览",
        "pid": CAT_DASHBOARD,
        "level": 2,
        "dv_type": "PANEL",
        "node_type": "template",
        "template_type": "self",
        "category_id": CAT_DASHBOARD,
    },
    {
        "id": "900000000000000020",
        "name": "实时监控大屏",
        "pid": CAT_SCREEN,
        "level": 2,
        "dv_type": "dataV",
        "node_type": "template",
        "template_type": "self",
        "category_id": CAT_SCREEN,
    },
    {
        "id": "900000000000000021",
        "name": "销售数据大屏",
        "pid": CAT_SCREEN,
        "level": 2,
        "dv_type": "dataV",
        "node_type": "template",
        "template_type": "self",
        "category_id": CAT_SCREEN,
    },
]

# ── Minimal template content ────────────────────────────────────────

PANEL_STYLE = json.dumps({
    "width": 1600,
    "height": 900,
    "scale": 100,
    "scaleWidth": 100,
    "scaleHeight": 100,
    "selfAdaption": True,
    "refreshViewEnable": False,
    "refreshViewLoading": True,
    "refreshUnit": "minute",
    "refreshTime": 5,
    "popupAvailable": False,
    "suspensionAvailable": False,
    "dashboardAdaptor": "keepHeight",
})

PANEL_DATA = json.dumps([])
PANEL_DYNAMIC = json.dumps({})

SCREEN_STYLE = json.dumps({
    "width": 1920,
    "height": 1080,
    "scale": 100,
    "scaleWidth": 100,
    "scaleHeight": 100,
    "selfAdaption": True,
    "refreshViewEnable": False,
    "refreshViewLoading": True,
    "refreshUnit": "minute",
    "refreshTime": 5,
    "screenAdaptor": "full",
    "popupAvailable": False,
    "suspensionAvailable": False,
})

SNAPSHOT = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

# ── Helpers ──────────────────────────────────────────────────────────

def docker_psql(sql: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "exec", "postgres16", "psql", "-U", PG_USER, "-d", PG_DB, "-c", sql],
        capture_output=True, text=True, timeout=30,
    )

def tcp_psql(sql: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PGPASSWORD": PG_PASS}
    return subprocess.run(
        ["psql", "-h", PG_HOST, "-p", PG_PORT, "-U", PG_USER, "-d", PG_DB, "-c", sql],
        capture_output=True, text=True, timeout=30, env=env,
    )

def psql(sql: str) -> subprocess.CompletedProcess[str]:
    if USE_DIRECT_TCP:
        return tcp_psql(sql)
    return docker_psql(sql)

def sql_val(val: str) -> str:
    return "'" + val.replace("'", "''") + "'"

def check_exists() -> bool:
    r = psql(f"SELECT COUNT(*) FROM visualization_template WHERE id = '{TEMPLATES[0]['id']}';")
    return "1" in r.stdout.split("\n")[2] if r.returncode == 0 else False

# ── Main ─────────────────────────────────────────────────────────────

def main() -> None:
    if check_exists():
        print("✓ Template data already seeded, skipping.")
        return

    print("Seeding template data...")

    # Create categories
    for cat_id, cat_name, dv_type in [
        (CAT_DASHBOARD, "仪表板模板", "PANEL"),
        (CAT_SCREEN, "大屏模板", "dataV"),
    ]:
        psql(f"""
            INSERT INTO visualization_template_category
                (id, name, pid, level, dv_type, node_type, create_by, create_time, snapshot, template_type)
            VALUES ({sql_val(cat_id)}, {sql_val(cat_name)}, '0', 1, {sql_val(dv_type)}, 'folder', 'admin', EXTRACT(EPOCH FROM NOW())::bigint * 1000, '', 'self')
            ON CONFLICT (id) DO NOTHING;
        """)

    # Create templates
    for t in TEMPLATES:
        style = PANEL_STYLE if t["dv_type"] == "PANEL" else SCREEN_STYLE
        psql(f"""
            INSERT INTO visualization_template
                (id, name, pid, level, dv_type, node_type, create_by, create_time, snapshot, template_type, template_style, template_data, dynamic_data)
            VALUES (
                {sql_val(t['id'])}, {sql_val(t['name'])}, {sql_val(t['pid'])}, {t['level']},
                {sql_val(t['dv_type'])}, {sql_val(t['node_type'])}, 'admin',
                EXTRACT(EPOCH FROM NOW())::bigint * 1000,
                {sql_val(SNAPSHOT)}, {sql_val(t['template_type'])},
                {sql_val(style)}::jsonb, {sql_val(PANEL_DATA)}::jsonb, {sql_val(PANEL_DYNAMIC)}::jsonb
            )
            ON CONFLICT (id) DO NOTHING;
        """)

        # Create category map
        map_id = t["id"][:-1] + "3"
        psql(f"""
            INSERT INTO visualization_template_category_map (id, category_id, template_id)
            VALUES ({sql_val(map_id)}, {sql_val(t['category_id'])}, {sql_val(t['id'])})
            ON CONFLICT (id) DO NOTHING;
        """)

    print("✓ Seeded 4 templates (2 dashboard + 2 screen) with 2 categories.")


if __name__ == "__main__":
    main()
