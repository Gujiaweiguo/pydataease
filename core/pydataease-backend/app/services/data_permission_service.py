from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.column_permission import CoreColumnPermission
from app.models.permission_whitelist import CorePermissionWhitelist
from app.models.role_user import CoreRoleUser
from app.models.row_permission import CoreRowPermission
from app.schemas.auth import TokenUser


def apply_row_filters(sql: str, filters: list[str]) -> str:
    """Inject row-level filter WHERE clauses into a SQL query.

    Uses query wrapping to handle all cases correctly:
    - Subqueries: filter applied to outer scope
    - UNION queries: filter applies to ALL branches
    - Plain queries: works like simple WHERE append
    """
    if not filters:
        return sql

    combined = " AND ".join(f"({f})" for f in filters)

    # Wrap the original query in an outer SELECT to handle subqueries and UNIONs correctly.
    # This ensures the permission filter is always applied at the outermost level.
    return f"SELECT * FROM ({sql}) AS _perm_filtered WHERE {combined}"


def _mask_value(value: str) -> str:
    """Mask a string value: keep first and last char, replace middle with *."""
    if not value:
        return ""
    if len(value) <= 2:
        return value[0] + "*" if len(value) == 2 else "*"
    return value[0] + "*" * (len(value) - 2) + value[-1]


