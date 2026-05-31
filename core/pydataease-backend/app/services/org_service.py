from __future__ import annotations

import time
from typing import final

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.models.org import CoreOrg
from app.repositories.org_repo import OrgRepository
from app.schemas.auth import TokenUser
from app.schemas.org import OrgCreateRequest, OrgEditRequest, OrgResponse, OrgTreeNode
from app.utils.id_utils import _sid


def _build_tree(nodes: list[dict[str, object]], pid: str = "0") -> list[dict[str, object]]:
    children: list[dict[str, object]] = []
    for node in nodes:
        if node.get("pid", "0") == pid:
            node_copy = dict(node)
            node_copy["children"] = _build_tree(nodes, str(node["id"]))
            node_copy["leaf"] = len(node_copy["children"]) == 0
            children.append(node_copy)
    return children


@final
class OrgService:
    session: AsyncSession
    repository: OrgRepository

    def __init__(self, session: AsyncSession, repository: OrgRepository) -> None:
        self.session = session
        self.repository = repository

    async def tree(self, user: TokenUser) -> list[OrgTreeNode]:
        if user.user_id == 1:
            all_orgs = await self.repository.list_all()
            flat = [self._to_tree_node(org) for org in all_orgs]
            children = [OrgTreeNode.model_validate(node) for node in _build_tree(flat, pid="0")]
            return [OrgTreeNode(id="0", name="root", pid=-1, leaf=False, children=children)]

        user_orgs = await self.repository.get_user_orgs(user.user_id)
        if not user_orgs:
            return [OrgTreeNode(id="0", name="root", pid=-1, leaf=False, children=[])]

        # Strict isolation: non-admin users see only their own orgs — no ancestors, no descendants.
        flat = [self._to_tree_node(org) for org in user_orgs]
        children = [OrgTreeNode.model_validate(node) for node in flat]
        return [OrgTreeNode(id="0", name="root", pid=-1, leaf=False, children=children)]

    async def create(self, payload: OrgCreateRequest) -> OrgResponse:
        pid = 0 if payload.pid in (None, 0) else payload.pid
        if pid != 0:
            parent = await self.repository.get_by_id(pid)
            if parent is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Parent org not found")

        now = _timestamp_ms()
        created = await self.repository.create(
            {
                "id": _new_identifier(),
                "pid": pid,
                "name": payload.name.strip(),
                "create_time": now,
                "update_time": now,
            }
        )
        return OrgResponse.model_validate(created)

    async def edit(self, payload: OrgEditRequest) -> OrgResponse:
        org = await self._get_entity(payload.id)
        updated = await self.repository.update(
            org,
            {
                "name": payload.name.strip(),
                "update_time": _timestamp_ms(),
            },
        )
        return OrgResponse.model_validate(updated)

    async def delete(self, oid: int) -> None:
        org = await self._get_entity(oid)
        children = await self.repository.get_children(oid)
        if children:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization has child organizations and cannot be deleted",
            )
        await self.repository.delete(org)

    async def resource_exist(self, oid: int) -> bool:
        _ = await self._get_entity(oid)
        children = await self.repository.get_children(oid)
        return len(children) > 0

    async def _get_entity(self, oid: int) -> CoreOrg:
        entity = await self.repository.get_by_id(oid)
        if entity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        return entity

    @staticmethod
    def _collect_allowed_org_ids(user_orgs: list[CoreOrg], all_orgs: list[CoreOrg]) -> set[int]:
        orgs_by_id = {org.id: org for org in all_orgs}
        descendants_by_pid: dict[int, list[CoreOrg]] = {}
        for org in all_orgs:
            if org.pid is None:
                continue
            descendants_by_pid.setdefault(org.pid, []).append(org)

        allowed_ids: set[int] = set()
        stack = [org.id for org in user_orgs]
        while stack:
            current = stack.pop()
            if current in allowed_ids:
                continue
            allowed_ids.add(current)
            for child in descendants_by_pid.get(current, []):
                stack.append(child.id)

        for org in user_orgs:
            parent_id = org.pid
            while parent_id not in (None, 0):
                parent = orgs_by_id.get(parent_id)
                if parent is None or parent.id in allowed_ids:
                    break
                allowed_ids.add(parent.id)
                parent_id = parent.pid
        return allowed_ids

    @staticmethod
    def _to_tree_node(org: CoreOrg) -> dict[str, object]:
        pid = _sid(org.pid) if org.pid not in (None, 0) else "0"
        return {
            "id": _sid(org.id) or "",
            "name": org.name,
            "pid": pid,
            "leaf": True,
            "weight": 9,
            "extraFlag": 0,
            "extraFlag1": 0,
        }


async def get_org_service(session: AsyncSession = Depends(get_db)) -> OrgService:
    return OrgService(session=session, repository=OrgRepository(session))


def _timestamp_ms() -> int:
    return int(time.time() * 1000)


def _new_identifier() -> int:
    return time.time_ns()
