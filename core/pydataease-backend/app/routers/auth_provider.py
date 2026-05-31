from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user, get_optional_user  # pyright: ignore[reportImplicitRelativeImport]
from app.dependencies.database import get_db  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.services.auth_provider_service import AuthProviderService, get_auth_provider_service

router = APIRouter(tags=["auth-provider"])


@router.get("/auth-provider/list")
async def list_providers(
    user: TokenUser = Depends(get_current_user),
    service: AuthProviderService = Depends(get_auth_provider_service),
) -> list[dict]:
    """List all auth providers. Admin only."""
    return await service.list_providers()


@router.get("/auth-provider/{provider_id}")
async def get_provider(
    provider_id: int,
    user: TokenUser = Depends(get_current_user),
    service: AuthProviderService = Depends(get_auth_provider_service),
) -> dict:
    """Get single provider detail. Admin only."""
    result = await service.get_provider(provider_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    return result


@router.post("/auth-provider/create")
async def create_provider(
    payload: dict,
    user: TokenUser = Depends(get_current_user),
    service: AuthProviderService = Depends(get_auth_provider_service),
) -> dict:
    """Create a new auth provider. Admin only."""
    result = await service.create_provider(payload)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.put("/auth-provider/{provider_id}")
async def update_provider(
    provider_id: int,
    payload: dict,
    user: TokenUser = Depends(get_current_user),
    service: AuthProviderService = Depends(get_auth_provider_service),
) -> dict:
    """Update an auth provider. Admin only."""
    result = await service.update_provider(provider_id, payload)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.delete("/auth-provider/{provider_id}")
async def delete_provider(
    provider_id: int,
    user: TokenUser = Depends(get_current_user),
    service: AuthProviderService = Depends(get_auth_provider_service),
) -> dict:
    """Delete an auth provider. Admin only."""
    result = await service.delete_provider(provider_id)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return {"success": True}


@router.post("/auth-provider/{provider_id}/toggle")
async def toggle_provider(
    provider_id: int,
    payload: dict,
    user: TokenUser = Depends(get_current_user),
    service: AuthProviderService = Depends(get_auth_provider_service),
) -> dict:
    """Enable or disable a provider. Admin only."""
    enabled = payload.get("enabled", True)
    result = await service.toggle_provider(provider_id, enabled)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/auth-provider/{provider_id}/default")
async def set_default_provider(
    provider_id: int,
    user: TokenUser = Depends(get_current_user),
    service: AuthProviderService = Depends(get_auth_provider_service),
) -> dict:
    """Set a provider as the default login method. Admin only."""
    result = await service.set_default_provider(provider_id)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/auth-provider/{provider_id}/callback")
async def provider_callback(
    provider_id: int,
    payload: dict,
    user: TokenUser | None = Depends(get_optional_user),
    session: AsyncSession = Depends(get_db),
    service: AuthProviderService = Depends(get_auth_provider_service),
) -> dict:
    """Handle SSO callback. Public endpoint (no auth required).

    Exchanges the OAuth code for user claims, provisions the user,
    and returns a JWT token.
    """
    code = payload.get("code", "")
    state = payload.get("state", "")
    redirect_uri = payload.get("redirect_uri", "")

    from app.services.auth_provider.base import AuthResult
    from app.services.user_provisioning_service import UserProvisioningService

    result = await service.handle_provider_callback(provider_id, code, state, redirect_uri)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    if isinstance(result, AuthResult):
        if not result.success:
            raise HTTPException(status_code=401, detail=result.error or "Authentication failed")
        if result.claims is None:
            raise HTTPException(status_code=500, detail="No claims returned from provider")

        # Provision user and issue JWT
        provisioning = UserProvisioningService(session)
        token_result = await provisioning.provision_and_issue_token(provider_id, result.claims)
        if isinstance(token_result, str):
            raise HTTPException(status_code=500, detail=token_result)

        await session.commit()
        return {"success": True, "token": token_result.token, "exp": token_result.exp}
    raise HTTPException(status_code=500, detail="Unexpected result")


@router.post("/auth-provider/{provider_id}/test")
async def test_provider(
    provider_id: int,
    payload: dict,
    user: TokenUser = Depends(get_current_user),
    service: AuthProviderService = Depends(get_auth_provider_service),
) -> dict:
    """Test provider connection with sample credentials. Admin only."""
    credentials = payload.get("credentials", {})
    from app.services.auth_provider.base import AuthResult

    result = await service.authenticate_with_provider(provider_id, credentials)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    if isinstance(result, AuthResult):
        return {
            "success": result.success,
            "error": result.error,
            "claims": {
                "externalId": result.claims.external_id,
                "username": result.claims.username,
            }
            if result.claims
            else None,
        }
    raise HTTPException(status_code=500, detail="Unexpected result")


@router.get("/auth-provider/{provider_id}/authorize")
async def provider_authorize(
    provider_id: int,
    redirect_uri: str,
    service: AuthProviderService = Depends(get_auth_provider_service),
) -> dict:
    """Get the OAuth authorize URL for a provider. Public endpoint."""
    import secrets as _secrets

    provider = await service.repo.get_by_id(provider_id)
    if provider is None:
        raise HTTPException(status_code=404, detail="Provider not found")
    if not provider.enabled:
        raise HTTPException(status_code=400, detail="Provider is disabled")

    from app.services.auth_provider import get_provider_class

    provider_cls = get_provider_class(provider.type)
    if provider_cls is None:
        raise HTTPException(status_code=400, detail=f"Unknown provider type: {provider.type}")

    instance = provider_cls(provider.config or {})
    state = _secrets.token_urlsafe(32)
    authorize_url = await instance.get_authorize_url(redirect_uri, state)

    if authorize_url is None:
        raise HTTPException(status_code=400, detail="This provider does not support OAuth redirect flow")

    return {"authorizeUrl": authorize_url, "state": state}


@router.post("/auth-provider/{provider_id}/login")
async def provider_direct_login(
    provider_id: int,
    payload: dict,
    session: AsyncSession = Depends(get_db),
    service: AuthProviderService = Depends(get_auth_provider_service),
) -> dict:
    """Direct login for providers like LDAP. Public endpoint (no auth required).

    Accepts username/password, authenticates against the provider,
    provisions the user, and returns a JWT token.
    """
    credentials = payload.get("credentials", {})

    from app.services.auth_provider.base import AuthResult
    from app.services.user_provisioning_service import UserProvisioningService

    result = await service.authenticate_with_provider(provider_id, credentials)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    if isinstance(result, AuthResult):
        if not result.success:
            raise HTTPException(status_code=401, detail=result.error or "Authentication failed")
        if result.claims is None:
            raise HTTPException(status_code=500, detail="No claims returned from provider")

        # Provision user and issue JWT
        provisioning = UserProvisioningService(session)
        token_result = await provisioning.provision_and_issue_token(provider_id, result.claims)
        if isinstance(token_result, str):
            raise HTTPException(status_code=500, detail=token_result)

        await session.commit()
        return {"success": True, "token": token_result.token, "exp": token_result.exp}
    raise HTTPException(status_code=500, detail="Unexpected result")
