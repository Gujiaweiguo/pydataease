from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.chart_service import ChartService


@pytest.mark.asyncio
async def test_list_fields_by_dq_splits_dimension_and_quota_lists() -> None:
    service = ChartService(cast(AsyncSession, cast(Any, SimpleNamespace())))
    service.group_repo.get_by_id = AsyncMock(return_value=SimpleNamespace(id=99))  # type: ignore[attr-defined]
    service.field_repo.list_by_chart = AsyncMock(  # type: ignore[attr-defined]
        return_value=[
            SimpleNamespace(
                id=1,
                datasource_id=10,
                dataset_table_id=20,
                dataset_group_id=99,
                origin_name="region",
                name="区域",
                dataease_name="f_region",
                group_type="d",
                type="VARCHAR",
                de_type=0,
                de_extract_type=0,
                ext_field=0,
                checked=True,
                field_short_name="region",
                desensitized=False,
                params=None,
            ),
            SimpleNamespace(
                id=2,
                datasource_id=10,
                dataset_table_id=20,
                dataset_group_id=99,
                origin_name="amount",
                name="销售额",
                dataease_name="f_amount",
                group_type="q",
                type="DECIMAL",
                de_type=2,
                de_extract_type=2,
                ext_field=0,
                checked=True,
                field_short_name="amount",
                desensitized=False,
                params=None,
            ),
        ]
    )

    result = await service.list_fields_by_dq(99, 1001)

    assert result["dimensionList"][0]["groupType"] == "d"
    assert result["quotaList"][0]["groupType"] == "q"
    assert result["dimensionList"][0]["name"] == "区域"
    assert result["quotaList"][0]["name"] == "销售额"
