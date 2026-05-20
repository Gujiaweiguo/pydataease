"""Tests for dataset data and chart field/data routes."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from typing import Any

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]


def _route_path(route: Any) -> str | None:
    return getattr(route, "path", None)


def _route_registered_methods(route: Any) -> set[str]:
    methods = getattr(route, "methods", None)
    return set(methods) if methods is not None else set()


@pytest.fixture
def route_paths() -> set[str]:
    """Collect all registered route paths."""
    return {path for route in app.routes if (path := _route_path(route)) is not None}


@pytest.fixture
def route_methods() -> dict[str, set[str]]:
    """Collect allowed methods for registered routes."""
    return {
        path: _route_registered_methods(route)
        for route in app.routes
        if (path := _route_path(route)) is not None
    }


class TestDatasetDataRoutesRegistered:
    """Verify dataset data routes are registered."""

    def test_preview_data_route(self, route_paths: set[str]) -> None:
        assert "/de2api/datasetData/previewData" in route_paths

    def test_enum_value_route(self, route_paths: set[str]) -> None:
        assert "/de2api/datasetData/enumValue" in route_paths

    def test_enum_value_obj_route(self, route_paths: set[str]) -> None:
        assert "/de2api/datasetData/enumValueObj" in route_paths

    def test_enum_value_ds_route(self, route_paths: set[str]) -> None:
        assert "/de2api/datasetData/enumValueDs" in route_paths

    def test_get_field_tree_route(self, route_paths: set[str]) -> None:
        assert "/de2api/datasetData/getFieldTree" in route_paths

    def test_inner_export_dataset_details_route(self, route_paths: set[str]) -> None:
        assert "/de2api/datasetData/innerExportDataSetDetails" in route_paths


class TestChartFieldRoutesRegistered:
    """Verify chart field routes are registered."""

    def test_list_by_dq_route(self, route_paths: set[str]) -> None:
        assert "/de2api/chart/listByDQ/{dataset_group_id}/{chart_id}" in route_paths

    def test_copy_field_route(self, route_paths: set[str]) -> None:
        assert "/de2api/chart/copyField/{field_id}/{chart_id}" in route_paths

    def test_delete_field_route(self, route_paths: set[str]) -> None:
        assert "/de2api/chart/deleteField/{field_id}" in route_paths

    def test_delete_field_by_chart_route(self, route_paths: set[str]) -> None:
        assert "/de2api/chart/deleteFieldByChart/{chart_id}" in route_paths


class TestChartDataRoutesRegistered:
    """Verify chart data routes are registered."""

    def test_get_field_data_route(self, route_paths: set[str]) -> None:
        assert "/de2api/chartData/getFieldData/{field_id}/{field_type}" in route_paths

    def test_get_drill_field_data_route(self, route_paths: set[str]) -> None:
        assert "/de2api/chartData/getDrillFieldData/{field_id}" in route_paths

    def test_check_same_dataset_route(self, route_paths: set[str]) -> None:
        assert "/de2api/chart/checkSameDataSet/{source_view_id}/{target_view_id}" in route_paths


class TestRouteContracts:
    """Verify route methods match the expected contract."""

    def test_dataset_data_methods(self, route_methods: dict[str, set[str]]) -> None:
        assert "POST" in route_methods["/de2api/datasetData/previewData"]
        assert "POST" in route_methods["/de2api/datasetData/enumValue"]
        assert "POST" in route_methods["/de2api/datasetData/enumValueObj"]
        assert "POST" in route_methods["/de2api/datasetData/enumValueDs"]
        assert "POST" in route_methods["/de2api/datasetData/getFieldTree"]
        assert "POST" in route_methods["/de2api/datasetData/innerExportDataSetDetails"]

    def test_chart_field_methods(self, route_methods: dict[str, set[str]]) -> None:
        assert "POST" in route_methods["/de2api/chart/listByDQ/{dataset_group_id}/{chart_id}"]
        assert "POST" in route_methods["/de2api/chart/copyField/{field_id}/{chart_id}"]
        assert "POST" in route_methods["/de2api/chart/deleteField/{field_id}"]
        assert "POST" in route_methods["/de2api/chart/deleteFieldByChart/{chart_id}"]

    def test_chart_data_methods(self, route_methods: dict[str, set[str]]) -> None:
        assert "POST" in route_methods["/de2api/chartData/getFieldData/{field_id}/{field_type}"]
        assert "POST" in route_methods["/de2api/chartData/getDrillFieldData/{field_id}"]
        assert "GET" in route_methods["/de2api/chart/checkSameDataSet/{source_view_id}/{target_view_id}"]


class TestDatasetDataAuthRequired:
    """Verify dataset data routes require authentication."""

    @pytest.mark.asyncio
    async def test_preview_data_requires_auth(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/de2api/datasetData/previewData", json={"datasetGroupId": 1})
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_enum_value_requires_auth(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/de2api/datasetData/enumValue", json={"datasetGroupId": 1})
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_get_field_tree_requires_auth(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/de2api/datasetData/getFieldTree", json={"id": 1})
        assert resp.status_code in (401, 403)


class TestChartFieldAuthRequired:
    """Verify chart field routes require authentication."""

    @pytest.mark.asyncio
    async def test_list_by_dq_requires_auth(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/de2api/chart/listByDQ/1/1", json={})
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_copy_field_requires_auth(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/de2api/chart/copyField/1/1", json={})
        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_check_same_dataset_requires_auth(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/de2api/chart/checkSameDataSet/1/2")
        assert resp.status_code in (401, 403)
