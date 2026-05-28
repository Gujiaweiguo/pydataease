"""End-to-end tests for the demo big screen (dataV) seed data.

Requires running PostgreSQL with seed data applied (DE_E2E=1).
"""
from __future__ import annotations

import os

import pytest

skip_no_db = pytest.mark.skipif(
    not os.getenv("DE_E2E"),
    reason="Set DE_E2E=1 to run big-screen e2e tests",
)

SCREEN_FOLDER = 995100000000000001
SCREEN_DV = 995100000000000002
BANNER_ID = 995100000000000100
SCREEN_CHART_IDS = [
    BANNER_ID,
    995100000000000101, 995100000000000102,
    995100000000000103, 995100000000000104,
    995100000000000105, 995100000000000106,
    995100000000000107, 995100000000000108,
    995100000000000109, 995100000000000110,
    995100000000000111, 995100000000000112,
]


def _parse_jsonb(value):
    if isinstance(value, str):
        import json
        return json.loads(value)
    return value


@skip_no_db
@pytest.mark.asyncio
async def test_big_screen_seed_visualization_records(db_session):
    from sqlalchemy import text

    result = await db_session.execute(
        text("SELECT id, name, type, node_type, status FROM data_visualization_info "
             f"WHERE id IN ({SCREEN_FOLDER}, {SCREEN_DV}) ORDER BY id")
    )
    rows = result.fetchall()
    assert len(rows) == 2, f"Expected 2 visualization records, found {len(rows)}"

    folder = rows[0]
    assert folder.id == SCREEN_FOLDER
    assert folder.type == "screen"
    assert folder.node_type == "folder"

    screen = rows[1]
    assert screen.id == SCREEN_DV
    assert screen.name == "连锁茶饮销售大屏"
    assert screen.type == "screen"
    assert screen.node_type == "leaf"
    assert screen.status == 1


@skip_no_db
@pytest.mark.asyncio
async def test_big_screen_seed_component_data_structure(db_session):
    from sqlalchemy import text

    result = await db_session.execute(
        text(f"SELECT component_data FROM data_visualization_info WHERE id = {SCREEN_DV}")
    )
    components = _parse_jsonb(result.scalar())
    assert len(components) == 13

    expected_ids = {str(cid) for cid in SCREEN_CHART_IDS}
    actual_ids = {comp["id"] for comp in components}
    assert actual_ids == expected_ids

    for i, comp in enumerate(components):
        assert comp["component"] == "UserView", f"Component {i} wrong type"
        assert comp["isShow"] is True, f"Component {i} missing isShow=True"
        assert "left" in comp["style"], f"Component {i} missing style.left"
        assert "top" in comp["style"], f"Component {i} missing style.top"
        assert comp["style"]["width"] > 0, f"Component {i} has zero width"
        assert comp["style"]["height"] > 0, f"Component {i} has zero height"

    assert components[0]["id"] == str(BANNER_ID)
    assert components[0]["style"]["top"] == 0, "Banner should be at top"
    assert components[0]["style"]["left"] == 0, "Banner should start at left edge"
    assert components[1]["style"]["top"] > 0, "Charts should be below banner"


@skip_no_db
@pytest.mark.asyncio
async def test_big_screen_seed_chart_views_exist(db_session):
    from sqlalchemy import text

    ids_str = ",".join(str(cid) for cid in SCREEN_CHART_IDS)
    result = await db_session.execute(
        text(f"SELECT id, title, type, render, scene_id FROM core_chart_view WHERE id IN ({ids_str}) ORDER BY id")
    )
    rows = result.fetchall()
    assert len(rows) == 13, f"Expected 13 chart views, found {len(rows)}"

    assert rows[0].type == "rich-text", "First chart should be rich-text banner"
    assert rows[0].render == "custom", "Banner should use custom render"

    kpi_rows = rows[1:5]
    kpi_types = {row.type for row in kpi_rows}
    assert kpi_types == {"indicator"}, f"KPI cards should be indicator type, got {kpi_types}"

    for row in kpi_rows:
        assert row.render == "custom", f"KPI chart {row.id} should render=custom, got {row.render}"

    chart_types = {row.type for row in rows[5:]}
    assert "area" in chart_types
    assert "line" in chart_types
    assert "pie-donut" in chart_types
    assert "bar-horizontal" in chart_types
    assert "bar" in chart_types

    for row in rows:
        assert row.scene_id == SCREEN_DV


@skip_no_db
@pytest.mark.asyncio
async def test_big_screen_seed_dark_theme_canvas(db_session):
    from sqlalchemy import text

    result = await db_session.execute(
        text(f"SELECT canvas_style_data FROM data_visualization_info WHERE id = {SCREEN_DV}")
    )
    style = _parse_jsonb(result.scalar())

    assert style["width"] == 1920
    assert style["height"] == 1190
    assert style["backgroundColor"] == "rgba(13,26,56,1)"
    assert style["backgroundColorSelect"] is True
    assert style["screenAdaptor"] == "widthFirst"


