from __future__ import annotations

from app.services.auth_provider.base import AuthResult, BaseAuthProvider, ProviderClaim


class MockAuthProvider(BaseAuthProvider):
    """Mock provider for testing. Accepts any username/password."""

    provider_type = "mock"

    async def authenticate(self, credentials: dict) -> AuthResult:
        username = credentials.get("username", "")

        if not username:
            return AuthResult(success=False, error="username is required")

        # Mock always succeeds with any username (password ignored for testing)
        return AuthResult(
            success=True,
            claims=ProviderClaim(
                external_id=f"mock:{username}",
                username=username,
                email=f"{username}@mock.local",
                display_name=username,
                groups=["mock-users"],
                raw_claims={"provider": "mock", "username": username},
            ),
        )

    async def get_authorize_url(self, redirect_uri: str, state: str) -> str | None:
        # Mock uses direct auth, no redirect flow
        return None

    async def handle_callback(self, code: str, state: str, redirect_uri: str) -> AuthResult:
        return AuthResult(success=False, error="mock provider does not support callback flow")

    def validate_config(self, config: dict) -> list[str]:
        # Mock provider has no required config
        return []
