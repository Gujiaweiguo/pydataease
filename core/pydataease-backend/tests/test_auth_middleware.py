from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi import APIRouter, Depends, Request
from httpx import AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.main import app
from app.settings.config import get_settings


async def _local_login() -> dict[str, str]:
    return {"token": "ok"}


async def _protected_me(request: Request, session: AsyncSession = Depends(get_db)) -> dict[str, int]:
    user = await get_current_user(request, session)
    return {"user_id": user.user_id, "oid": user.oid}


async def _share_view(request: Request, session: AsyncSession = Depends(get_db)) -> dict[str, int]:
    user = await get_current_user(request, session)
    return {"user_id": user.user_id, "oid": user.oid}


def _ensure_test_routes() -> None:
    existing_paths = {path for route in app.routes if (path := getattr(route, "path", None)) is not None}
    if "/de2api/share/view" in existing_paths:
        return

    router = APIRouter(prefix=get_settings().api_prefix)
    router.add_api_route("/login/localLogin", _local_login, methods=["POST"])
    router.add_api_route("/protected/me", _protected_me, methods=["GET"])
    router.add_api_route("/share/view", _share_view, methods=["GET"])
    app.include_router(router)


def _build_token(secret: str, **claims: int) -> str:
    settings = get_settings()
    payload = {
        **claims,
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }
    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


_ensure_test_routes()


@pytest.mark.asyncio
async def test_whitelist_path_accessible_without_token(client: AsyncClient) -> None:
    response = await client.get("/de2api/dekey")

    assert response.status_code == 200
    assert response.json()["code"] == 0


@pytest.mark.asyncio
async def test_protected_path_without_token_returns_wrapped_401(client: AsyncClient) -> None:
    response = await client.get("/de2api/protected/me")

    assert response.status_code == 401
    assert response.json() == {
        "code": 401,
        "data": None,
        "msg": "token is empty for uri {/de2api/protected/me}",
    }


@pytest.mark.asyncio
async def test_protected_path_with_invalid_token_returns_401(client: AsyncClient) -> None:
    response = await client.get("/de2api/protected/me", headers={"X-DE-TOKEN": "invalid-token"})

    assert response.status_code == 401
    assert response.json() == {"code": 401, "data": None, "msg": "token is invalid"}


@pytest.mark.asyncio
async def test_protected_path_with_valid_token_is_not_rejected_by_auth(client: AsyncClient) -> None:
    settings = get_settings()
    token = _build_token(settings.secret_key, uid=7, oid=9)

    protected = await client.get("/de2api/protected/me", headers={"X-DE-TOKEN": token})
    missing = await client.get("/de2api/does-not-exist", headers={"X-DE-TOKEN": token})

    assert protected.status_code == 200
    assert protected.json() == {
        "code": 0,
        "data": {"user_id": 7, "oid": 9},
        "msg": "success",
    }
    assert missing.status_code == 404
    assert missing.json() == {"code": 404, "data": None, "msg": "Not Found"}


@pytest.mark.asyncio
async def test_share_link_token_is_supported(client: AsyncClient) -> None:
    settings = get_settings()
    token = _build_token(settings.share_secret_key, uid=11, oid=13, resourceId=101)

    response = await client.get("/de2api/share/view", headers={"X-DE-LINK-TOKEN": token})

    assert response.status_code == 200
    assert response.json() == {
        "code": 0,
        "data": {"user_id": 11, "oid": 13},
        "msg": "success",
    }


@pytest.mark.asyncio
async def test_health_endpoint_remains_unwrapped(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
