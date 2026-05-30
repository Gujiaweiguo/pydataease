"""Tests for the embed control plane (model, service, routes)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# 1. Model field presence
# ---------------------------------------------------------------------------


def test_embed_config_model_fields():
    """EmbedConfig model has all expected columns."""
    from app.models.embed_config import EmbedConfig

    expected = {
        "id",
        "resource_type",
        "embed_enabled",
        "allowed_domains",
        "password_required",
        "ticket_required",
        "max_expiry_hours",
        "extra_config",
        "create_time",
        "update_time",
    }
    actual = {c.name for c in EmbedConfig.__table__.columns}
    assert expected == actual


# ---------------------------------------------------------------------------
# 2. Valid resource types
# ---------------------------------------------------------------------------


def test_valid_resource_types():
    from app.services.embed_control_service import VALID_RESOURCE_TYPES

    assert "dashboard" in VALID_RESOURCE_TYPES
    assert "chart" in VALID_RESOURCE_TYPES
    assert "datav" in VALID_RESOURCE_TYPES
    assert "dataFiling" in VALID_RESOURCE_TYPES
    assert len(VALID_RESOURCE_TYPES) == 4


# ---------------------------------------------------------------------------
# 3. update_config returns error when feature disabled
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_config_feature_disabled():
    from app.services.embed_control_service import EmbedControlService

    session = MagicMock()
    service = EmbedControlService(session)

    with patch(
        "app.services.embed_control_service.is_feature_enabled",
        new_callable=AsyncMock,
        return_value=False,
    ):
        result = await service.update_config("dashboard", {"embedEnabled": True})
        assert isinstance(result, str)
        assert "disabled" in result.lower()


# ---------------------------------------------------------------------------
# 4. is_embed_allowed defaults to false for unknown type
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_is_embed_allowed_default_false():
    from app.services.embed_control_service import EmbedControlService

    session = MagicMock()
    repo = MagicMock()
    repo.get_by_resource_type = AsyncMock(return_value=None)
    service = EmbedControlService(session)
    service.repo = repo

    with patch(
        "app.services.embed_control_service.is_feature_enabled",
        new_callable=AsyncMock,
        return_value=True,
    ):
        result = await service.is_embed_allowed("dashboard")
        assert result is False


# ---------------------------------------------------------------------------
# 5. is_embed_allowed returns True when enabled
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_is_embed_allowed_enabled():
    from app.services.embed_control_service import EmbedControlService

    session = MagicMock()
    config = MagicMock()
    config.embed_enabled = True
    config.allowed_domains = []
    repo = MagicMock()
    repo.get_by_resource_type = AsyncMock(return_value=config)
    service = EmbedControlService(session)
    service.repo = repo

    with patch(
        "app.services.embed_control_service.is_feature_enabled",
        new_callable=AsyncMock,
        return_value=True,
    ):
        result = await service.is_embed_allowed("chart")
        assert result is True


# ---------------------------------------------------------------------------
# 6. Domain validation: empty list allows all
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_domain_validation_empty_allows_all():
    from app.services.embed_control_service import EmbedControlService

    session = MagicMock()
    config = MagicMock()
    config.embed_enabled = True
    config.allowed_domains = []
    repo = MagicMock()
    repo.get_by_resource_type = AsyncMock(return_value=config)
    service = EmbedControlService(session)
    service.repo = repo

    with patch(
        "app.services.embed_control_service.is_feature_enabled",
        new_callable=AsyncMock,
        return_value=True,
    ):
        result = await service.is_embed_allowed("dashboard", domain="evil.com")
        assert result is True


# ---------------------------------------------------------------------------
# 7. Domain validation: specific whitelist
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_domain_validation_specific():
    from app.services.embed_control_service import EmbedControlService

    session = MagicMock()
    config = MagicMock()
    config.embed_enabled = True
    config.allowed_domains = ["trusted.com", "example.org"]
    repo = MagicMock()
    repo.get_by_resource_type = AsyncMock(return_value=config)
    service = EmbedControlService(session)
    service.repo = repo

    with patch(
        "app.services.embed_control_service.is_feature_enabled",
        new_callable=AsyncMock,
        return_value=True,
    ):
        assert await service.is_embed_allowed("dashboard", domain="trusted.com") is True
        assert await service.is_embed_allowed("dashboard", domain="evil.com") is False


# ---------------------------------------------------------------------------
# 8. Admin routes require auth
# ---------------------------------------------------------------------------


def test_admin_routes_require_auth():
    """Admin embed-control routes return 401/403 without auth token."""
    from app.main import app

    client = TestClient(app, raise_server_exceptions=False)

    # List endpoint — admin only
    resp = client.get("/de2api/embed-control/list")
    assert resp.status_code in (401, 403)

    # Get single config — admin only
    resp = client.get("/de2api/embed-control/dashboard")
    assert resp.status_code in (401, 403)

    # Update — admin only
    resp = client.put("/de2api/embed-control/dashboard", json={"embedEnabled": True})
    assert resp.status_code in (401, 403)

    # Check endpoint is public — should NOT return 401/403
    resp = client.get("/de2api/embed-control/dashboard/check")
    # May return 200 (public) or 500 (no DB), but not auth error
    assert resp.status_code not in (401, 403)
