"""Tests for OIDC, CAS, LDAP providers and user provisioning service.

Pure unit tests — no database, no external HTTP services.
"""

from __future__ import annotations


import pytest

from app.services.auth_provider import get_provider_class, list_provider_types
from app.services.auth_provider.oidc_provider import OIDCAuthProvider
from app.services.auth_provider.cas_provider import CASAuthProvider
from app.services.auth_provider.ldap_provider import LDAPAuthProvider
from app.services.auth_provider.mock_provider import MockAuthProvider


# ---------------------------------------------------------------------------
# Group 1: Provider registration
# ---------------------------------------------------------------------------


def test_registry_has_oidc() -> None:
    assert get_provider_class("oidc") is OIDCAuthProvider


def test_registry_has_cas() -> None:
    assert get_provider_class("cas") is CASAuthProvider


def test_registry_has_ldap() -> None:
    assert get_provider_class("ldap") is LDAPAuthProvider


def test_registry_lists_all_four() -> None:
    types = list_provider_types()
    assert {"cas", "ldap", "mock", "oidc"}.issubset(set(types))


# ---------------------------------------------------------------------------
# Group 2: OIDC provider
# ---------------------------------------------------------------------------


def test_oidc_config_validation_empty() -> None:
    p = OIDCAuthProvider({})
    errors = p.validate_config({})
    assert len(errors) == 3
    assert any("issuer_url" in e for e in errors)
    assert any("client_id" in e for e in errors)
    assert any("client_secret" in e for e in errors)


def test_oidc_config_validation_valid() -> None:
    config = {"issuer_url": "https://accounts.google.com", "client_id": "x", "client_secret": "s"}
    p = OIDCAuthProvider(config)
    errors = p.validate_config(config)
    assert errors == []


@pytest.mark.asyncio
async def test_oidc_no_direct_auth() -> None:
    p = OIDCAuthProvider({})
    result = await p.authenticate({"username": "u"})
    assert not result.success
    assert result.error is not None
    assert "direct" in result.error.lower()


@pytest.mark.asyncio
async def test_oidc_authorize_url_with_explicit_endpoint() -> None:
    config = {
        "issuer_url": "https://example.com",
        "client_id": "my-client",
        "client_secret": "secret",
        "authorize_url": "https://example.com/auth",
    }
    p = OIDCAuthProvider(config)
    url = await p.get_authorize_url("http://localhost/callback", "state123")
    assert url is not None
    assert "https://example.com/auth?" in url
    assert "client_id=my-client" in url
    assert "state=state123" in url
    assert "redirect_uri=" in url


# ---------------------------------------------------------------------------
# Group 3: CAS provider
# ---------------------------------------------------------------------------


def test_cas_config_validation_empty() -> None:
    p = CASAuthProvider({})
    errors = p.validate_config({})
    assert len(errors) == 1
    assert "cas_server_url" in errors[0]


def test_cas_config_validation_valid() -> None:
    config = {"cas_server_url": "https://cas.example.com/cas"}
    p = CASAuthProvider(config)
    errors = p.validate_config(config)
    assert errors == []


@pytest.mark.asyncio
async def test_cas_no_direct_auth() -> None:
    p = CASAuthProvider({})
    result = await p.authenticate({"username": "u"})
    assert not result.success
    assert result.error is not None
    assert "direct" in result.error.lower()


@pytest.mark.asyncio
async def test_cas_authorize_url() -> None:
    config = {"cas_server_url": "https://cas.example.com/cas"}
    p = CASAuthProvider(config)
    url = await p.get_authorize_url("http://localhost/callback", "state123")
    assert url is not None
    assert "https://cas.example.com/cas/login?" in url
    assert "service=" in url


def test_cas_parse_success_response() -> None:
    p = CASAuthProvider({})
    xml = """<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
      <cas:authenticationSuccess>
        <cas:user>testuser</cas:user>
        <cas:attributes>
          <cas:mail>test@example.com</cas:mail>
          <cas:displayName>Test User</cas:displayName>
        </cas:attributes>
      </cas:authenticationSuccess>
    </cas:serviceResponse>"""
    success, user, attrs = p._parse_cas_response(xml)
    assert success is True
    assert user == "testuser"
    assert attrs.get("mail") == "test@example.com"
    assert attrs.get("displayName") == "Test User"


def test_cas_parse_failure_response() -> None:
    p = CASAuthProvider({})
    xml = """<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas">
      <cas:authenticationFailure code="INVALID_TICKET">
        Ticket ST-12345 not recognized
      </cas:authenticationFailure>
    </cas:serviceResponse>"""
    success, _user, _attrs = p._parse_cas_response(xml)
    assert success is False


# ---------------------------------------------------------------------------
# Group 4: LDAP provider
# ---------------------------------------------------------------------------


def test_ldap_config_validation_empty() -> None:
    p = LDAPAuthProvider({})
    errors = p.validate_config({})
    assert len(errors) == 2
    assert any("server_url" in e for e in errors)
    assert any("bind_dn" in e for e in errors)


def test_ldap_config_validation_valid() -> None:
    config = {"server_url": "ldap://ldap.example.com", "bind_dn": "uid={username},dc=example,dc=com"}
    p = LDAPAuthProvider(config)
    errors = p.validate_config(config)
    assert errors == []


@pytest.mark.asyncio
async def test_ldap_no_redirect() -> None:
    p = LDAPAuthProvider({})
    url = await p.get_authorize_url("http://callback", "state")
    assert url is None


@pytest.mark.asyncio
async def test_ldap_no_callback() -> None:
    p = LDAPAuthProvider({})
    result = await p.handle_callback("code", "state", "http://callback")
    assert not result.success
    assert result.error is not None
    assert "callback" in result.error.lower()


# ---------------------------------------------------------------------------
# Group 5: Provider constructor accepts config
# ---------------------------------------------------------------------------


def test_provider_constructor_stores_config() -> None:
    config = {"issuer_url": "https://example.com", "client_id": "x", "client_secret": "s"}
    p = OIDCAuthProvider(config)
    assert p.config == config


def test_provider_constructor_empty_config() -> None:
    p = MockAuthProvider()
    assert p.config == {}


def test_provider_constructor_none_config() -> None:
    p = MockAuthProvider(None)
    assert p.config == {}
