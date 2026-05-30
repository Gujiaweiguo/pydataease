"""Tests for the auth provider feature: contract, mock provider, registry, and service logic.

Pure unit tests — no database, no httpx, no external services.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.services.auth_provider import get_provider_class, list_provider_types, register_provider
from app.services.auth_provider.base import AuthResult, BaseAuthProvider, ProviderClaim
from app.services.auth_provider.mock_provider import MockAuthProvider
from app.services.auth_provider_service import AuthProviderService


# ---------------------------------------------------------------------------
# Group 1: Provider dataclass contract
# ---------------------------------------------------------------------------


def test_provider_claim_fields() -> None:
    """T1: ProviderClaim dataclass has expected fields."""
    claim = ProviderClaim(external_id="x", username="u", email="e@x.com")
    assert claim.external_id == "x"
    assert claim.username == "u"
    assert claim.email == "e@x.com"
    assert claim.groups == []
    assert claim.raw_claims is None


def test_auth_result_success() -> None:
    """T2: AuthResult success with claims."""
    claim = ProviderClaim(external_id="mock:test")
    result = AuthResult(success=True, claims=claim)
    assert result.success
    assert result.claims.external_id == "mock:test"
    assert result.error is None


def test_auth_result_failure() -> None:
    """T3: AuthResult failure."""
    result = AuthResult(success=False, error="bad credentials")
    assert not result.success
    assert result.claims is None
    assert result.error == "bad credentials"


def test_base_provider_is_abstract() -> None:
    """T4: BaseAuthProvider cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseAuthProvider()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# Group 2: Mock provider behavior
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mock_provider_authenticate_success() -> None:
    """T5: Mock provider authenticates with any username."""
    provider = MockAuthProvider()
    result = await provider.authenticate({"username": "testuser", "password": "anything"})
    assert result.success
    assert result.claims.external_id == "mock:testuser"
    assert result.claims.username == "testuser"
    assert result.claims.email == "testuser@mock.local"
    assert "mock-users" in result.claims.groups


@pytest.mark.asyncio
async def test_mock_provider_rejects_empty_username() -> None:
    """T6: Mock provider rejects empty username."""
    provider = MockAuthProvider()
    result = await provider.authenticate({"username": "", "password": "x"})
    assert not result.success
    assert "required" in result.error.lower()


@pytest.mark.asyncio
async def test_mock_provider_no_redirect() -> None:
    """T7: Mock provider get_authorize_url returns None."""
    provider = MockAuthProvider()
    url = await provider.get_authorize_url("http://callback", "state123")
    assert url is None


@pytest.mark.asyncio
async def test_mock_provider_callback_error() -> None:
    """T8: Mock provider callback returns error."""
    provider = MockAuthProvider()
    result = await provider.handle_callback("code", "state", "http://callback")
    assert not result.success
    assert "callback" in result.error.lower()


def test_mock_provider_config_valid() -> None:
    """T9: Mock provider validate_config always passes."""
    provider = MockAuthProvider()
    errors = provider.validate_config({"anything": True})
    assert errors == []


# ---------------------------------------------------------------------------
# Group 3: Registry
# ---------------------------------------------------------------------------


def test_registry_has_mock() -> None:
    """T10: Registry has mock registered."""
    cls = get_provider_class("mock")
    assert cls is MockAuthProvider


def test_registry_unknown_type() -> None:
    """T11: Registry returns None for unknown type."""
    cls = get_provider_class("nonexistent")
    assert cls is None


def test_registry_lists_types() -> None:
    """T12: list_provider_types includes mock."""
    types = list_provider_types()
    assert "mock" in types


def test_registry_register_custom() -> None:
    """T13: Register and retrieve a custom provider."""

    class FakeProvider(MockAuthProvider):
        provider_type = "fake"

    register_provider("fake", FakeProvider)
    assert get_provider_class("fake") is FakeProvider
    assert "fake" in list_provider_types()


# ---------------------------------------------------------------------------
# Group 4: Edge cases
# ---------------------------------------------------------------------------


def test_provider_claim_groups_independent() -> None:
    """T14: ProviderClaim groups default_factory creates independent lists."""
    c1 = ProviderClaim(external_id="a")
    c2 = ProviderClaim(external_id="b")
    c1.groups.append("admin")
    assert c2.groups == []  # No shared mutable state


# ---------------------------------------------------------------------------
# Group 5: Service claim mapping (pure function, mocked session)
# ---------------------------------------------------------------------------


def test_claim_mapping_applied() -> None:
    """T15: Claim mapping remaps fields from raw_claims."""
    service = AuthProviderService(AsyncMock())
    claim = ProviderClaim(
        external_id="ldap:jdoe",
        username="jdoe_original",
        email="jdoe@old.com",
        raw_claims={"uid": "jdoe", "mail": "john@new.com", "cn": "John Doe"},
    )
    mapping = {"username": "uid", "email": "mail", "displayName": "cn"}
    result = service._apply_claim_mapping(claim, mapping)
    assert result.username == "jdoe"
    assert result.email == "john@new.com"
    assert result.display_name == "John Doe"


def test_claim_mapping_no_raw() -> None:
    """T16: Claim mapping with missing raw_claims returns unchanged."""
    service = AuthProviderService(AsyncMock())
    claim = ProviderClaim(external_id="x", username="original")
    result = service._apply_claim_mapping(claim, {"username": "uid"})
    assert result.username == "original"
