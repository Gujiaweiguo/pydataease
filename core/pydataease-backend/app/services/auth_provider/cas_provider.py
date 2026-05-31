from __future__ import annotations

import logging
from urllib.parse import urlencode

import httpx

from app.services.auth_provider.base import AuthResult, BaseAuthProvider, ProviderClaim

logger = logging.getLogger(__name__)


class CASAuthProvider(BaseAuthProvider):
    """CAS (Central Authentication Service) provider.

    Implements CAS 2.0/3.0 protocol with /serviceValidate or /p3/serviceValidate.

    Config keys:
        cas_server_url:  CAS server base URL (e.g. https://cas.example.com/cas)
        validate_endpoint: Validation path (default: "/p3/serviceValidate")
        attribute_prefix:  Prefix for CAS attributes in response (default: "cas:")
    """

    provider_type = "cas"

    _REQUIRED_KEYS = ("cas_server_url",)

    def _cfg(self, key: str, default: str = "") -> str:
        return str(self.config.get(key, default))

    # ------------------------------------------------------------------
    # OAuth-like redirect flow
    # ------------------------------------------------------------------

    async def get_authorize_url(self, redirect_uri: str, state: str) -> str | None:
        cas_url = self._cfg("cas_server_url").rstrip("/")
        login_url = f"{cas_url}/login"
        params = {"service": redirect_uri}
        return f"{login_url}?{urlencode(params)}"

    async def handle_callback(self, code: str, state: str, redirect_uri: str) -> AuthResult:
        """Validate the CAS service ticket (the 'code' is the ticket)."""
        cas_url = self._cfg("cas_server_url").rstrip("/")
        endpoint = self._cfg("validate_endpoint", "/p3/serviceValidate")
        validate_url = f"{cas_url}{endpoint}"

        params = {"service": redirect_uri, "ticket": code}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(validate_url, params=params)

            if resp.status_code != 200:
                logger.error("CAS validation failed: HTTP %s", resp.status_code)
                return AuthResult(success=False, error=f"CAS validation failed: HTTP {resp.status_code}")

            body = resp.text

        # Parse CAS XML response
        success, user, attributes = self._parse_cas_response(body)

        if not success:
            return AuthResult(success=False, error="CAS ticket validation failed")

        return AuthResult(
            success=True,
            claims=ProviderClaim(
                external_id=user or "",
                username=user,
                email=attributes.get("mail") or attributes.get("email"),
                display_name=attributes.get("displayName") or attributes.get("cn") or user,
                groups=attributes.get("groups", "").split(",") if attributes.get("groups") else [],
                raw_claims={"user": user, "attributes": attributes},
            ),
        )

    # ------------------------------------------------------------------
    # Direct auth — not supported for CAS
    # ------------------------------------------------------------------

    async def authenticate(self, credentials: dict) -> AuthResult:
        return AuthResult(success=False, error="CAS provider does not support direct authentication")

    # ------------------------------------------------------------------
    # Config validation
    # ------------------------------------------------------------------

    def validate_config(self, config: dict) -> list[str]:
        errors: list[str] = []
        if not config.get("cas_server_url"):
            errors.append("Missing required config: cas_server_url")
        return errors

    # ------------------------------------------------------------------
    # CAS XML parsing (simple — no dependency on lxml)
    # ------------------------------------------------------------------

    def _parse_cas_response(self, body: str) -> tuple[bool, str | None, dict]:
        """Parse CAS 2.0/3.0 XML serviceValidate response.

        Returns (success, user, attributes_dict).
        """
        import xml.etree.ElementTree as ET

        try:
            root = ET.fromstring(body)
        except ET.ParseError:
            logger.error("CAS: failed to parse XML response")
            return False, None, {}

        # Handle namespace-prefixed CAS 3.0 responses
        ns = ""
        if root.tag.startswith("{"):
            ns = root.tag.split("}")[0] + "}"

        auth_success = root.find(f".//{ns}authenticationSuccess")
        if auth_success is None:
            return False, None, {}

        user_elem = auth_success.find(f"{ns}user")
        user = user_elem.text if user_elem is not None else None

        attributes: dict = {}
        attrs_elem = auth_success.find(f"{ns}attributes")
        if attrs_elem is not None:
            for child in attrs_elem:
                # Strip namespace from tag
                tag = child.tag.replace(ns, "")
                attributes[tag] = child.text or ""

        return True, user, attributes
