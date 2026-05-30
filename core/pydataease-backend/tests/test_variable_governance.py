from __future__ import annotations

import logging
import os
import time
from typing import cast

import pytest
from fastapi import HTTPException  # pyright: ignore[reportMissingImports]
from sqlalchemy import delete, select

from app.models.sys_variable import CoreSysVariable  # pyright: ignore[reportImplicitRelativeImport]
from app.models.watermark import VisualizationWatermark  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.sys_variable import SysVariableCreateRequest  # pyright: ignore[reportImplicitRelativeImport]
from app.services.sys_variable_service import SysVariableService  # pyright: ignore[reportImplicitRelativeImport]

skip_no_db = pytest.mark.skipif(os.getenv("DE_E2E") != "1", reason="Requires PostgreSQL (set DE_E2E=1)")


def _user() -> TokenUser:
    return TokenUser(user_id=7, oid=9)


async def _cleanup_variable(db_session, names: list[str]) -> None:
    if not names:
        return
    result = await db_session.execute(select(CoreSysVariable.id).where(CoreSysVariable.name.in_(names)))
    ids = list(result.scalars().all())
    if ids:
        await db_session.execute(delete(CoreSysVariable).where(CoreSysVariable.id.in_(ids)))
        await db_session.commit()


@skip_no_db
@pytest.mark.asyncio
async def test_valid_variable_creation_passes(db_session) -> None:
    await _cleanup_variable(db_session, ["gov_city"])
    try:
        service = SysVariableService(db_session)

        result = await service.create(SysVariableCreateRequest(name="gov_city", alias="城市"), _user())

        assert result["name"] == "gov_city"
        assert result["type"] == "text"
    finally:
        await _cleanup_variable(db_session, ["gov_city"])


@skip_no_db
@pytest.mark.asyncio
async def test_invalid_name_starts_with_number_rejected(db_session) -> None:
    service = SysVariableService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await service.create(SysVariableCreateRequest(name="1city", type="text"), _user())

    assert exc_info.value.status_code == 400


@skip_no_db
@pytest.mark.asyncio
async def test_invalid_name_with_spaces_rejected(db_session) -> None:
    service = SysVariableService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await service.create(SysVariableCreateRequest(name="city name", type="text"), _user())

    assert exc_info.value.status_code == 400


@skip_no_db
@pytest.mark.asyncio
async def test_duplicate_name_rejected(db_session) -> None:
    await _cleanup_variable(db_session, ["gov_dup"])
    try:
        service = SysVariableService(db_session)
        await service.create(SysVariableCreateRequest(name="gov_dup", type="text"), _user())

        with pytest.raises(HTTPException) as exc_info:
            await service.create(SysVariableCreateRequest(name="gov_dup", type="text"), _user())

        assert exc_info.value.status_code == 409
    finally:
        await _cleanup_variable(db_session, ["gov_dup"])


@skip_no_db
@pytest.mark.asyncio
async def test_invalid_type_rejected(db_session) -> None:
    service = SysVariableService(db_session)

    with pytest.raises(HTTPException) as exc_info:
        await service.create(SysVariableCreateRequest(name="gov_type", type="json"), _user())

    assert exc_info.value.status_code == 400


@skip_no_db
@pytest.mark.asyncio
async def test_deletion_with_dependency_warning_soft_check(db_session, caplog: pytest.LogCaptureFixture) -> None:
    variable_name = "gov_delete_warn"
    await _cleanup_variable(db_session, [variable_name])
    watermark_snapshot = await db_session.get(VisualizationWatermark, "system_default")
    try:
        service = SysVariableService(db_session)
        created = await service.create(SysVariableCreateRequest(name=variable_name, type="text"), _user())
        created_id = cast(int, created["id"])
        await db_session.execute(delete(VisualizationWatermark).where(VisualizationWatermark.id == "system_default"))
        db_session.add(
            VisualizationWatermark(
                id="system_default",
                version="1.0",
                setting_content=f'{{"enable": true, "text": "${{{variable_name}}}"}}',
                create_by="tester",
                create_time=int(time.time() * 1000),
            )
        )
        await db_session.commit()

        with caplog.at_level(logging.WARNING):
            await service.delete(created_id, check_dependencies=True)

        assert f"System variable '{variable_name}' referenced in watermark setting_content" in caplog.text
        assert await db_session.get(CoreSysVariable, created_id) is None
    finally:
        await db_session.execute(delete(VisualizationWatermark).where(VisualizationWatermark.id == "system_default"))
        await db_session.commit()
        if watermark_snapshot is not None:
            db_session.add(
                VisualizationWatermark(
                    id=watermark_snapshot.id,
                    version=watermark_snapshot.version,
                    setting_content=watermark_snapshot.setting_content,
                    create_by=watermark_snapshot.create_by,
                    create_time=watermark_snapshot.create_time,
                )
            )
            await db_session.commit()
        await _cleanup_variable(db_session, [variable_name])
