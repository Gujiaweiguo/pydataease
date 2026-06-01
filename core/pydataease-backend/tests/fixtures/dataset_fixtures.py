from __future__ import annotations

from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.dataset import (  # pyright: ignore[reportImplicitRelativeImport]
    DatasetFieldResponse,
    DatasetNodeResponse,
    DatasetTreeNodeResponse,
)

class FakeDatasetService:
    def __init__(self) -> None:
        self.created: list[tuple[object, TokenUser]] = []
        self.saved: list[tuple[object, TokenUser]] = []
        self.renamed: list[tuple[object, TokenUser]] = []
        self.moved: list[tuple[object, TokenUser]] = []
        self.deleted_ids: list[int] = []

    async def tree(self) -> list[DatasetTreeNodeResponse]:
        return [
            DatasetTreeNodeResponse(
                id=1,
                name="root-folder",
                pid=0,
                level=0,
                node_type="folder",
                leaf=False,
                children=[
                    DatasetTreeNodeResponse(
                        id=2,
                        name="child-dataset",
                        pid=1,
                        level=1,
                        node_type="dataset",
                        leaf=True,
                        children=[],
                    )
                ],
            )
        ]

    async def create(self, payload: object, user: TokenUser) -> DatasetNodeResponse:
        self.created.append((payload, user))
        return DatasetNodeResponse(
            id=100,
            name="new-dataset",
            pid=0,
            level=0,
            node_type="dataset",
        )

    async def save(self, payload: object, user: TokenUser) -> DatasetNodeResponse:
        self.saved.append((payload, user))
        return DatasetNodeResponse(
            id=200,
            name="updated-dataset",
            pid=0,
            level=0,
            node_type="dataset",
        )

    async def rename(self, payload: object, user: TokenUser) -> DatasetNodeResponse:
        self.renamed.append((payload, user))
        return DatasetNodeResponse(
            id=300,
            name="renamed-dataset",
            pid=0,
            level=0,
            node_type="folder",
        )

    async def move(self, payload: object, user: TokenUser) -> DatasetNodeResponse:
        self.moved.append((payload, user))
        return DatasetNodeResponse(
            id=400,
            name="moved-dataset",
            pid=5,
            level=1,
            node_type="dataset",
        )

    async def delete(self, group_id: int) -> None:
        self.deleted_ids.append(group_id)

    async def per_delete(self, group_id: int) -> bool:
        return True

    async def get_bar_info(self, group_id: int) -> dict[str, object]:
        return {
            "id": str(group_id),
            "name": "bar-info-ds",
            "pid": "0",
            "level": 0,
            "nodeType": "dataset",
            "createBy": "7",
        }

    async def get_details(self, group_id: int) -> dict[str, object]:
        return {
            "id": str(group_id),
            "name": "detail-ds",
            "pid": "0",
            "level": 0,
            "nodeType": "dataset",
        }

    async def get_fields(self, request: object) -> list[DatasetFieldResponse]:
        return [
            DatasetFieldResponse(
                id=501,
                origin_name="col_a",
                name="Column A",
                de_type=0,
                de_extract_type=0,
                ext_field=0,
            )
        ]

    async def preview_sql(self, payload: dict[str, object]) -> dict[str, object]:
        return {"sql": str(payload.get("sql", "")), "data": [], "fields": [], "total": 0}

    async def get_dataset_preview(self, group_id: int, user: TokenUser | None = None) -> dict[str, object]:
        return {}

    async def get_dataset_total(self, group_id: int, user: TokenUser | None = None) -> int:
        return 0

    async def preview_data(self, payload: object, user: TokenUser | None = None) -> dict[str, object]:
        return {"allFields": [], "data": {"fields": [], "data": [], "total": 0}}

    async def get_enum_values(self, payload: object, user: TokenUser | None = None) -> list[str]:
        return []

    async def get_enum_value_objects(self, payload: object, user: TokenUser | None = None) -> list[dict[str, str]]:
        return []

    async def export_dataset(self, payload: object) -> dict:  # pyright: ignore[reportMissingTypeArgument]
        return {"file": "dataset.xlsx", "status": "SUCCESS"}
