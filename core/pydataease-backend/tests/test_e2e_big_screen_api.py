"""E2E API tests for the demo big screen — findById and chart/getData."""
from __future__ import annotations

import pytest
import httpx

from tests.fixtures.e2e_helpers import (  # pyright: ignore[reportImplicitRelativeImport]
    BASE_URL,
    E2E_GATE,
    login,
)

SCREEN_DV = "995100000000000002"
SCREEN_FOLDER = "995100000000000001"
CHART_IDS = [
    "995100000000000100",
    "995100000000000101", "995100000000000102",
    "995100000000000103", "995100000000000104",
    "995100000000000105", "995100000000000106",
    "995100000000000107", "995100000000000108",
    "995100000000000109", "995100000000000110",
    "995100000000000111", "995100000000000112",
]


@pytest.fixture
async def api_client():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=60.0) as client:
        yield client


@E2E_GATE
@pytest.mark.asyncio
async def test_big_screen_api_find_by_id(api_client: httpx.AsyncClient) -> None:
    headers = await login(api_client)

    resp = await api_client.post(
        "/de2api/dataVisualization/findById",
        json={"id": SCREEN_DV, "busiFlag": "dataV"},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0, f"API error: {body.get('msg')}"

    data = body["data"]
    assert data["name"] == "连锁茶饮销售大屏"
    assert data["type"] == "screen"
    assert data["nodeType"] == "leaf"

    import json
    components = json.loads(data["componentData"])
    assert len(components) == 13
    assert all(c.get("isShow") is True for c in components)

    canvas_info = data["canvasViewInfo"]
    assert len(canvas_info) == 13, f"Expected 13 canvasViewInfo, got {len(canvas_info)}"


@E2E_GATE
@pytest.mark.asyncio
async def test_big_screen_api_interactive_tree(api_client: httpx.AsyncClient) -> None:
    headers = await login(api_client)

    resp = await api_client.post(
        "/de2api/dataVisualization/interactiveTree",
        json={"dataV": {"busiFlag": "dataV"}},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0

    tree = body["data"]
    data_v_tree = tree.get("dataV", [])
    assert len(data_v_tree) > 0, "dataV tree should not be empty"

    def find(nodes, fid):
        for node in nodes:
            if node.get("id") == str(fid):
                return node
            found = find(node.get("children", []), fid)
            if found:
                return found
        return None

    folder_node = find(data_v_tree, int(SCREEN_FOLDER))
    assert folder_node is not None, "Screen folder not found in tree"

    screen_node = find([folder_node], int(SCREEN_DV))
    assert screen_node is not None, "Screen leaf not found under folder"


@E2E_GATE
@pytest.mark.asyncio
async def test_big_screen_api_kpi_returns_value(api_client: httpx.AsyncClient) -> None:
    headers = await login(api_client)

    resp = await api_client.post(
        "/de2api/chart/getData",
        json={"id": CHART_IDS[1]},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0, f"KPI chart error: {body.get('data', {}).get('error')}"

    data = body["data"]
    assert data["type"] == "indicator"
    assert data.get("error") is None

    data_items = data.get("data", [])
    assert len(data_items) >= 1, "KPI should return at least 1 data point"
    assert data_items[0]["value"] > 0, "KPI value should be positive"


@E2E_GATE
@pytest.mark.asyncio
async def test_big_screen_api_trend_chart_has_data(api_client: httpx.AsyncClient) -> None:
    headers = await login(api_client)

    resp = await api_client.post(
        "/de2api/chart/getData",
        json={"id": CHART_IDS[5]},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert data.get("error") is None

    data_items = data.get("data", [])
    assert len(data_items) >= 2, "Trend chart should have multiple data points"


@E2E_GATE
@pytest.mark.asyncio
async def test_big_screen_api_pie_chart_has_segments(api_client: httpx.AsyncClient) -> None:
    headers = await login(api_client)

    resp = await api_client.post(
        "/de2api/chart/getData",
        json={"id": CHART_IDS[7]},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert data.get("error") is None

    data_items = data.get("data", [])
    assert len(data_items) >= 2, f"冷热饮 pie should have >= 2 segments, got {len(data_items)}"
