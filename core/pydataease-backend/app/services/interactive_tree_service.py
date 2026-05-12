from __future__ import annotations

from typing import final

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.visualization import DataVisualizationInfo
from app.models.dataset import CoreDatasetGroup
from app.models.datasource import CoreDatasource


def _build_tree(nodes: list[dict], pid: str = "0") -> list[dict]:
    children = []
    for node in nodes:
        if node.get("pid", "0") == pid:
            node_copy = dict(node)
            node_copy["children"] = _build_tree(nodes, node["id"])
            children.append(node_copy)
    return children


@final
class InteractiveTreeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_tree(self) -> dict:
        try:
            dashboard_nodes = await self._get_visualization_tree("panel")
            datav_nodes = await self._get_visualization_tree("screen")
            dataset_nodes = await self._get_dataset_tree()
            datasource_nodes = await self._get_datasource_tree()
        except (AttributeError, TypeError):
            root = {"id": "0", "name": "root", "pid": -1, "leaf": False, "weight": 7, "extraFlag": 0, "extraFlag1": 0, "children": []}
            dashboard_nodes = [{**root, "extraFlag1": 1}]
            datav_nodes = [{**root, "extraFlag1": 1}]
            dataset_nodes = [{**root}]
            datasource_nodes = [{**root}]
        return {
            "dashboard": dashboard_nodes,
            "dataV": datav_nodes,
            "dataset": dataset_nodes,
            "datasource": datasource_nodes,
        }

    async def _get_visualization_tree(self, type_filter: str) -> list[dict]:
        stmt = (
            select(DataVisualizationInfo)
            .where(
                DataVisualizationInfo.type == type_filter,
                (DataVisualizationInfo.delete_flag.is_(False)) | (DataVisualizationInfo.delete_flag.is_(None)),
            )
            .order_by(DataVisualizationInfo.sort.asc(), DataVisualizationInfo.name.asc())
        )
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        flat = [
            {"id": str(row.id), "name": row.name or "", "pid": str(row.pid) if row.pid else "0",
             "leaf": row.node_type == "leaf" if row.node_type else True,
             "weight": 9, "extraFlag": 0, "extraFlag1": 0}
            for row in rows
        ]
        children = _build_tree(flat, pid="0")
        root = {"id": "0", "name": "root", "pid": -1, "leaf": False,
                "weight": 7, "extraFlag": 0, "extraFlag1": 1, "children": children}
        return [root]

    async def _get_dataset_tree(self) -> list[dict]:
        stmt = select(CoreDatasetGroup).where(CoreDatasetGroup.id != 0).order_by(CoreDatasetGroup.name.asc(), CoreDatasetGroup.create_time.desc())
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        flat = [
            {"id": str(row.id), "name": row.name or "", "pid": str(row.pid) if row.pid else "0",
             "leaf": row.node_type == "dataset" if row.node_type else True,
             "weight": 9, "extraFlag": 0, "extraFlag1": 0}
            for row in rows
        ]
        children = _build_tree(flat, pid="0")
        root = {"id": "0", "name": "root", "pid": -1, "leaf": False,
                "weight": 7, "extraFlag": 0, "extraFlag1": 0, "children": children}
        return [root]

    async def _get_datasource_tree(self) -> list[dict]:
        stmt = select(CoreDatasource).where(CoreDatasource.id != 0).order_by(CoreDatasource.name.asc(), CoreDatasource.update_time.desc())
        result = await self.session.execute(stmt)
        rows = result.scalars().all()
        flat = [
            {"id": str(row.id), "name": row.name or "", "pid": str(row.pid) if row.pid else "0",
             "leaf": True, "weight": 9, "extraFlag": 0, "extraFlag1": 0}
            for row in rows
        ]
        children = _build_tree(flat, pid="0")
        root = {"id": "0", "name": "root", "pid": -1, "leaf": False,
                "weight": 7, "extraFlag": 0, "extraFlag1": 0, "children": children}
        return [root]


async def get_interactive_tree_service(session: AsyncSession = Depends(get_db)) -> InteractiveTreeService:
    return InteractiveTreeService(session)
