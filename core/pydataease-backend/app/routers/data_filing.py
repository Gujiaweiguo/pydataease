from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies.auth import get_current_user  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.data_filing import FilingConfigCreateRequest, FilingConfigUpdateRequest, FilingSubmitRequest
from app.services.data_filing_service import DataFilingService, get_data_filing_service

router = APIRouter(tags=["data-filing"])


# --- Admin routes (require auth) ---


@router.get("/data-filing/config/list")
async def list_configs(
    status: str | None = None,
    user: TokenUser = Depends(get_current_user),
    service: DataFilingService = Depends(get_data_filing_service),
) -> list[dict[str, Any]]:
    """List filing configs, optionally filtered by status."""
    return await service.list_configs(status)


@router.get("/data-filing/config/{filing_id}")
async def get_config(
    filing_id: int,
    user: TokenUser = Depends(get_current_user),
    service: DataFilingService = Depends(get_data_filing_service),
) -> dict[str, Any]:
    """Get a single filing config."""
    result = await service.get_config(filing_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Filing config not found")
    return result


@router.post("/data-filing/config/create")
async def create_config(
    payload: FilingConfigCreateRequest,
    user: TokenUser = Depends(get_current_user),
    service: DataFilingService = Depends(get_data_filing_service),
) -> dict[str, Any]:
    """Create a new filing config in draft state."""
    data = payload.model_dump(by_alias=True)
    data.setdefault("creatorUid", user.user_id)
    result = await service.create_config(data)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.put("/data-filing/config/{filing_id}")
async def update_config(
    filing_id: int,
    payload: FilingConfigUpdateRequest,
    user: TokenUser = Depends(get_current_user),
    service: DataFilingService = Depends(get_data_filing_service),
) -> dict[str, Any]:
    """Update a draft filing config."""
    result = await service.update_config(filing_id, payload.model_dump(by_alias=True, exclude_unset=True))
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.delete("/data-filing/config/{filing_id}")
async def delete_config(
    filing_id: int,
    user: TokenUser = Depends(get_current_user),
    service: DataFilingService = Depends(get_data_filing_service),
) -> bool:
    """Delete a draft filing config."""
    result = await service.delete_config(filing_id)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/data-filing/config/{filing_id}/publish")
async def publish_config(
    filing_id: int,
    user: TokenUser = Depends(get_current_user),
    service: DataFilingService = Depends(get_data_filing_service),
) -> dict[str, Any]:
    """Publish a draft filing config."""
    result = await service.publish_config(filing_id)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/data-filing/config/{filing_id}/disable")
async def disable_config(
    filing_id: int,
    user: TokenUser = Depends(get_current_user),
    service: DataFilingService = Depends(get_data_filing_service),
) -> dict[str, Any]:
    """Disable a published filing config."""
    result = await service.disable_config(filing_id)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result


# --- Submission routes (require auth) ---


@router.post("/data-filing/{filing_id}/submit")
async def submit_data(
    filing_id: int,
    payload: FilingSubmitRequest,
    user: TokenUser = Depends(get_current_user),
    service: DataFilingService = Depends(get_data_filing_service),
) -> dict[str, Any]:
    """Submit data to a published filing config."""
    result = await service.submit_data(filing_id, payload.model_dump(), user.user_id)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.get("/data-filing/{filing_id}/submissions")
async def list_submissions(
    filing_id: int,
    user: TokenUser = Depends(get_current_user),
    service: DataFilingService = Depends(get_data_filing_service),
) -> list[dict[str, Any]]:
    """List submissions for a filing config."""
    return await service.list_submissions(filing_id)


@router.get("/data-filing/submission/{submission_id}")
async def get_submission(
    submission_id: int,
    user: TokenUser = Depends(get_current_user),
    service: DataFilingService = Depends(get_data_filing_service),
) -> dict[str, Any]:
    """Get a single submission."""
    result = await service.get_submission(submission_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Submission not found")
    return result


@router.post("/data-filing/submission/{submission_id}/retry")
async def retry_submission(
    submission_id: int,
    user: TokenUser = Depends(get_current_user),
    service: DataFilingService = Depends(get_data_filing_service),
) -> dict[str, Any]:
    """Retry a failed submission."""
    result = await service.retry_submission(submission_id)
    if isinstance(result, str):
        raise HTTPException(status_code=400, detail=result)
    return result


# --- Audit routes (require auth) ---


@router.get("/data-filing/{filing_id}/audit")
async def list_audit(
    filing_id: int,
    user: TokenUser = Depends(get_current_user),
    service: DataFilingService = Depends(get_data_filing_service),
) -> list[dict[str, Any]]:
    """List audit records for a filing config."""
    return await service.list_audit(filing_id)
