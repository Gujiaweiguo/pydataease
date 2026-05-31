from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.auth_provider.base import BaseAuthProvider

# Global provider type registry
_PROVIDER_REGISTRY: dict[str, type[BaseAuthProvider]] = {}


def register_provider(provider_type: str, cls: type[BaseAuthProvider]) -> None:
    """Register a provider class under a type key."""
    _PROVIDER_REGISTRY[provider_type] = cls


def get_provider_class(provider_type: str) -> type[BaseAuthProvider] | None:
    """Look up a registered provider class by type."""
    return _PROVIDER_REGISTRY.get(provider_type)


def list_provider_types() -> list[str]:
    """Return all registered provider type keys."""
    return sorted(_PROVIDER_REGISTRY.keys())


# Auto-register built-in providers
from app.services.auth_provider.mock_provider import MockAuthProvider  # noqa: E402
from app.services.auth_provider.oidc_provider import OIDCAuthProvider  # noqa: E402
from app.services.auth_provider.cas_provider import CASAuthProvider  # noqa: E402
from app.services.auth_provider.ldap_provider import LDAPAuthProvider  # noqa: E402

register_provider("mock", MockAuthProvider)
register_provider("oidc", OIDCAuthProvider)
register_provider("cas", CASAuthProvider)
register_provider("ldap", LDAPAuthProvider)