@skip_no_db
@pytest.mark.asyncio
async def test_big_screen_seed_auto_refresh_enabled(db_session):
    from sqlalchemy import text

    result = await db_session.execute(
        text(f"SELECT canvas_style_data FROM data_visualization_info WHERE id = {SCREEN_DV}")
    )
    style = _parse_jsonb(result.scalar())

    assert style["refreshViewEnable"] is True, "Auto-refresh should be enabled"
    assert style["refreshTime"] > 0, "Refresh interval should be positive"
    assert style["refreshUnit"] in ("second", "minute"), f"Invalid refresh unit: {style['refreshUnit']}"


@skip_no_db
@pytest.mark.asyncio
async def test_big_screen_seed_cold_hot_chart_no_slash(db_session):
    from sqlalchemy import text

    cold_hot_idx = next(i for i, cid in enumerate(SCREEN_CHART_IDS) if cid == 995100000000000108)
    result = await db_session.execute(
        text(f"SELECT x_axis FROM core_chart_view WHERE id = {SCREEN_CHART_IDS[cold_hot_idx]}")
    )
    x_axis = _parse_jsonb(result.scalar())
    assert len(x_axis) == 1
    assert "/" not in x_axis[0]["originName"], (
        f"冷热饮 dimension should not contain slash: {x_axis[0]['originName']}"
    )


@skip_no_db
@pytest.mark.asyncio
async def test_big_screen_seed_banner_is_rich_text(db_session):
    from sqlalchemy import text

    result = await db_session.execute(
        text(f"SELECT type, render FROM core_chart_view WHERE id = {BANNER_ID}")
    )
    row = result.fetchone()
    assert row is not None, "Banner chart view should exist"
    assert row.type == "rich-text"
    assert row.render == "custom"


@skip_no_db
@pytest.mark.asyncio
async def test_big_screen_seed_banner_has_board_decoration(db_session):
    from sqlalchemy import text

    result = await db_session.execute(
        text(f"SELECT component_data FROM data_visualization_info WHERE id = {SCREEN_DV}")
    )
    components = _parse_jsonb(result.scalar())
    banner = components[0]
    bg = banner["commonBackground"]
    assert bg["backgroundImageEnable"] is True, "Banner board decoration should be enabled"
    assert bg["backgroundType"] == "innerImage"
    assert "board_" in bg["innerImage"], f"Banner should use board SVG, got {bg['innerImage']}"


@skip_no_db
@pytest.mark.asyncio
async def test_big_screen_seed_datasets_referenced_exist(db_session):
    from sqlalchemy import text

    chart_ids_str = ",".join(str(cid) for cid in SCREEN_CHART_IDS)
    result = await db_session.execute(
        text(f"SELECT DISTINCT table_id FROM core_chart_view WHERE id IN ({chart_ids_str})")
    )
    table_ids = [row.table_id for row in result.fetchall()]
    assert len(table_ids) >= 1, "Charts should reference at least one dataset"

    for tid in table_ids:
        check = await db_session.execute(
            text(f"SELECT id FROM core_dataset_group WHERE id = {tid}")
        )
        assert check.scalar() is not None, f"Referenced dataset {tid} not found"


@skip_no_db
@pytest.mark.asyncio
async def test_big_screen_seed_screen_in_interactive_tree(db_session):
    from sqlalchemy import text

    result = await db_session.execute(
        text(f"SELECT id, pid, name, type, node_type FROM data_visualization_info "
             f"WHERE id IN ({SCREEN_FOLDER}, {SCREEN_DV}) ORDER BY id")
    )
    rows = result.fetchall()
    assert len(rows) == 2

    folder = rows[0]
    assert folder.pid in (0, None), "Screen folder should be at root level"
    screen = rows[1]
    assert screen.pid == SCREEN_FOLDER, "Screen should be under the folder"


@skip_no_db
@pytest.mark.asyncio
async def test_big_screen_seed_idempotent(db_session):
    from sqlalchemy import text

    expected_viz = 2
    expected_charts = 13

    result = await db_session.execute(
        text(f"SELECT count(*) FROM data_visualization_info "
             f"WHERE id IN ({SCREEN_FOLDER}, {SCREEN_DV})")
    )
    assert result.scalar() == expected_viz

    result = await db_session.execute(
        text(f"SELECT count(*) FROM core_chart_view WHERE scene_id = {SCREEN_DV}")
    )
    assert result.scalar() == expected_charts

    import pathlib
    import subprocess
    script = pathlib.Path(__file__).resolve().parents[3] / "scripts" / "seed_demo_data.py"
    r = subprocess.run(
        ["python3", str(script), "--screen-only"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Second seed run failed: {r.stderr[:500]}"

    result = await db_session.execute(
        text(f"SELECT count(*) FROM data_visualization_info "
             f"WHERE id IN ({SCREEN_FOLDER}, {SCREEN_DV})")
    )
    assert result.scalar() == expected_viz

    result = await db_session.execute(
        text(f"SELECT count(*) FROM core_chart_view WHERE scene_id = {SCREEN_DV}")
    )
    assert result.scalar() == expected_charts
