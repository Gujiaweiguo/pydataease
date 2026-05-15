from __future__ import annotations

from collections.abc import AsyncGenerator, Callable, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt

from app.main import app
from app.settings.config import BaseConfig, get_settings
from app.utils.password_utils import derive_jwt_secret


def _build_token(secret: str, algorithm: str, **claims: int) -> str:
    return jwt.encode({**claims, "exp": 9999999999}, secret, algorithm=algorithm)


@pytest.fixture(autouse=True)
def _patch_direct_get_current_user(monkeypatch, fake_auth_users) -> Generator[None, None, None]:
    import tests.contracts.test_auth_contract as auth_test
    from typing import cast
    from fastapi import HTTPException, status
    from app.schemas.auth import TokenUser

    users = fake_auth_users

    async def _fake_get_current_user(request, session=None):
        user = cast(TokenUser | None, getattr(request.state, "user", None))
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        db_user = users.get(user.user_id)
        if db_user is None or not db_user.enable:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is disabled")
        return TokenUser(user_id=db_user.id, oid=db_user.oid or 0, language=db_user.language or "zh-CN")

    monkeypatch.setattr(auth_test, "get_current_user", _fake_get_current_user)
    yield


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Generator[None, None, None]:
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
def auth_headers(settings: BaseConfig, fake_auth_users) -> dict[str, str]:
    user = fake_auth_users[1]
    token = _build_token(derive_jwt_secret(user.password), settings.jwt_algorithm, uid=1, oid=1)
    return {"X-DE-TOKEN": token}


@pytest.fixture
def invalid_auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": "invalid-token"}


@pytest.fixture
def share_headers(settings: BaseConfig) -> dict[str, str]:
    token = _build_token(settings.share_secret_key, settings.jwt_algorithm, uid=1, oid=1, resourceId=101)
    return {"X-DE-LINK-TOKEN": token}


@pytest.fixture
def embedded_auth_headers(settings: BaseConfig, fake_auth_users) -> dict[str, str]:
    user = fake_auth_users[2]
    token = _build_token(derive_jwt_secret(user.password), settings.jwt_algorithm, uid=2, oid=3)
    return {"X-EMBEDDED-TOKEN": token}


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
