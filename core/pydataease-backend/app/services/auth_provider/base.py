from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ProviderClaim:
    """Normalized claim from an external identity provider."""

    external_id: str
    username: str | None = None
    email: str | None = None
    display_name: str | None = None
    groups: list[str] = field(default_factory=list)
    raw_claims: dict | None = None


@dataclass
class AuthResult:
    """Result of an authentication attempt."""

    success: bool
    claims: ProviderClaim | None = None
    error: str | None = None


class BaseAuthProvider(ABC):
    """Unified contract for all identity providers (LDAP, OIDC, CAS, mock).

    Each provider type must implement this contract. The contract covers:
    - Direct authentication (username/password style)
    - OAuth-style redirect flow (authorize URL + callback)
    - Configuration validation
    """

    provider_type: str = ""  # Override in subclass: "ldap", "oidc", "cas", "mock"

    def __init__(self, config: dict | None = None) -> None:
        self.config: dict = config or {}

    @abstractmethod
    async def authenticate(self, credentials: dict) -> AuthResult:
        """Authenticate a user with provider-specific credentials.

        For direct-auth providers (LDAP, mock): credentials contain username/password.
        For OAuth providers: this may raise NotImplementedError.
        """
        ...

    @abstractmethod
    async def get_authorize_url(self, redirect_uri: str, state: str) -> str | None:
        """Get the authorization URL for OAuth-style flows.

        Returns None for direct-auth providers (LDAP, mock) that don't use redirect flow.
        """
        ...

    @abstractmethod
    async def handle_callback(self, code: str, state: str, redirect_uri: str) -> AuthResult:
        """Handle OAuth callback after user authenticates at provider.

        Exchange code for tokens, extract claims.
        May raise NotImplementedError for direct-auth providers.
        """
        ...

    @abstractmethod
    def validate_config(self, config: dict) -> list[str]:
        """Validate provider configuration.

        Returns list of error messages. Empty list = valid config.
        """
        ...
