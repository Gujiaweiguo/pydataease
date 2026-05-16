from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_user
from app.schemas.auth import TokenUser
from app.schemas.visualization_subject import SubjectUpdateRequest
from app.services.visualization_subject_service import (
    VisualizationSubjectService,
    get_subject_service,
)

router = APIRouter(tags=["visualization-subject"])


@router.post("/visualizationSubject/query")
async def query_subjects(
    user: TokenUser = Depends(get_current_user),
    service: VisualizationSubjectService = Depends(get_subject_service),
) -> object:
    return await service.query()


@router.post("/visualizationSubject/querySubjectWithGroup")
async def query_subjects_with_group(
    user: TokenUser = Depends(get_current_user),
    service: VisualizationSubjectService = Depends(get_subject_service),
) -> object:
    return await service.query_subject_with_group()


@router.post("/visualizationSubject/update")
async def update_subject(
    payload: SubjectUpdateRequest,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationSubjectService = Depends(get_subject_service),
) -> object:
    return await service.update_subject(payload, user)


@router.post("/visualizationSubject/delete/{subject_id}")
async def delete_subject(
    subject_id: str,
    user: TokenUser = Depends(get_current_user),
    service: VisualizationSubjectService = Depends(get_subject_service),
) -> None:
    await service.delete_subject(subject_id)
