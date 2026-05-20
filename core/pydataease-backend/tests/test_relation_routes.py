"""Tests for relation/lineage routes."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]


@pytest.fixture
def route_paths() -> set[str]:
    return {getattr(route, "path", "") for route in app.routes}


class TestRelationRoutes:
    def test_relation_datasource_route(self, route_paths: set[str]) -> None:
        assert "/de2api/relation/datasource/{datasource_id}" in route_paths

    def test_relation_dataset_route(self, route_paths: set[str]) -> None:
        assert "/de2api/relation/dataset/{dataset_group_id}" in route_paths

    def test_relation_dv_route(self, route_paths: set[str]) -> None:
        assert "/de2api/relation/dv/{dv_id}" in route_paths


class TestRelationAuth:
    @pytest.mark.asyncio
    async def test_relation_datasource_requires_auth(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/de2api/relation/datasource/1")
        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_relation_dataset_requires_auth(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/de2api/relation/dataset/1")
        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_relation_dv_requires_auth(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/de2api/relation/dv/1")
        assert response.status_code in (401, 403)
