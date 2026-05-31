"""User provisioning for third-party authentication.

When an external identity provider successfully authenticates a user,
this service:
1. Looks up an existing user-auth-link for the provider + external_id
2. If found, returns the linked local user
3. If not found, attempts email matching
4. If no match, creates a new local user
5. Creates/updates the user-auth-link
6. Issues a JWT token
"""

from __future__ import annotations

import logging
import secrets
import time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_provider import AuthProvider
from app.repositories.auth_provider_repo import AuthProviderRepository
from app.repositories.user_auth_link_repo import UserAuthLinkRepository
from app.repositories.user_repo import UserRepository
from app.schemas.login import TokenResponse
from app.services.auth_provider.base import ProviderClaim
from app.services.auth_service import AuthService
from app.utils.password_utils import hash_password

logger = logging.getLogger(__name__)

# Origin values matching the data model convention
ORIGIN_OIDC = 1
ORIGIN_CAS = 2
ORIGIN_LDAP = 3
ORIGIN_MOCK = 9

_ORIGIN_MAP: dict[str, int] = {
    "oidc": ORIGIN_OIDC,
    "cas": ORIGIN_CAS,
    "ldap": ORIGIN_LDAP,
    "mock": ORIGIN_MOCK,
}


class UserProvisioningService:
    """Find or create a local user for a third-party auth result, then issue JWT."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.link_repo = UserAuthLinkRepository(session)
        self.provider_repo = AuthProviderRepository(session)

    async def provision_and_issue_token(
        self,
        provider_id: int,
        claims: ProviderClaim,
    ) -> TokenResponse | str:
        """Provision a local user from provider claims and issue a JWT.

        Returns TokenResponse on success or an error string on failure.
        """
        # 1. Look up the provider to determine type
        provider = await self.provider_repo.get_by_id(provider_id)
        if provider is None:
            return f"Provider not found: {provider_id}"

        origin = _ORIGIN_MAP.get(provider.type, 0)
        if origin == 0:
            return f"Unknown provider type: {provider.type}"

        # 2. Find existing link
        link = await self.link_repo.get_by_provider_and_external_id(provider_id, claims.external_id)

        user_id: int | None = None

        if link is not None:
            # Existing link — use the linked user
            user_id = link.user_id
            # Update link metadata
            await self.link_repo.update(link, {
                "external_username": claims.username,
                "external_email": claims.email,
                "update_time": time.time_ns() // 1_000_000,
            })
        else:
            # 3. No link — try email matching
            user = None
            if claims.email:
                user = await self.user_repo.get_by_email(claims.email)

            if user is None:
                # 4. Create new user
                user = await self._create_user(claims, origin, provider)
                if isinstance(user, str):
                    return user  # error string

            user_id = user.id

            # 5. Create user-auth-link
            await self.link_repo.create({
                "user_id": user_id,
                "provider_id": provider_id,
                "external_id": claims.external_id,
                "external_username": claims.username,
                "external_email": claims.email,
            })

        # 6. Verify user exists and is enabled
        if user_id is None:
            return "User not found after provisioning"
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            return "User not found after provisioning"
        if not user.enable:
            return "User account is disabled"

        # 7. Issue JWT via AuthService
        auth_service = AuthService(self.session)
        oid = await auth_service._resolve_current_org_id(user.id, user.oid or 0)
        return auth_service._issue_token(user.id, oid, user.password)

    async def _create_user(self, claims: ProviderClaim, origin: int, provider: AuthProvider) -> Any:
        """Create a new local user from provider claims.

        Generates a random password (user never sees it — they always auth via the provider).
        """
        # Build a unique account name
        account = claims.username or claims.email or claims.external_id
        # Ensure account uniqueness
        existing = await self.user_repo.get_by_account(account)
        if existing is not None:
            # Append provider suffix to avoid collision
            account = f"{account}@{provider.type}"

        existing = await self.user_repo.get_by_account(account)
        if existing is not None:
            return f"Cannot create unique account for external user: {claims.external_id}"

        # Generate random password — user authenticates via provider, not password
        random_password = secrets.token_hex(32)
        password_hash = hash_password(random_password)

        user = await self.user_repo.create({
            "id": time.time_ns(),
            "account": account,
            "name": claims.display_name or account,
            "email": claims.email,
            "password": password_hash,
            "enable": True,
            "origin": origin,
            "oid": provider.oid or 0,
            "create_time": time.time_ns() // 1_000_000,
            "update_time": time.time_ns() // 1_000_000,
        })

        await self.session.flush()
        return user
