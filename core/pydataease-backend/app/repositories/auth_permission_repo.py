from __future__ import annotations

import time
from collections.abc import Sequence
from typing import final

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from ..models.dataset import CoreDatasetGroup
from ..models.datasource import CoreDatasource
from ..models.org_permission import CoreOrgPermission
from ..models.permission_point import CorePermissionPoint
from ..models.resource_acl import CoreResourceAcl
from ..models.role_permission import CoreRolePermission
from ..models.system import CoreMenu
from ..models.user_permission import CoreUserPermission
from ..models.visualization import DataVisualizationInfo


@final
class AuthPermissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_menu_tree_nodes(self) -> Sequence[CoreMenu]:
        stmt = select(CoreMenu).order_by(CoreMenu.pid.asc(), CoreMenu.menu_sort.asc(), CoreMenu.id.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_permission_points_by_menu(self, menu_id: int) -> Sequence[CorePermissionPoint]:
        stmt = select(CorePermissionPoint).where(CorePermissionPoint.menu_id == menu_id).order_by(CorePermissionPoint.id.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_permission_points_by_resource_type(self, resource_type: str) -> Sequence[CorePermissionPoint]:
        stmt = (
            select(CorePermissionPoint)
            .where(CorePermissionPoint.resource_type == resource_type)
            .order_by(CorePermissionPoint.id.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_role_menu_grants(self, role_id: int, oid: int) -> Sequence[CoreRolePermission]:
        stmt = (
            select(CoreRolePermission)
            .where(CoreRolePermission.role_id == role_id, CoreRolePermission.oid == oid)
            .order_by(CoreRolePermission.permission_point_id.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_menu_grants(self, user_id: int) -> Sequence[CoreUserPermission]:
        stmt = (
            select(CoreUserPermission)
            .where(CoreUserPermission.user_id == user_id)
            .order_by(CoreUserPermission.permission_point_id.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_org_menu_grants(self, org_id: int) -> Sequence[CoreOrgPermission]:
        stmt = (
            select(CoreOrgPermission)
            .where(CoreOrgPermission.org_id == org_id)
            .order_by(CoreOrgPermission.permission_point_id.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_resource_acl(self, target_type: str, target_id: int, resource_type: str) -> Sequence[CoreResourceAcl]:
        stmt = (
            select(CoreResourceAcl)
            .where(
                CoreResourceAcl.target_type == target_type,
                CoreResourceAcl.target_id == target_id,
                CoreResourceAcl.resource_type == resource_type,
            )
            .order_by(CoreResourceAcl.resource_id.asc(), CoreResourceAcl.id.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_resource_acl_by_ids(
        self,
        target_type: str,
        target_id: int,
        resource_type: str,
        resource_ids: list[int],
    ) -> Sequence[CoreResourceAcl]:
        if not resource_ids:
            return []

        stmt = (
            select(CoreResourceAcl)
            .where(
                CoreResourceAcl.target_type == target_type,
                CoreResourceAcl.target_id == target_id,
                CoreResourceAcl.resource_type == resource_type,
                CoreResourceAcl.resource_id.in_(resource_ids),
            )
            .order_by(CoreResourceAcl.resource_id.asc(), CoreResourceAcl.id.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def save_resource_acl(self, entries: list[CoreResourceAcl]) -> None:
        if not entries:
            return

        first = entries[0]
        if any(
            entry.target_type != first.target_type
            or entry.target_id != first.target_id
            or entry.resource_type != first.resource_type
            for entry in entries[1:]
        ):
            raise ValueError("All ACL entries must target the same target/resource type combination")

        await self.session.execute(
            delete(CoreResourceAcl).where(
                CoreResourceAcl.target_type == first.target_type,
                CoreResourceAcl.target_id == first.target_id,
                CoreResourceAcl.resource_type == first.resource_type,
            )
        )

        now = int(time.time_ns())
        for index, entry in enumerate(entries):
            if not entry.id:
                entry.id = now + index
            if entry.create_time is None:
                entry.create_time = now
            entry.update_time = now

        self.session.add_all(entries)
        await self.session.commit()

    async def delete_resource_acl(self, target_type: str, target_id: int, resource_type: str) -> None:
        await self.session.execute(
            delete(CoreResourceAcl).where(
                CoreResourceAcl.target_type == target_type,
                CoreResourceAcl.target_id == target_id,
                CoreResourceAcl.resource_type == resource_type,
            )
        )
        await self.session.commit()

    async def get_menu_point_grants(self, target_type: str, target_id: int, oid: int) -> dict[int, bool]:
        grant_model = self._get_menu_grant_model(target_type)
        filters = self._get_target_filters(grant_model, target_id, oid)
        stmt = (
            select(CorePermissionPoint.menu_id, grant_model.granted)
            .join(grant_model, grant_model.permission_point_id == CorePermissionPoint.id)
            .where(CorePermissionPoint.menu_id.is_not(None), *filters)
            .order_by(CorePermissionPoint.menu_id.asc())
        )
        result = await self.session.execute(stmt)
        return {int(menu_id): granted for menu_id, granted in result.all() if menu_id is not None}

    async def save_menu_point_grants(
        self,
        target_type: str,
        target_id: int,
        oid: int,
        grants: list[tuple[int, bool]],
    ) -> None:
        grant_model = self._get_menu_grant_model(target_type)
        filters = self._get_target_filters(grant_model, target_id, oid)

        await self.session.execute(
            delete(grant_model).where(
                *filters,
                grant_model.permission_point_id.in_(
                    select(CorePermissionPoint.id).where(CorePermissionPoint.menu_id.is_not(None))
                ),
            )
        )

        if grants:
            menu_ids = [menu_id for menu_id, _ in grants]
            point_result = await self.session.execute(
                select(CorePermissionPoint).where(CorePermissionPoint.menu_id.in_(menu_ids))
            )
            point_by_menu = {
                int(point.menu_id): point
                for point in point_result.scalars().all()
                if point.menu_id is not None
            }

            now = int(time.time_ns())
            entities = []
            for index, (menu_id, granted) in enumerate(grants):
                point = point_by_menu.get(menu_id)
                if point is None:
                    continue
                payload = {
                    "id": now + index,
                    "permission_point_id": point.id,
                    "granted": granted,
                    "create_time": now,
                    **self._get_target_payload(target_type, target_id, oid),
                }
                entities.append(grant_model(**payload))

            if entities:
                self.session.add_all(entities)

        await self.session.commit()

    async def get_visualization_tree(self, type_filter: str) -> Sequence[DataVisualizationInfo]:
        stmt = (
            select(DataVisualizationInfo)
            .where(
                DataVisualizationInfo.type == type_filter,
                (DataVisualizationInfo.delete_flag.is_(False)) | (DataVisualizationInfo.delete_flag.is_(None)),
            )
            .order_by(DataVisualizationInfo.sort.asc(), DataVisualizationInfo.name.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_dataset_tree(self) -> Sequence[CoreDatasetGroup]:
        stmt = (
            select(CoreDatasetGroup)
            .where(CoreDatasetGroup.id != 0)
            .order_by(CoreDatasetGroup.name.asc(), CoreDatasetGroup.create_time.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_datasource_tree(self) -> Sequence[CoreDatasource]:
        stmt = (
            select(CoreDatasource)
            .where(CoreDatasource.id != 0)
            .order_by(CoreDatasource.name.asc(), CoreDatasource.update_time.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    def _get_menu_grant_model(target_type: str) -> type[CoreRolePermission] | type[CoreUserPermission] | type[CoreOrgPermission]:
        if target_type == "role":
            return CoreRolePermission
        if target_type == "user":
            return CoreUserPermission
        if target_type == "org":
            return CoreOrgPermission
        raise ValueError(f"Unsupported target_type: {target_type}")

    @staticmethod
    def _get_target_filters(
        model: type[CoreRolePermission] | type[CoreUserPermission] | type[CoreOrgPermission],
        target_id: int,
        oid: int,
    ) -> tuple[ColumnElement[bool], ...]:
        if model is CoreRolePermission:
            return (model.role_id == target_id, model.oid == oid)
        if model is CoreUserPermission:
            return (model.user_id == target_id,)
        return (model.org_id == target_id,)

    @staticmethod
    def _get_target_payload(target_type: str, target_id: int, oid: int) -> dict[str, int]:
        if target_type == "role":
            return {"role_id": target_id, "oid": oid}
        if target_type == "user":
            return {"user_id": target_id}
        if target_type == "org":
            return {"org_id": target_id}
        raise ValueError(f"Unsupported target_type: {target_type}")