class DataPermissionService:
    """Query-time enforcement of row and column permissions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def collect_row_filters(self, user: TokenUser, dataset_id: int) -> list[str]:
        """Collect all enabled row-permission WHERE fragments for this user.

        Priority: user > role > org (higher priority entries override lower).
        Returns list of filter_sql fragments to AND together.
        """
        if user.user_id == 1:
            return []

        # Check whitelist
        if await self._is_whitelisted(user.user_id, dataset_id, "row"):
            return []

        # Get user's role IDs in current org
        role_ids = await self._get_user_role_ids(user)

        user_rules = await self._fetch_rules(dataset_id, "user", user.user_id)
        if user_rules:
            return [r.filter_sql for r in user_rules]

        role_filters: list[str] = []
        for rid in role_ids:
            for r in await self._fetch_rules(dataset_id, "role", rid):
                role_filters.append(r.filter_sql)
        if role_filters:
            return role_filters

        org_rules = await self._fetch_rules(dataset_id, "org", user.oid)
        if org_rules:
            return [r.filter_sql for r in org_rules]

        # BUG-007 fix: Default deny when no rules exist for non-admin user
        return ["1=0"]

    async def apply_column_rules(
        self,
        user: TokenUser,
        dataset_id: int,
        fields: list[dict[str, str]],
        rows: list[list[Any]],
    ) -> tuple[list[dict[str, str]], list[list[Any]]]:
        """Apply column-level permission rules to query results.

        Actions:
        - disable: remove field and its data
        - desensitize: replace values with ***
        - mask: keep first/last char, replace middle with *

        Priority: user > role > org for same field
        """
        if user.user_id == 1:
            return fields, rows

        # Check whitelist
        if await self._is_whitelisted(user.user_id, dataset_id, "column"):
            return fields, rows

        role_ids = await self._get_user_role_ids(user)

        # Collect all enabled column rules
        all_rules = await self._fetch_column_rules(dataset_id, user, role_ids)

        # Build field -> action map with priority
        field_actions: dict[int, str] = {}  # field_id -> action
        field_priorities: dict[int, int] = {}  # field_id -> priority (3=user, 2=role, 1=org)

        _RESTRICTIVENESS: dict[str, int] = {"disable": 3, "desensitize": 2, "mask": 1}

        for rule in all_rules:
            priority = {"user": 3, "role": 2, "org": 1}.get(rule.target_type, 0)
            existing = field_priorities.get(rule.field_id, 0)
            if priority > existing or (
                priority == existing
                and _RESTRICTIVENESS.get(rule.action, 0) > _RESTRICTIVENESS.get(field_actions.get(rule.field_id, ""), 0)
            ):
                field_actions[rule.field_id] = rule.action
                field_priorities[rule.field_id] = priority

        if not field_actions:
            return fields, rows

        # Map field names to their indices and build field_id lookup
        # We need to match field names to field IDs. Since fields from SQL executor
        # use column names, we look up field IDs from the dataset's field definitions.
        # For simplicity, we use the field name to look up the rule.
        # The rules store field_id, but we need to match to field names.
        field_name_to_id: dict[str, int] = {}
        if field_actions:
            from app.models.dataset import CoreDatasetTableField

            field_stmt = select(CoreDatasetTableField).where(
                CoreDatasetTableField.dataset_group_id == dataset_id
            )
            result = await self.session.execute(field_stmt)
            for f in result.scalars().all():
                field_name_to_id[f.origin_name] = f.id
                if f.name:
                    field_name_to_id[f.name] = f.id
                if f.dataease_name:
                    field_name_to_id[f.dataease_name] = f.id

        # Determine which indices to disable/desensitize/mask
        disable_indices: set[int] = set()
        desensitize_indices: set[int] = set()
        mask_indices: set[int] = set()

        for idx, field in enumerate(fields):
            name = field.get("name", "")
            fid = field_name_to_id.get(name)
            if fid is not None and fid in field_actions:
                action = field_actions[fid]
                if action == "disable":
                    disable_indices.add(idx)
                elif action == "desensitize":
                    desensitize_indices.add(idx)
                elif action == "mask":
                    mask_indices.add(idx)

        if not disable_indices and not desensitize_indices and not mask_indices:
            return fields, rows

        # Build new fields (remove disabled)
        new_fields = [f for idx, f in enumerate(fields) if idx not in disable_indices]

        # Build new rows
        new_rows: list[list[Any]] = []
        for row in rows:
            new_row: list[Any] = []
            for idx, val in enumerate(row):
                if idx in disable_indices:
                    continue
                if idx in desensitize_indices:
                    new_row.append("***")
                elif idx in mask_indices:
                    new_row.append(_mask_value(str(val)) if val is not None else None)
                else:
                    new_row.append(val)
            new_rows.append(new_row)

        return new_fields, new_rows

    async def _is_whitelisted(self, user_id: int, dataset_id: int, scope: str) -> bool:
        """Check if user is whitelisted for this dataset and scope."""
        stmt = select(CorePermissionWhitelist).where(
            CorePermissionWhitelist.user_id == user_id,
        ).where(
            (CorePermissionWhitelist.dataset_id == dataset_id)
            | (CorePermissionWhitelist.dataset_id == 0)
        ).where(
            (CorePermissionWhitelist.scope == scope)
            | (CorePermissionWhitelist.scope == "both")
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def _get_user_role_ids(self, user: TokenUser) -> list[int]:
        """Get all role IDs for the user in the current org."""
        stmt = select(CoreRoleUser.role_id).where(
            CoreRoleUser.user_id == user.user_id,
            CoreRoleUser.oid == user.oid,
        )
        result = await self.session.execute(stmt)
        return [row[0] for row in result.all()]

    async def _fetch_rules(
        self, dataset_id: int, target_type: str, target_id: int
    ) -> list[CoreRowPermission]:
        """Fetch enabled row permission rules."""
        stmt = select(CoreRowPermission).where(
            CoreRowPermission.dataset_id == dataset_id,
            CoreRowPermission.target_type == target_type,
            CoreRowPermission.target_id == target_id,
            CoreRowPermission.enabled.is_(True),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def _fetch_column_rules(
        self, dataset_id: int, user: TokenUser, role_ids: list[int]
    ) -> list[CoreColumnPermission]:
        """Fetch all enabled column permission rules for this user's context."""
        conditions = [
            CoreColumnPermission.dataset_id == dataset_id,
            CoreColumnPermission.enabled.is_(True),
        ]

        # Build OR conditions for target_type + target_id combinations
        from sqlalchemy import or_

        or_filters = [
            # Org-level rules
            (CoreColumnPermission.target_type == "org") & (CoreColumnPermission.target_id == user.oid),
            # User-level rules
            (CoreColumnPermission.target_type == "user") & (CoreColumnPermission.target_id == user.user_id),
        ]
        # Role-level rules
        for rid in role_ids:
            or_filters.append(
                (CoreColumnPermission.target_type == "role") & (CoreColumnPermission.target_id == rid)
            )

        stmt = select(CoreColumnPermission).where(
            *conditions,
            or_(*or_filters),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
