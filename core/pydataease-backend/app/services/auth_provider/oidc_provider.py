from __future__ import annotations

import logging
from urllib.parse import urlencode

import httpx

from app.services.auth_provider.base import AuthResult, BaseAuthProvider, ProviderClaim

logger = logging.getLogger(__name__)


class OIDCAuthProvider(BaseAuthProvider):
    """OIDC provider implementing Authorization Code flow.

    Config keys:
        issuer_url:       OIDC issuer (e.g. https://accounts.google.com)
        client_id:        OAuth client ID
        client_secret:    OAuth client secret
        scope:            Space-separated scopes (default: "openid profile email")
        authorize_url:    Override auto-discovered authorization endpoint
        token_url:        Override auto-discovered token endpoint
        userinfo_url:     Override auto-discovered userinfo endpoint
    """

    provider_type = "oidc"

    # --- Required config keys for validation ---
    _REQUIRED_KEYS = ("issuer_url", "client_id", "client_secret")

    def _cfg(self, key: str, default: str = "") -> str:
        return str(self.config.get(key, default))

    # ------------------------------------------------------------------
    # OAuth redirect flow
    # ------------------------------------------------------------------

    async def get_authorize_url(self, redirect_uri: str, state: str) -> str | None:
        authorize_url = self._cfg("authorize_url")
        if not authorize_url:
            # Attempt OIDC discovery
            discovered = await self._discover_endpoints()
            if discovered:
                authorize_url = discovered.get("authorization_endpoint", "")
            if not authorize_url:
                logger.error("OIDC: cannot determine authorization_endpoint")
                return None

        params = {
            "response_type": "code",
            "client_id": self._cfg("client_id"),
            "redirect_uri": redirect_uri,
            "scope": self._cfg("scope", "openid profile email"),
            "state": state,
        }
        return f"{authorize_url}?{urlencode(params)}"

    async def handle_callback(self, code: str, state: str, redirect_uri: str) -> AuthResult:
        token_url = self._cfg("token_url")
        userinfo_url = self._cfg("userinfo_url")

        if not token_url or not userinfo_url:
            discovered = await self._discover_endpoints()
            if discovered:
                token_url = token_url or discovered.get("token_endpoint", "")
                userinfo_url = userinfo_url or discovered.get("userinfo_endpoint", "")

        if not token_url:
            return AuthResult(success=False, error="OIDC: token_endpoint not configured and discovery failed")

        if not userinfo_url:
            return AuthResult(success=False, error="OIDC: userinfo_endpoint not configured and discovery failed")

        # Exchange code for tokens
        async with httpx.AsyncClient(timeout=30.0) as client:
            token_resp = await client.post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": self._cfg("client_id"),
                    "client_secret": self._cfg("client_secret"),
                },
                headers={"Accept": "application/json"},
            )

            if token_resp.status_code != 200:
                logger.error("OIDC token exchange failed: %s %s", token_resp.status_code, token_resp.text)
                return AuthResult(success=False, error=f"OIDC token exchange failed: HTTP {token_resp.status_code}")

            token_data = token_resp.json()
            access_token = token_data.get("access_token", "")

            if not access_token:
                return AuthResult(success=False, error="OIDC: no access_token in token response")

            # Fetch user info
            userinfo_resp = await client.get(
                userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if userinfo_resp.status_code != 200:
                logger.error("OIDC userinfo failed: %s %s", userinfo_resp.status_code, userinfo_resp.text)
                return AuthResult(success=False, error=f"OIDC userinfo failed: HTTP {userinfo_resp.status_code}")

            claims = userinfo_resp.json()

        return AuthResult(
            success=True,
            claims=ProviderClaim(
                external_id=str(claims.get("sub", "")),
                username=claims.get("preferred_username") or claims.get("name"),
                email=claims.get("email"),
                display_name=claims.get("name"),
                groups=claims.get("groups", []),
                raw_claims=claims,
            ),
        )

    # ------------------------------------------------------------------
    # Direct auth — not supported for OIDC
    # ------------------------------------------------------------------

    async def authenticate(self, credentials: dict) -> AuthResult:
        return AuthResult(success=False, error="OIDC provider does not support direct authentication")

    # ------------------------------------------------------------------
    # Config validation
    # ------------------------------------------------------------------

    def validate_config(self, config: dict) -> list[str]:
        errors: list[str] = []
        for key in self._REQUIRED_KEYS:
            if not config.get(key):
                errors.append(f"Missing required config: {key}")
        return errors

    # ------------------------------------------------------------------
    # OIDC Discovery
    # ------------------------------------------------------------------

    async def _discover_endpoints(self) -> dict | None:
        """Fetch OIDC discovery document from issuer_url + /.well-known/openid-configuration."""
        issuer = self._cfg("issuer_url").rstrip("/")
        discovery_url = f"{issuer}/.well-known/openid-configuration"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(discovery_url)
                if resp.status_code == 200:
                    return resp.json()
        except httpx.HTTPError:
            logger.warning("OIDC discovery failed for %s", discovery_url)
        return None
