from __future__ import annotations

import pytest
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.main import app
from app.settings.config import get_settings


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
    @pytest.mark.skip(reason="Endpoint not yet implemented")
    async def test_local_login_success_contract(self) -> None:
        """POST /de2api/login/localLogin should accept credential body and return ResultMessage with TokenVO data on success; no auth header required."""

    @pytest.mark.skip(reason="Endpoint not yet implemented")
    async def test_local_login_auth_failure_contract(self) -> None:
        """POST /de2api/login/localLogin should reject invalid credentials with non-zero ResultMessage.code and error msg."""

    @pytest.mark.skip(reason="Endpoint not yet implemented")
    async def test_refresh_success_contract(self) -> None:
        """GET /de2api/login/refresh should require X-DE-TOKEN and return refreshed TokenVO in ResultMessage.data."""

    @pytest.mark.skip(reason="Endpoint not yet implemented")
    async def test_refresh_missing_token_contract(self) -> None:
        """GET /de2api/login/refresh should fail when X-DE-TOKEN is missing, invalid, or expired."""

    @pytest.mark.skip(reason="Endpoint not yet implemented")
    async def test_logout_success_contract(self) -> None:
        """GET /de2api/logout should require X-DE-TOKEN and return success ResultMessage with empty data on logout."""

    @pytest.mark.skip(reason="Endpoint not yet implemented")
    async def test_logout_missing_token_contract(self) -> None:
        """GET /de2api/logout should fail when X-DE-TOKEN is missing, invalid, or expired."""


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
