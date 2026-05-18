from __future__ import annotations

# pyright: reportMissingTypeArgument=false

import pytest
from httpx import AsyncClient

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.services.watermark_service import get_watermark_service  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


def _auth_header(user_id: int = 1, oid: int = 1) -> dict[str, str]:
    token = _build_token(uid=user_id, oid=oid)
    return {"X-DE-TOKEN": token}


# ---------------------------------------------------------------------------
# Fake service
# ---------------------------------------------------------------------------


class FakeWatermarkService:
    def __init__(self) -> None:
        self._watermark: dict | None = None

    async def get_watermark_info(self) -> dict | None:
        return self._watermark

    async def save_watermark_info(self, payload) -> None:
        self._watermark = {
            "id": "system_default",
            "version": payload.version,
            "settingContent": payload.setting_content,
            "createBy": None,
            "createTime": None,
        }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def fake_watermark_service():
    return FakeWatermarkService()


@pytest.fixture(autouse=True)
def override_services(fake_watermark_service):
    app.dependency_overrides[get_watermark_service] = lambda: fake_watermark_service
    yield
    app.dependency_overrides.pop(get_watermark_service, None)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_get_watermark_info_empty(client: AsyncClient) -> None:
    """GET /watermark/find returns null when no config exists."""
    resp = await client.get("/de2api/watermark/find", headers=_auth_header())
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    assert body["data"] is None


@pytest.mark.anyio
async def test_save_and_get_watermark(
    client: AsyncClient, fake_watermark_service: FakeWatermarkService
) -> None:
    """POST /watermark/save persists, then GET returns the saved data."""
    save_resp = await client.post(
        "/de2api/watermark/save",
        json={"version": "1.0", "settingContent": '{"opacity": 0.3}'},
        headers=_auth_header(),
    )
    assert save_resp.status_code == 200
    assert save_resp.json()["data"] is None  # void endpoint

    get_resp = await client.get("/de2api/watermark/find", headers=_auth_header())
    assert get_resp.status_code == 200
    data = get_resp.json()["data"]
    assert data is not None
    assert data["version"] == "1.0"
    assert data["settingContent"] == '{"opacity": 0.3}'


@pytest.mark.anyio
async def test_save_watermark_requires_auth(client: AsyncClient) -> None:
    """POST /watermark/save requires authentication."""
    resp = await client.post(
        "/de2api/watermark/save",
        json={"version": "1.0"},
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_get_watermark_requires_auth(client: AsyncClient) -> None:
    """GET /watermark/find requires authentication (not whitelisted)."""
    resp = await client.get("/de2api/watermark/find")
    assert resp.status_code == 401
