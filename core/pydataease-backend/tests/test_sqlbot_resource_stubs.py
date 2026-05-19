"""Tests for the SQLBot and Resource stub endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


@pytest.mark.asyncio
async def test_sqlbot_datasource_list(client: AsyncClient) -> None:
    token = _build_token(uid=1, oid=1)
    response = await client.get(
        "/de2api/sqlbot/datasource",
        headers={"X-DE-TOKEN": token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"] == []


@pytest.mark.asyncio
async def test_sqlbot_datasource_list_with_params(client: AsyncClient) -> None:
    token = _build_token(uid=1, oid=1)
    response = await client.get(
        "/de2api/sqlbot/datasource",
        params={"dsId": "123", "tableId": "456"},
        headers={"X-DE-TOKEN": token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"] == []


@pytest.mark.asyncio
async def test_sqlbot_dataset_list(client: AsyncClient) -> None:
    token = _build_token(uid=1, oid=1)
    response = await client.get(
        "/de2api/sqlbot/dataset/some-dv-info",
        headers={"X-DE-TOKEN": token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"] == []


@pytest.mark.asyncio
async def test_resource_check_permission(client: AsyncClient) -> None:
    token = _build_token(uid=1, oid=1)
    response = await client.post(
        "/de2api/resource/checkPermission/999",
        headers={"X-DE-TOKEN": token},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"] is True
