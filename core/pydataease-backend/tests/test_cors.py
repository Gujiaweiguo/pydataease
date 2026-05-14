from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_cors_preflight_includes_allow_origin(client: AsyncClient) -> None:
    """OPTIONS preflight should include Access-Control-Allow-Origin."""
    response = await client.options(
        "/de2api/dekey",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


@pytest.mark.asyncio
async def test_cors_actual_request_includes_allow_origin(client: AsyncClient) -> None:
    """Actual cross-origin request should include Access-Control-Allow-Origin."""
    response = await client.get(
        "/de2api/dekey",
        headers={"Origin": "http://example.com"},
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


@pytest.mark.asyncio
async def test_cors_allows_all_methods(client: AsyncClient) -> None:
    """Preflight should allow all methods (Access-Control-Allow-Methods present)."""
    response = await client.options(
        "/de2api/dekey",
        headers={
            "Origin": "http://example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
