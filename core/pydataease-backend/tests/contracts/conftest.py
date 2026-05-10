from __future__ import annotations

from collections.abc import AsyncGenerator, Callable, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt

from app.main import app
from app.settings.config import BaseConfig, get_settings


def _build_token(secret: str, algorithm: str, **claims: int) -> str:
    return jwt.encode({**claims, "exp": 9999999999}, secret, algorithm=algorithm)


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Generator[None, None, None]:
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def install_override() -> Callable[[Callable[..., object], object], None]:
    def _install(provider: Callable[..., object], service: object) -> None:
        app.dependency_overrides[provider] = lambda: service

    return _install


@pytest.fixture
def settings() -> BaseConfig:
    return get_settings()


@pytest.fixture
def api_prefix() -> str:
    return "/de2api"


@pytest.fixture
def auth_headers(settings: BaseConfig) -> dict[str, str]:
    token = _build_token(settings.secret_key, settings.jwt_algorithm, uid=1, oid=1)
    return {"X-DE-TOKEN": token}


@pytest.fixture
def invalid_auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": "invalid-token"}


@pytest.fixture
def share_headers(settings: BaseConfig) -> dict[str, str]:
    token = _build_token(settings.share_secret_key, settings.jwt_algorithm, uid=1, oid=1, resourceId=101)
    return {"X-DE-LINK-TOKEN": token}


@pytest.fixture
def embedded_auth_headers(settings: BaseConfig) -> dict[str, str]:
    token = _build_token(settings.secret_key, settings.jwt_algorithm, uid=2, oid=3)
    return {"X-EMBEDDED-TOKEN": token}


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
