from __future__ import annotations

import logging

from ldap3 import ALL, SUBTREE, Connection, Server
from ldap3.core.exceptions import LDAPBindError, LDAPException

from app.services.auth_provider.base import AuthResult, BaseAuthProvider, ProviderClaim

logger = logging.getLogger(__name__)


class LDAPAuthProvider(BaseAuthProvider):
    """LDAP direct-auth provider.

    Authenticates users by binding to the LDAP server with their DN.
    Optionally searches for group membership.

    Config keys:
        server_url:       LDAP server URL (e.g. ldap://ldap.example.com:389)
        bind_dn:          DN pattern for binding; {username} placeholder replaced at runtime
                          e.g. "uid={username},ou=users,dc=example,dc=com"
        search_base:      Base DN for user search (used for attribute lookup after bind)
        search_filter:    LDAP filter to find user (default: "(uid={username})")
        use_ssl:          Whether to use SSL/TLS (default: False based on ldap:// vs ldaps://)
    """

    provider_type = "ldap"

    _REQUIRED_KEYS = ("server_url", "bind_dn")

    def _cfg(self, key: str, default: str = "") -> str:
        return str(self.config.get(key, default))

    # ------------------------------------------------------------------
    # Direct authentication (LDAP bind)
    # ------------------------------------------------------------------

    async def authenticate(self, credentials: dict) -> AuthResult:
        username = credentials.get("username", "")
        password = credentials.get("password", "")

        if not username or not password:
            return AuthResult(success=False, error="username and password are required")

        server_url = self._cfg("server_url")
        bind_dn_template = self._cfg("bind_dn")
        search_base = self._cfg("search_base")
        search_filter_template = self._cfg("search_filter", "(uid={username})")

        # Build user-specific bind DN and search filter
        bind_dn = bind_dn_template.replace("{username}", username)
        search_filter = search_filter_template.replace("{username}", username)

        try:
            server = Server(server_url, get_info=ALL, connect_timeout=10)
            conn = Connection(server, user=bind_dn, password=password, auto_bind=True, raise_exceptions=True)
        except LDAPBindError:
            return AuthResult(success=False, error="LDAP bind failed: invalid credentials")
        except LDAPException as exc:
            logger.error("LDAP connection error: %s", exc)
            return AuthResult(success=False, error=f"LDAP connection error: {exc}")

        # Search for user attributes
        attributes: dict = {}
        if search_base:
            try:
                conn.search(search_base, search_filter, search_scope=SUBTREE, attributes=["*"])
                if conn.entries:
                    entry = conn.entries[0]
                    attributes = {attr: entry[attr].value for attr in entry.entry_attributes}
            except LDAPException as exc:
                logger.warning("LDAP search error (non-fatal): %s", exc)

        conn.unbind()

        external_id = attributes.get("uid", username)
        email = attributes.get("mail")
        if isinstance(email, list):
            email = email[0] if email else None
        display_name = attributes.get("displayName") or attributes.get("cn") or username
        if isinstance(display_name, list):
            display_name = display_name[0] if display_name else username
        groups_raw = attributes.get("memberOf", [])
        if isinstance(groups_raw, str):
            groups_raw = [groups_raw]

        return AuthResult(
            success=True,
            claims=ProviderClaim(
                external_id=str(external_id),
                username=username,
                email=str(email) if email else None,
                display_name=str(display_name),
                groups=[str(g) for g in groups_raw],
                raw_claims=attributes,
            ),
        )

    # ------------------------------------------------------------------
    # OAuth redirect flow — not supported for LDAP
    # ------------------------------------------------------------------

    async def get_authorize_url(self, redirect_uri: str, state: str) -> str | None:
        return None

    async def handle_callback(self, code: str, state: str, redirect_uri: str) -> AuthResult:
        return AuthResult(success=False, error="LDAP provider does not support callback flow")

    # ------------------------------------------------------------------
    # Config validation
    # ------------------------------------------------------------------

    def validate_config(self, config: dict) -> list[str]:
        errors: list[str] = []
        if not config.get("server_url"):
            errors.append("Missing required config: server_url")
        if not config.get("bind_dn"):
            errors.append("Missing required config: bind_dn")
        return errors
