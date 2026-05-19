from __future__ import annotations

# pyright: reportMissingTypeArgument=false, reportAttributeAccessIssue=false

import pytest
from httpx import AsyncClient

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.services.log_service import get_log_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.api_key_service import get_api_key_service  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


# ---------------------------------------------------------------------------
# Fake services
# ---------------------------------------------------------------------------


class FakeLogService:
    def __init__(self) -> None:
        self.last_pager_request = None

    async def pager(self, page: int, page_size: int, request: object) -> dict:
        self.last_pager_request = request
        return {
            "pager": {
                "totalItem": 0,
                "pageSize": page_size,
                "totalPage": 0,
                "currentPage": page,
            },
            "data": [],
        }

    async def export_logs(self, request: object) -> None:
        pass

    async def log_options(self) -> list[dict]:
        return [
            {"value": "LOGIN", "label": "登录", "children": []},
            {"value": "CREATE", "label": "创建", "children": []},
        ]


class FakeApiKeyService:
    def __init__(self) -> None:
        self.keys: list[dict] = []

    async def generate(self, user: object) -> dict:
        key = {
            "id": 1001,
            "accessKey": "ak-test-key",
            "accessSecret": "sk-test-secret",
            "enable": True,
            "createTime": 1700000000000,
        }
        self.keys.append({**key, "_creator": user.user_id if hasattr(user, "user_id") else 0})
        return key

    async def query(self, user: object) -> list[dict]:
        uid = user.user_id if hasattr(user, "user_id") else 0
        return [k for k in self.keys if k.get("_creator") == uid]

    async def switch_enable(self, payload: object, user: object) -> None:
        uid = user.user_id if hasattr(user, "user_id") else 0
        key_id = payload.id if hasattr(payload, "id") else 0
        for k in self.keys:
            if k["id"] == key_id:
                if k["_creator"] != uid:
                    from fastapi import HTTPException  # pyright: ignore[reportMissingImports]
                    raise HTTPException(403, "Not your API key")
                k["enable"] = payload.enable if hasattr(payload, "enable") else False

    async def delete_key(self, key_id: int, user: object) -> None:
        uid = user.user_id if hasattr(user, "user_id") else 0
        self.keys = [k for k in self.keys if not (k["id"] == key_id and k["_creator"] == uid)]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_log_service():
    return FakeLogService()


@pytest.fixture
def fake_api_key_service():
    return FakeApiKeyService()


@pytest.fixture(autouse=True)
def override_services(fake_log_service, fake_api_key_service):
    app.dependency_overrides[get_log_service] = lambda: fake_log_service
    app.dependency_overrides[get_api_key_service] = lambda: fake_api_key_service
    yield
    app.dependency_overrides.pop(get_log_service, None)
    app.dependency_overrides.pop(get_api_key_service, None)


def _auth_header(user_id: int = 1, oid: int = 1) -> dict[str, str]:
    token = _build_token(uid=user_id, oid=oid)
    return {"X-DE-TOKEN": token}


# ---------------------------------------------------------------------------
# Log endpoint tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_log_pager_returns_paginated_result(client: AsyncClient, fake_log_service: FakeLogService) -> None:
    resp = await client.post(
        "/de2api/log/pager/1/10",
        json={},
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    data = body["data"]
    assert "pager" in data
    assert "data" in data
    assert data["pager"]["currentPage"] == 1
    assert data["pager"]["pageSize"] == 10


@pytest.mark.anyio
async def test_log_pager_with_keyword(client: AsyncClient, fake_log_service: FakeLogService) -> None:
    resp = await client.post(
        "/de2api/log/pager/1/20",
        json={"keyword": "login"},
        headers=_auth_header(),
    )
    assert resp.status_code == 200
    assert fake_log_service.last_pager_request is not None


@pytest.mark.anyio
async def test_log_options_returns_tree(client: AsyncClient) -> None:
    resp = await client.get("/de2api/log/options", headers=_auth_header())
    assert resp.status_code == 200
    body = resp.json()
    data = body["data"]
    assert isinstance(data, list)
    assert any(item["value"] == "LOGIN" for item in data)


@pytest.mark.anyio
async def test_log_export_returns_none(client: AsyncClient) -> None:
    resp = await client.post(
        "/de2api/log/export",
        json={},
        headers=_auth_header(),
    )
    assert resp.status_code == 200


@pytest.mark.anyio
async def test_log_pager_requires_auth(client: AsyncClient) -> None:
    resp = await client.post("/de2api/log/pager/1/10", json={})
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_log_options_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/de2api/log/options")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# ApiKey endpoint tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_apikey_generate(client: AsyncClient, fake_api_key_service: FakeApiKeyService) -> None:
    resp = await client.post("/de2api/apiKey/generate", headers=_auth_header())
    assert resp.status_code == 200
    body = resp.json()
    data = body["data"]
    assert "accessKey" in data
    assert "accessSecret" in data
    assert data["enable"] is True


@pytest.mark.anyio
async def test_apikey_query(client: AsyncClient, fake_api_key_service: FakeApiKeyService) -> None:
    # Generate first
    await client.post("/de2api/apiKey/generate", headers=_auth_header())
    # Then query
    resp = await client.get("/de2api/apiKey/query", headers=_auth_header())
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 1


@pytest.mark.anyio
async def test_apikey_switch(client: AsyncClient, fake_api_key_service: FakeApiKeyService) -> None:
    # Generate first
    gen_resp = await client.post("/de2api/apiKey/generate", headers=_auth_header())
    key_id = gen_resp.json()["data"]["id"]
    # Switch disable
    resp = await client.post(
        "/de2api/apiKey/switch",
        json={"id": key_id, "enable": False},
        headers=_auth_header(),
    )
    assert resp.status_code == 200


@pytest.mark.anyio
async def test_apikey_delete(client: AsyncClient, fake_api_key_service: FakeApiKeyService) -> None:
    # Generate first
    gen_resp = await client.post("/de2api/apiKey/generate", headers=_auth_header())
    key_id = gen_resp.json()["data"]["id"]
    # Delete
    resp = await client.post(
        f"/de2api/apiKey/delete/{key_id}",
        headers=_auth_header(),
    )
    assert resp.status_code == 200


@pytest.mark.anyio
async def test_apikey_generate_requires_auth(client: AsyncClient) -> None:
    resp = await client.post("/de2api/apiKey/generate")
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_apikey_query_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/de2api/apiKey/query")
    assert resp.status_code == 401
