from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.core.limiter import limiter


@pytest.fixture(autouse=True)
def _reset_rate_limiter(monkeypatch):
    """Reset in-memory rate limit storage and bypass RSA decryption for rate limit tests."""
    limiter.reset()
    monkeypatch.setattr("app.services.auth_service.decrypt_rsa", lambda x: x)
    yield
    limiter.reset()


@pytest.mark.asyncio
async def test_login_rate_limit_returns_429_after_5_attempts(client: AsyncClient) -> None:
    """Six rapid login requests should trigger a 429 on the 6th."""
    body = {"name": "admin", "pwd": "wrong", "origin": 0}
    for i in range(5):
        response = await client.post("/de2api/login/localLogin", json=body)
        assert response.status_code != 429, f"Request {i + 1} was rate-limited prematurely"

    response = await client.post("/de2api/login/localLogin", json=body)
    assert response.status_code == 429


@pytest.mark.asyncio
async def test_non_login_endpoints_are_not_rate_limited(client: AsyncClient) -> None:
    """Endpoints without @limiter.limit are not rate limited."""
    for _ in range(10):
        response = await client.get("/de2api/dekey")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_limiter_is_configured_on_app() -> None:
    """Verify the limiter is attached to app.state."""
    from app.main import app

    assert hasattr(app.state, "limiter")
    assert app.state.limiter is limiter
