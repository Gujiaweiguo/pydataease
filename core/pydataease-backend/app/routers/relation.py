from __future__ import annotations

# pyright: reportMissingImports=false

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user  # pyright: ignore[reportImplicitRelativeImport]
from app.dependencies.database import get_db  # pyright: ignore[reportImplicitRelativeImport]
from app.models.chart import CoreChartView  # pyright: ignore[reportImplicitRelativeImport]
from app.models.dataset import CoreDatasetTable  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]

router = APIRouter(tags=["relation"])


@router.post("/relation/datasource/{datasource_id}")
async def relation_datasource(
    datasource_id: int,
    _: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[dict[str, str | None]]:
    """Find all datasets that use this datasource."""
    stmt = select(CoreDatasetTable).where(CoreDatasetTable.datasource_id == datasource_id)
    result = await session.execute(stmt)
    tables = list(result.scalars().all())
    return [
        {
            "id": str(table.dataset_group_id),
            "name": table.name or "",
            "type": "dataset",
        }
        for table in tables
        if table.dataset_group_id is not None
    ]


@router.post("/relation/dataset/{dataset_group_id}")
async def relation_dataset(
    dataset_group_id: int,
    _: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[dict[str, str | None]]:
    """Find all charts that use this dataset group."""
    stmt = select(CoreChartView).where(CoreChartView.table_id == dataset_group_id)
    result = await session.execute(stmt)
    charts = list(result.scalars().all())
    return [
        {
            "id": str(chart.id),
            "name": chart.title or "",
            "type": "chart",
            "sceneId": str(chart.scene_id),
        }
        for chart in charts
    ]


@router.post("/relation/dv/{dv_id}")
async def relation_dv(
    dv_id: int,
    _: TokenUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[dict[str, str | None]]:
    """Find all charts in this visualization."""
    stmt = select(CoreChartView).where(CoreChartView.scene_id == dv_id)
    result = await session.execute(stmt)
    charts = list(result.scalars().all())
    return [
        {
            "id": str(chart.id),
            "name": chart.title or "",
            "type": "chart",
            "tableId": str(chart.table_id) if chart.table_id is not None else None,
        }
        for chart in charts
    ]
