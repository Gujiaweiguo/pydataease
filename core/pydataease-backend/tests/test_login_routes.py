from __future__ import annotations

from datetime import UTC, datetime

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from fastapi import APIRouter, Depends, Request
from httpx import AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.main import app
from app.settings.config import get_settings
from app.utils.password_utils import derive_jwt_secret


def _ensure_test_routes() -> None:
    existing_paths = {path for route in app.routes if (path := getattr(route, "path", None)) is not None}
    if "/de2api/protected/me" in existing_paths:
        return

    async def _protected_me(request: Request, session: AsyncSession = Depends(get_db)) -> dict[str, int]:
        user = await get_current_user(request, session)
        return {"user_id": user.user_id, "oid": user.oid}

    router = APIRouter(prefix=get_settings().api_prefix)
    router.add_api_route("/protected/me", _protected_me, methods=["GET"])
    app.include_router(router)


def _encrypt(value: str, public_key_pem: str) -> str:
    public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    ciphertext = public_key.encrypt(
        value.encode("utf-8"),
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )
    return __import__("base64").b64encode(ciphertext).decode("utf-8")


_ensure_test_routes()


@pytest.mark.asyncio
async def test_dekey_returns_public_key(client: AsyncClient) -> None:
    response = await client.get("/de2api/dekey")

    assert response.status_code == 200
    assert "BEGIN PUBLIC KEY" in response.json()["data"]


@pytest.mark.asyncio
async def test_login_with_correct_credentials_returns_token(client: AsyncClient) -> None:
    public_key = (await client.get("/de2api/dekey")).json()["data"]
    response = await client.post(
        "/de2api/login/localLogin",
        json={
            "name": _encrypt("admin", public_key),
            "pwd": _encrypt("DataEase@123456", public_key),
            "origin": 0,
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data["token"], str)
    assert data["exp"] > int(datetime.now(UTC).timestamp() * 1000)


@pytest.mark.asyncio
async def test_login_with_wrong_password_returns_401(client: AsyncClient) -> None:
    public_key = (await client.get("/de2api/dekey")).json()["data"]
    response = await client.post(
        "/de2api/login/localLogin",
        json={"name": _encrypt("admin", public_key), "pwd": _encrypt("wrong", public_key), "origin": 0},
    )

    assert response.status_code == 401
    assert response.json()["code"] == 401


@pytest.mark.asyncio
async def test_login_with_disabled_user_returns_401(client: AsyncClient, fake_auth_users) -> None:
    fake_auth_users[1].enable = False
    public_key = (await client.get("/de2api/dekey")).json()["data"]
    response = await client.post(
        "/de2api/login/localLogin",
        json={"name": _encrypt("admin", public_key), "pwd": _encrypt("DataEase@123456", public_key), "origin": 0},
    )

    assert response.status_code == 401
    assert response.json()["code"] == 401


@pytest.mark.asyncio
async def test_login_with_nonexistent_user_returns_401(client: AsyncClient) -> None:
    public_key = (await client.get("/de2api/dekey")).json()["data"]
    response = await client.post(
        "/de2api/login/localLogin",
        json={"name": _encrypt("missing", public_key), "pwd": _encrypt("DataEase@123456", public_key), "origin": 0},
    )

    assert response.status_code == 401
    assert response.json()["code"] == 401


@pytest.mark.asyncio
async def test_refresh_with_valid_token_returns_new_token(client: AsyncClient, fake_auth_users) -> None:
    settings = get_settings()
    user = fake_auth_users[1]
    token = jwt.encode(
        {"uid": user.id, "oid": user.oid, "exp": int(datetime.now(UTC).timestamp()) + 60},
        derive_jwt_secret(user.password),
        algorithm=settings.jwt_algorithm,
    )

    response = await client.get("/de2api/login/refresh", headers={"X-DE-TOKEN": token})

    assert response.status_code == 200
    assert response.json()["data"]["token"] != ""


@pytest.mark.asyncio
async def test_refresh_without_token_returns_401(client: AsyncClient) -> None:
    response = await client.get("/de2api/login/refresh")

    assert response.status_code == 401
    assert response.json()["code"] == 401


@pytest.mark.asyncio
async def test_logout_returns_success(client: AsyncClient, fake_auth_users) -> None:
    settings = get_settings()
    user = fake_auth_users[1]
    token = jwt.encode(
        {"uid": user.id, "oid": user.oid, "exp": int(datetime.now(UTC).timestamp()) + 60},
        derive_jwt_secret(user.password),
        algorithm=settings.jwt_algorithm,
    )

    response = await client.get("/de2api/logout", headers={"X-DE-TOKEN": token})

    assert response.status_code == 200
    assert response.json() == {"code": 0, "data": None, "msg": "success"}


@pytest.mark.asyncio
async def test_protected_route_with_valid_token_works(client: AsyncClient, fake_auth_users) -> None:
    settings = get_settings()
    user = fake_auth_users[1]
    token = jwt.encode(
        {"uid": user.id, "oid": user.oid, "exp": int(datetime.now(UTC).timestamp()) + 60},
        derive_jwt_secret(user.password),
        algorithm=settings.jwt_algorithm,
    )

    response = await client.get("/de2api/protected/me", headers={"X-DE-TOKEN": token})

    assert response.status_code == 200
    assert response.json() == {"code": 0, "data": {"user_id": 1, "oid": 1}, "msg": "success"}
