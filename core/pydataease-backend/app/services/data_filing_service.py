from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db  # pyright: ignore[reportImplicitRelativeImport]
from app.repositories.data_filing_repo import (
    FilingAuditRepository,
    FilingConfigRepository,
    FilingSubmissionRepository,
)
from app.repositories.datasource_repo import DatasourceRepository
from app.settings.defaults import is_feature_enabled
from app.services.datasource_drivers import open_connection

logger = logging.getLogger(__name__)

VALID_CONFIG_STATUSES = {"draft", "published", "disabled"}
VALID_SUBMISSION_STATUSES = {"pending", "success", "failed", "retrying"}
VALID_AUDIT_ACTIONS = {"submit", "publish", "disable", "retry", "config_update"}


class DataFilingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.config_repo = FilingConfigRepository(session)
        self.submission_repo = FilingSubmissionRepository(session)
        self.audit_repo = FilingAuditRepository(session)

    # --- Config CRUD ---

    async def list_configs(self, status: str | None = None) -> list[dict[str, Any]]:
        if status:
            configs = await self.config_repo.get_by_status(status)
        else:
            configs = await self.config_repo.get_all()
        return [self._config_to_dict(c) for c in configs]

    async def get_config(self, filing_id: int) -> dict[str, Any] | None:
        config = await self.config_repo.get_by_id(filing_id)
        if config is None:
            return None
        return self._config_to_dict(config)

    async def create_config(self, payload: dict[str, Any]) -> dict[str, Any] | str:
        feature_on = await is_feature_enabled(self.session, "feature.dataFiling.enabled")
        if not feature_on:
            return "Data filing feature is disabled"

        config = await self.config_repo.create(
            name=payload.get("name", ""),
            status="draft",
            target_datasource_id=payload.get("targetDatasourceId"),
            target_table=payload.get("targetTable"),
            form_schema=payload.get("formSchema", {}),
            field_mapping=payload.get("fieldMapping", {}),
            idempotency_window_seconds=payload.get("idempotencyWindowSeconds", 300),
            oid=payload.get("oid"),
            creator_uid=payload.get("creatorUid"),
        )
        return self._config_to_dict(config)

    async def update_config(self, filing_id: int, payload: dict[str, Any]) -> dict[str, Any] | str:
        config = await self.config_repo.get_by_id(filing_id)
        if config is None:
            return "Config not found"
        if config.status != "draft":
            return "Only draft configs can be updated"

        updates: dict[str, Any] = {}
        if "name" in payload:
            updates["name"] = payload["name"]
        if "targetDatasourceId" in payload:
            updates["target_datasource_id"] = payload["targetDatasourceId"]
        if "targetTable" in payload:
            updates["target_table"] = payload["targetTable"]
        if "formSchema" in payload:
            updates["form_schema"] = payload["formSchema"]
        if "fieldMapping" in payload:
            updates["field_mapping"] = payload["fieldMapping"]
        if "idempotencyWindowSeconds" in payload:
            updates["idempotency_window_seconds"] = payload["idempotencyWindowSeconds"]

        updated = await self.config_repo.update(filing_id, **updates)
        if updated is None:
            return "Config not found"

        await self._create_audit(filing_id, "config_update", payload.get("creatorUid"), details=updates)
        return self._config_to_dict(updated)

    async def delete_config(self, filing_id: int) -> bool | str:
        config = await self.config_repo.get_by_id(filing_id)
        if config is None:
            return "Config not found"
        if config.status != "draft":
            return "Only draft configs can be deleted"

        return await self.config_repo.delete(filing_id)

    async def publish_config(self, filing_id: int) -> dict[str, Any] | str:
        config = await self.config_repo.get_by_id(filing_id)
        if config is None:
            return "Config not found"
        if config.status != "draft":
            return "Only draft configs can be published"

        updated = await self.config_repo.update(filing_id, status="published")
        if updated is None:
            return "Config not found"

        await self._create_audit(filing_id, "publish", config.creator_uid)
        return self._config_to_dict(updated)

    async def disable_config(self, filing_id: int) -> dict[str, Any] | str:
        config = await self.config_repo.get_by_id(filing_id)
        if config is None:
            return "Config not found"
        if config.status != "published":
            return "Only published configs can be disabled"

        updated = await self.config_repo.update(filing_id, status="disabled")
        if updated is None:
            return "Config not found"

        await self._create_audit(filing_id, "disable", config.creator_uid)
        return self._config_to_dict(updated)

    # --- Submissions ---

    async def submit_data(self, filing_id: int, payload: dict[str, Any], submitter_uid: int) -> dict[str, Any] | str:
        feature_on = await is_feature_enabled(self.session, "feature.dataFiling.enabled")
        if not feature_on:
            return "Data filing feature is disabled"

        config = await self.config_repo.get_by_id(filing_id)
        if config is None:
            return "Filing config not found"
        if config.status != "published":
            return "Filing config is not published"

        # Validate payload against form schema
        validation_error = self._validate_payload(config.form_schema or {}, payload)
        if validation_error:
            await self._create_audit(filing_id, "submit", submitter_uid, outcome="failure", error_code="validation_error", details={"error": validation_error})
            return validation_error

        # Idempotency check
        payload_hash = self._compute_hash(payload)
        duplicate = await self._check_idempotency_async(filing_id, payload_hash, config.idempotency_window_seconds)
        if duplicate:
            await self._create_audit(filing_id, "submit", submitter_uid, outcome="failure", error_code="duplicate_submission", details={"hash": payload_hash})
            return "Duplicate submission within idempotency window"

        submission = await self.submission_repo.create(
            filing_id=filing_id,
            payload_hash=payload_hash,
            payload=payload,
            status="pending",
            submitter_uid=submitter_uid,
        )

        try:
            await self._write_to_datasource(config, payload)
            submission = await self.submission_repo.update_status(submission.id, "success", error_message=None)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Data filing write-back failed for filing_id=%s submission_id=%s", filing_id, submission.id)
            error_message = str(exc)
            submission = await self.submission_repo.update_status(
                submission.id,
                "failed",
                error_message=error_message,
            )
            await self._create_audit(
                filing_id,
                "submit",
                submitter_uid,
                submission_id=submission.id if submission else None,
                outcome="failure",
                error_code="write_back_failed",
                details={"payloadHash": payload_hash, "error": error_message},
            )
            if submission is None:
                return "Submission not found"
            return self._submission_to_dict(submission)

        if submission is None:
            return "Submission not found"

        await self._create_audit(
            filing_id, "submit", submitter_uid,
            submission_id=submission.id,
            details={"payloadHash": payload_hash},
        )
        return self._submission_to_dict(submission)

    async def list_submissions(self, filing_id: int) -> list[dict[str, Any]]:
        submissions = await self.submission_repo.get_by_filing(filing_id)
        return [self._submission_to_dict(s) for s in submissions]

    async def get_submission(self, submission_id: int) -> dict[str, Any] | None:
        submission = await self.submission_repo.get_by_id(submission_id)
        if submission is None:
            return None
        return self._submission_to_dict(submission)

    async def retry_submission(self, submission_id: int) -> dict[str, Any] | str:
        submission = await self.submission_repo.get_by_id(submission_id)
        if submission is None:
            return "Submission not found"
        if submission.status not in ("failed",):
            return "Only failed submissions can be retried"

        config = await self.config_repo.get_by_id(submission.filing_id)
        if config is None:
            return "Filing config not found"

        updated = await self.submission_repo.update_status(
            submission_id, "retrying",
            retry_count=submission.retry_count + 1,
            error_message=None,
        )
        if updated is None:
            return "Submission not found"

        try:
            await self._write_to_datasource(config, submission.payload or {})
            updated = await self.submission_repo.update_status(
                submission_id,
                "success",
                retry_count=updated.retry_count,
                error_message=None,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Data filing retry failed for submission_id=%s", submission_id)
            error_message = str(exc)
            updated = await self.submission_repo.update_status(
                submission_id,
                "failed",
                retry_count=updated.retry_count,
                error_message=error_message,
            )
            if updated is None:
                return "Submission not found"
            await self._create_audit(
                submission.filing_id,
                "retry",
                submission.submitter_uid,
                submission_id=submission_id,
                outcome="failure",
                error_code="write_back_failed",
                details={"retryCount": updated.retry_count, "error": error_message},
            )
            return self._submission_to_dict(updated)

        if updated is None:
            return "Submission not found"

        await self._create_audit(
            submission.filing_id, "retry", submission.submitter_uid,
            submission_id=submission_id,
            details={"retryCount": updated.retry_count},
        )
        return self._submission_to_dict(updated)

    # --- Audit ---

    async def list_audit(self, filing_id: int) -> list[dict[str, Any]]:
        audits = await self.audit_repo.get_by_filing(filing_id)
        return [self._audit_to_dict(a) for a in audits]

    # --- Internal helpers ---

    def _check_idempotency(self, filing_id: int, payload_hash: str, window_seconds: int) -> bool:
        """Check for duplicate submission - delegates to repo."""
        # This is called via the service method which awaits the repo
        raise NotImplementedError("Use the async version")

    async def _check_idempotency_async(self, filing_id: int, payload_hash: str, window_seconds: int) -> bool:
        duplicate = await self.submission_repo.get_by_hash(filing_id, payload_hash, window_seconds)
        return duplicate is not None

    async def _write_to_datasource(self, config: Any, payload: dict[str, Any]) -> None:
        if not config.target_datasource_id or not config.target_table:
            raise ValueError("Filing config has no target datasource/table configured")

        ds_repo = DatasourceRepository(self.session)
        datasource = await ds_repo.get_by_id(config.target_datasource_id)
        if datasource is None:
            raise ValueError(f"Datasource {config.target_datasource_id} not found")

        mapping = config.field_mapping or {}
        mapped_payload: dict[str, Any] = {}
        for form_field, value in payload.items():
            target_col = mapping.get(form_field, form_field)
            if target_col:
                mapped_payload[str(target_col)] = value

        if not mapped_payload:
            raise ValueError("No fields to write after applying field mapping")

        columns = list(mapped_payload.keys())
        placeholders = [f"${i + 1}" for i in range(len(columns))]
        values = [mapped_payload[column] for column in columns]

        quoted_cols = ", ".join(self._quote_identifier(column) for column in columns)
        quoted_table = self._quote_identifier(config.target_table)
        sql = f"INSERT INTO {quoted_table} ({quoted_cols}) VALUES ({', '.join(placeholders)})"

        configuration = datasource.configuration if isinstance(datasource.configuration, dict) else {}
        conn = await open_connection(datasource.type, configuration)
        try:
            await conn.execute(sql, *values)
        finally:
            await conn.close()

    @staticmethod
    def _compute_hash(payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _validate_payload(form_schema: dict[str, Any], payload: dict[str, Any]) -> str | None:
        """Validate payload against form schema. Returns error message or None."""
        fields = form_schema.get("fields", [])
        if not fields:
            return None

        for field in fields:
            field_name = field.get("name", "")
            required = field.get("required", False)
            if required and field_name not in payload:
                return f"Missing required field: {field_name}"
        return None

    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        escaped = identifier.replace('"', '""')
        return f'"{escaped}"'

    async def _create_audit(
        self,
        filing_id: int,
        action: str,
        actor_uid: int | None = None,
        *,
        submission_id: int | None = None,
        details: dict[str, Any] | None = None,
        outcome: str = "success",
        error_code: str | None = None,
    ) -> None:
        await self.audit_repo.create(
            filing_id=filing_id,
            submission_id=submission_id,
            action=action,
            actor_uid=actor_uid,
            details=details,
            outcome=outcome,
            error_code=error_code,
        )

    @staticmethod
    def _config_to_dict(config: Any) -> dict[str, Any]:
        return {
            "id": config.id,
            "name": config.name,
            "status": config.status,
            "targetDatasourceId": config.target_datasource_id,
            "targetTable": config.target_table,
            "formSchema": config.form_schema or {},
            "fieldMapping": config.field_mapping or {},
            "idempotencyWindowSeconds": config.idempotency_window_seconds,
            "oid": config.oid,
            "creatorUid": config.creator_uid,
            "createTime": str(config.create_time) if config.create_time else None,
            "updateTime": str(config.update_time) if config.update_time else None,
        }

    @staticmethod
    def _submission_to_dict(submission: Any) -> dict[str, Any]:
        return {
            "id": submission.id,
            "filingId": submission.filing_id,
            "payloadHash": submission.payload_hash,
            "payload": submission.payload,
            "status": submission.status,
            "errorMessage": submission.error_message,
            "submitterUid": submission.submitter_uid,
            "retryCount": submission.retry_count,
            "createTime": str(submission.create_time) if submission.create_time else None,
            "updateTime": str(submission.update_time) if submission.update_time else None,
        }

    @staticmethod
    def _audit_to_dict(audit: Any) -> dict[str, Any]:
        return {
            "id": audit.id,
            "filingId": audit.filing_id,
            "submissionId": audit.submission_id,
            "action": audit.action,
            "actorUid": audit.actor_uid,
            "details": audit.details,
            "outcome": audit.outcome,
            "errorCode": audit.error_code,
            "createTime": str(audit.create_time) if audit.create_time else None,
        }


def get_data_filing_service(session: AsyncSession = Depends(get_db)) -> DataFilingService:
    return DataFilingService(session)
