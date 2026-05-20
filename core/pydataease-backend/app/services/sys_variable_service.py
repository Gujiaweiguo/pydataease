from __future__ import annotations

import time
from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.repositories.sys_variable_repo import SysVariableRepository, SysVariableValueRepository
from app.models.sys_variable import CoreSysVariable, CoreSysVariableValue
from app.schemas.auth import TokenUser
from app.schemas.sys_variable import (
    SysVariableCreateRequest,
    SysVariableEditRequest,
    SysVariableQueryRequest,
    SysVariableResponse,
    SysVariableValueBatchDeleteRequest,
    SysVariableValueCreateRequest,
    SysVariableValueEditRequest,
    SysVariableValuePageRequest,
    SysVariableValuePageResponse,
    SysVariableValueResponse,
)


def _timestamp_ms() -> int:
    return int(time.time() * 1000)


def _identifier() -> int:
    return time.time_ns()


@final
class SysVariableService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.variable_repo = SysVariableRepository(session)
        self.value_repo = SysVariableValueRepository(session)

    async def create(self, payload: SysVariableCreateRequest, user: TokenUser) -> dict[str, object]:
        now = _timestamp_ms()
        entity = await self.variable_repo.create(
            {
                "id": _identifier(),
                "name": payload.name.strip(),
                "alias": _clean_optional(payload.alias),
                "type": _clean_optional(payload.type),
                "remark": _clean_optional(payload.remark),
                "dataset_group_id": payload.dataset_group_id,
                "dataset_table_id": payload.dataset_table_id,
                "create_time": now,
                "update_time": now,
                "create_by": user.user_id,
            }
        )
        return _dump(SysVariableResponse.model_validate(entity))

    async def edit(self, payload: SysVariableEditRequest) -> dict[str, object]:
        entity = await self._get_variable(payload.id)
        updated = await self.variable_repo.update(
            entity,
            {
                "name": payload.name.strip(),
                "alias": _clean_optional(payload.alias),
                "type": _clean_optional(payload.type),
                "remark": _clean_optional(payload.remark),
                "dataset_group_id": payload.dataset_group_id,
                "dataset_table_id": payload.dataset_table_id,
                "update_time": _timestamp_ms(),
            },
        )
        return _dump(SysVariableResponse.model_validate(updated))

    async def detail(self, variable_id: int) -> dict[str, object]:
        return _dump(SysVariableResponse.model_validate(await self._get_variable(variable_id)))

    async def delete(self, variable_id: int) -> None:
        entity = await self._get_variable(variable_id)
        await self.value_repo.delete_by_variable_id(variable_id)
        await self.variable_repo.delete(entity)

    async def query(self, payload: SysVariableQueryRequest | None) -> list[dict[str, object]]:
        rows = await self.variable_repo.search(
            keyword=payload.keyword if payload else None,
            name=payload.name if payload else None,
            type_=payload.type if payload else None,
        )
        return [_dump(SysVariableResponse.model_validate(row)) for row in rows]

    async def value_page(self, page: int, limit: int, payload: SysVariableValuePageRequest | None) -> dict[str, object]:
        normalized_page = max(page, 1)
        normalized_limit = max(limit, 1)
        records, total = await self.value_repo.page_by_variable_id(
            variable_id=payload.variable_id if payload else None,
            keyword=payload.keyword if payload else None,
            offset=(normalized_page - 1) * normalized_limit,
            limit=normalized_limit,
        )
        return _dump(
            SysVariableValuePageResponse(
                records=[SysVariableValueResponse.model_validate(row) for row in records],
                total=total,
                page=normalized_page,
                page_size=normalized_limit,
            )
        )

    async def value_list(self, variable_id: int) -> list[dict[str, object]]:
        _ = await self._get_variable(variable_id)
        rows = await self.value_repo.list_by_variable_id(variable_id)
        return [_dump(SysVariableValueResponse.model_validate(row)) for row in rows]

    async def create_value(self, payload: SysVariableValueCreateRequest) -> dict[str, object]:
        await self._get_variable(payload.variable_id)
        now = _timestamp_ms()
        entity = await self.value_repo.create(
            {
                "id": _identifier(),
                "variable_id": payload.variable_id,
                "value": payload.value,
                "name": _clean_optional(payload.name),
                "remark": _clean_optional(payload.remark),
                "create_time": now,
                "update_time": now,
            }
        )
        return _dump(SysVariableValueResponse.model_validate(entity))

    async def edit_value(self, payload: SysVariableValueEditRequest) -> dict[str, object]:
        await self._get_variable(payload.variable_id)
        entity = await self._get_value(payload.id)
        updated = await self.value_repo.update(
            entity,
            {
                "variable_id": payload.variable_id,
                "value": payload.value,
                "name": _clean_optional(payload.name),
                "remark": _clean_optional(payload.remark),
                "update_time": _timestamp_ms(),
            },
        )
        return _dump(SysVariableValueResponse.model_validate(updated))

    async def delete_value(self, value_id: int) -> None:
        await self.value_repo.delete(await self._get_value(value_id))

    async def batch_delete_values(self, payload: SysVariableValueBatchDeleteRequest) -> None:
        await self.value_repo.batch_delete(payload.ids)

    async def _get_variable(self, variable_id: int) -> CoreSysVariable:
        entity = await self.variable_repo.get_by_id(variable_id)
        if entity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="System variable not found")
        return entity

    async def _get_value(self, value_id: int) -> CoreSysVariableValue:
        entity = await self.value_repo.get_by_id(value_id)
        if entity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="System variable value not found")
        return entity


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _dump(model: SysVariableResponse | SysVariableValueResponse | SysVariableValuePageResponse) -> dict[str, object]:
    return model.model_dump(by_alias=True)


async def get_sys_variable_service(session: AsyncSession = Depends(get_db)) -> SysVariableService:
    return SysVariableService(session)
