from __future__ import annotations

import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.repositories.dataset_repo import DatasetFieldRepository
from app.schemas.auth import TokenUser
from app.schemas.dataset import (
    DatasetFieldIdsRequest,
    DatasetFieldResponse,
    DatasetFieldSaveRequest,
)

router = APIRouter(prefix="/datasetField", tags=["dataset-field"])

SQL_FUNCTIONS = [
    {"name": "SUBSTRING", "func": "SUBSTRING(s,n,len)", "type": 0, "desc": "获取从字符串s中的第n个位置开始长度为len的字符串", "isCustom": False},
    {"name": "ABS", "func": "ABS(x)", "type": 2, "desc": "返回x的绝对值", "isCustom": False},
    {"name": "CEIL", "func": "CEIL(x)", "type": 2, "desc": "返回不小于x的最小整数", "isCustom": False},
    {"name": "FLOOR", "func": "FLOOR(x)", "type": 2, "desc": "返回不大于x的最大整数", "isCustom": False},
    {"name": "ROUND", "func": "ROUND(x)", "type": 2, "desc": "返回离x最近的整数", "isCustom": False},
    {"name": "ROUND", "func": "ROUND(x,y)", "type": 2, "desc": "保留x小数点后y位的值", "isCustom": False},
    {"name": "COUNT", "func": "COUNT(x)", "type": 4, "desc": "对x计数", "isCustom": False},
    {"name": "SUM", "func": "SUM(x)", "type": 4, "desc": "对x求和", "isCustom": False},
    {"name": "AVG", "func": "AVG(x)", "type": 4, "desc": "对x求平均值", "isCustom": False},
    {"name": "MAX", "func": "MAX(x)", "type": 4, "desc": "对x求最大值", "isCustom": False},
    {"name": "MIN", "func": "MIN(x)", "type": 4, "desc": "对x求最小值", "isCustom": False},
]


async def get_field_repo(session: AsyncSession = Depends(get_db)) -> DatasetFieldRepository:
    return DatasetFieldRepository(session)


@router.post("/listByDatasetGroup/{id}")
async def list_by_dataset_group(
    id: int,
    _: TokenUser = Depends(get_current_user),
    repo: DatasetFieldRepository = Depends(get_field_repo),
) -> list[dict[str, object]]:
    rows = await repo.list_checked_by_group(id)
    return [DatasetFieldResponse.model_validate(r).model_dump(by_alias=True) for r in rows]


@router.get("/listWithPermissions/{id}")
async def list_with_permissions(
    id: int,
    _: TokenUser = Depends(get_current_user),
    repo: DatasetFieldRepository = Depends(get_field_repo),
) -> list[dict[str, object]]:
    rows = await repo.list_checked_by_group(id)
    return [DatasetFieldResponse.model_validate(r).model_dump(by_alias=True) for r in rows]


@router.post("/listByDQ/{id}")
async def list_by_dq(
    id: int,
    _: TokenUser = Depends(get_current_user),
    repo: DatasetFieldRepository = Depends(get_field_repo),
) -> dict[str, list[dict[str, object]]]:
    rows = await repo.list_checked_by_group_no_chart_filter(id)
    dimension_list = [DatasetFieldResponse.model_validate(r).model_dump(by_alias=True) for r in rows if r.group_type == "d"]
    quota_list = [DatasetFieldResponse.model_validate(r).model_dump(by_alias=True) for r in rows if r.group_type == "q"]
    return {"dimensionList": dimension_list, "quotaList": quota_list}


@router.post("/get/{id}")
async def get_field(
    id: int,
    _: TokenUser = Depends(get_current_user),
    repo: DatasetFieldRepository = Depends(get_field_repo),
) -> dict[str, object]:
    field = await repo.get_by_id(id)
    if field is None:
        raise HTTPException(status_code=404, detail="Field not found")
    return DatasetFieldResponse.model_validate(field).model_dump(by_alias=True)


@router.post("/save")
async def save_field(
    payload: DatasetFieldSaveRequest,
    _: TokenUser = Depends(get_current_user),
    repo: DatasetFieldRepository = Depends(get_field_repo),
) -> dict[str, object]:
    field_data = payload.model_dump(by_alias=False, exclude_none=True)

    if payload.chart_id is not None and payload.ext_field == 1:
        field_data["dataset_group_id"] = None

    if payload.id is None:
        field_data["id"] = time.time_ns()

    origin_name = field_data.get("origin_name") or ""
    field_data.setdefault("origin_name", origin_name)
    field_data.setdefault("type", "VARCHAR")
    field_data.setdefault("de_type", 0)
    field_data.setdefault("de_extract_type", 0)

    saved = await repo.save_field(field_data)
    return DatasetFieldResponse.model_validate(saved).model_dump(by_alias=True)


@router.post("/delete/{id}")
async def delete_field(
    id: int,
    _: TokenUser = Depends(get_current_user),
    repo: DatasetFieldRepository = Depends(get_field_repo),
) -> None:
    await repo.delete_by_id(id)


@router.post("/listByDsIds")
async def list_by_ds_ids(
    payload: DatasetFieldIdsRequest,
    _: TokenUser = Depends(get_current_user),
    repo: DatasetFieldRepository = Depends(get_field_repo),
) -> dict[str, list[dict[str, object]]]:
    result = await repo.list_origin_fields_by_groups(payload.ids)
    return {
        key: [DatasetFieldResponse.model_validate(f).model_dump(by_alias=True) for f in fields]
        for key, fields in result.items()
    }


@router.post("/multFieldValuesForPermissions")
async def mult_field_values_for_permissions(
    payload: dict[str, object],
    _: TokenUser = Depends(get_current_user),
) -> list[object]:
    return []


@router.post("/copilotFields/{id}")
async def copilot_fields(
    id: int,
    _: TokenUser = Depends(get_current_user),
    repo: DatasetFieldRepository = Depends(get_field_repo),
) -> list[dict[str, object]]:
    rows = await repo.list_checked_by_group(id)
    return [DatasetFieldResponse.model_validate(r).model_dump(by_alias=True) for r in rows]


@router.post("/getFunction")
async def get_function(
    _: TokenUser = Depends(get_current_user),
):
    return SQL_FUNCTIONS


@router.post("/deleteByChartId/{id}")
async def delete_by_chart_id(
    id: int,
    _: TokenUser = Depends(get_current_user),
    repo: DatasetFieldRepository = Depends(get_field_repo),
) -> None:
    await repo.delete_by_chart_id(id)
