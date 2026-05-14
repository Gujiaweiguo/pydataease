from __future__ import annotations

import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.main import app
from app.settings.config import get_settings


def _extract_public_key_pem(dekey: str) -> str:
    """Parse Java-compatible dekey format back to PEM public key."""
    separator = base64.urlsafe_b64encode(b"-pk_separator-").decode("utf-8")
    k1, k2 = dekey.split(separator)
    ct = base64.b64decode(k1)
    cipher = Cipher(algorithms.AES(k2.encode("utf-8")), modes.CBC(b"0000000000000000"))
    decryptor = cipher.decryptor()
    padded = decryptor.update(ct) + decryptor.finalize()
    unpadder = sym_padding.PKCS7(128).unpadder()
    plaintext = (unpadder.update(padded) + unpadder.finalize()).decode("utf-8")
    # The dekey response now contains a PEM-formatted public key (for JSEncrypt compat).
    if plaintext.startswith("-----BEGIN PUBLIC KEY-----"):
        return plaintext
    der_bytes = base64.b64decode(plaintext)
    pub = serialization.load_der_public_key(der_bytes)
    pem_bytes = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem_bytes.decode("utf-8")


def _encrypt(value: str, dekey: str) -> str:
    public_key_pem = _extract_public_key_pem(dekey)
    public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    ciphertext = public_key.encrypt(
        value.encode("utf-8"),
        asym_padding.PKCS1v15(),
    )
    return base64.b64encode(ciphertext).decode("utf-8")


def _ensure_test_routes() -> None:
    existing_paths = {path for route in app.routes if (path := getattr(route, "path", None)) is not None}
    if "/de2api/protected/me" in existing_paths:
        return

    async def _protected_me(request: Request, session: AsyncSession = Depends(get_db)) -> dict[str, int]:
        user = await get_current_user(request, session)
        return {"user_id": user.user_id, "oid": user.oid}

    async def _share_view(request: Request, session: AsyncSession = Depends(get_db)) -> dict[str, int]:
        user = await get_current_user(request, session)
        return {"user_id": user.user_id, "oid": user.oid}

    router = APIRouter(prefix=get_settings().api_prefix)
    router.add_api_route("/protected/me", _protected_me, methods=["GET"])
    router.add_api_route("/share/view", _share_view, methods=["GET"])
    app.include_router(router)


_ensure_test_routes()


class TestLoginContract:
    async def test_local_login_success_contract(self, async_client, settings) -> None:
        """POST /de2api/login/localLogin should accept credential body and return ResultMessage with TokenVO data on success; no auth header required."""
        dekey_resp = await async_client.get("/de2api/dekey")
        assert dekey_resp.status_code == 200
        dekey = dekey_resp.json()["data"]

        encrypted_name = _encrypt("admin", dekey)
        encrypted_pwd = _encrypt("DataEase@123456", dekey)

        response = await async_client.post(
            "/de2api/login/localLogin",
            json={"name": encrypted_name, "pwd": encrypted_pwd, "origin": 0},
        )
        body = response.json()
        assert response.status_code == 200
        assert body["code"] == 0
        assert isinstance(body["data"]["token"], str) and len(body["data"]["token"]) > 0

    async def test_local_login_auth_failure_contract(self, async_client, settings) -> None:
        """POST /de2api/login/localLogin should reject invalid credentials with non-zero ResultMessage.code and error msg."""
        dekey_resp = await async_client.get("/de2api/dekey")
        assert dekey_resp.status_code == 200
        dekey = dekey_resp.json()["data"]

        encrypted_name = _encrypt("admin", dekey)
        encrypted_pwd = _encrypt("wrong_password", dekey)

        response = await async_client.post(
            "/de2api/login/localLogin",
            json={"name": encrypted_name, "pwd": encrypted_pwd, "origin": 0},
        )
        body = response.json()
        assert body["code"] == 401

    async def test_refresh_success_contract(self, async_client, auth_headers) -> None:
        """GET /de2api/login/refresh should require X-DE-TOKEN and return refreshed TokenVO in ResultMessage.data."""
        response = await async_client.get("/de2api/login/refresh", headers=auth_headers)
        body = response.json()
        assert response.status_code == 200
        assert body["code"] == 0
        assert isinstance(body["data"]["token"], str) and len(body["data"]["token"]) > 0

    async def test_refresh_missing_token_contract(self, async_client, invalid_auth_headers) -> None:
        """GET /de2api/login/refresh should fail when X-DE-TOKEN is missing, invalid, or expired."""
        response = await async_client.get("/de2api/login/refresh", headers=invalid_auth_headers)
        assert response.status_code == 401

    async def test_logout_success_contract(self, async_client, auth_headers) -> None:
        """GET /de2api/logout should require X-DE-TOKEN and return success ResultMessage with empty data on logout."""
        response = await async_client.get("/de2api/logout", headers=auth_headers)
        body = response.json()
        assert response.status_code == 200
        assert body["code"] == 0

    async def test_logout_missing_token_contract(self, async_client, invalid_auth_headers) -> None:
        """GET /de2api/logout should fail when X-DE-TOKEN is missing, invalid, or expired."""
        response = await async_client.get("/de2api/logout", headers=invalid_auth_headers)
        assert response.status_code == 401


class TestTokenSemanticsContract:
    async def test_share_token_header_contract(self, async_client, share_headers) -> None:
        """Protected share routes should accept X-DE-LINK-TOKEN as alternate auth header and resolve uid/oid/resourceId from JWT claims."""
        response = await async_client.get("/de2api/share/view", headers=share_headers)

        assert response.status_code == 200
        assert response.json() == {"code": 0, "data": {"user_id": 1, "oid": 1}, "msg": "success"}

    async def test_embedded_token_header_contract(self, async_client, embedded_auth_headers) -> None:
        """Embedded requests should support X-EMBEDDED-TOKEN header where frontend injects embedded session tokens."""
        response = await async_client.get("/de2api/protected/me", headers=embedded_auth_headers)

        assert response.status_code == 200
        assert response.json() == {"code": 0, "data": {"user_id": 2, "oid": 3}, "msg": "success"}
