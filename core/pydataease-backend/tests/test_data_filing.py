"""Tests for data filing backbone: models, service, routes."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.data_filing import FilingAudit, FilingConfig, FilingSubmission
from app.services.data_filing_service import DataFilingService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_config(**overrides) -> FilingConfig:
    defaults = {
        "id": 1001,
        "name": "test-form",
        "status": "draft",
        "target_datasource_id": None,
        "target_table": None,
        "form_schema": {},
        "field_mapping": {},
        "idempotency_window_seconds": 300,
        "oid": None,
        "creator_uid": 42,
    }
    defaults.update(overrides)
    cfg = MagicMock(spec=FilingConfig)
    for k, v in defaults.items():
        setattr(cfg, k, v)
    return cfg


def _make_submission(**overrides) -> FilingSubmission:
    defaults = {
        "id": 2001,
        "filing_id": 1001,
        "payload_hash": "abc123",
        "payload": {"field1": "value1"},
        "status": "success",
        "error_message": None,
        "submitter_uid": 42,
        "retry_count": 0,
    }
    defaults.update(overrides)
    sub = MagicMock(spec=FilingSubmission)
    for k, v in defaults.items():
        setattr(sub, k, v)
    return sub


def _mock_service() -> DataFilingService:
    session = AsyncMock()
    svc = DataFilingService(session)
    svc.config_repo = AsyncMock()
    svc.submission_repo = AsyncMock()
    svc.audit_repo = AsyncMock()
    return svc


# ---------------------------------------------------------------------------
# 1. Model field checks
# ---------------------------------------------------------------------------


class TestFilingConfigModelFields:
    def test_config_has_expected_columns(self):
        mapper = FilingConfig.__table__.columns
        expected = [
            "id", "name", "status", "target_datasource_id", "target_table",
            "form_schema", "field_mapping", "idempotency_window_seconds",
            "oid", "creator_uid", "create_time", "update_time",
        ]
        for col_name in expected:
            assert col_name in mapper, f"Missing column: {col_name}"

    def test_submission_has_expected_columns(self):
        mapper = FilingSubmission.__table__.columns
        expected = [
            "id", "filing_id", "payload_hash", "payload", "status",
            "error_message", "submitter_uid", "retry_count",
            "create_time", "update_time",
        ]
        for col_name in expected:
            assert col_name in mapper, f"Missing column: {col_name}"

    def test_audit_has_expected_columns(self):
        mapper = FilingAudit.__table__.columns
        expected = [
            "id", "filing_id", "submission_id", "action", "actor_uid",
            "details", "outcome", "error_code", "create_time",
        ]
        for col_name in expected:
            assert col_name in mapper, f"Missing column: {col_name}"


# ---------------------------------------------------------------------------
# 2. Config status transitions
# ---------------------------------------------------------------------------


class TestFilingConfigStatusTransitions:
    @pytest.mark.asyncio
    async def test_draft_to_published(self):
        svc = _mock_service()
        draft = _make_config(status="draft")
        svc.config_repo.get_by_id.return_value = draft
        published = _make_config(status="published")
        svc.config_repo.update.return_value = published
        svc.audit_repo.create.return_value = AsyncMock()

        result = await svc.publish_config(1001)
        assert isinstance(result, dict)
        assert result["status"] == "published"
        svc.config_repo.update.assert_called_once_with(1001, status="published")

    @pytest.mark.asyncio
    async def test_published_to_disabled(self):
        svc = _mock_service()
        published = _make_config(status="published")
        svc.config_repo.get_by_id.return_value = published
        disabled = _make_config(status="disabled")
        svc.config_repo.update.return_value = disabled
        svc.audit_repo.create.return_value = AsyncMock()

        result = await svc.disable_config(1001)
        assert isinstance(result, dict)
        assert result["status"] == "disabled"

    @pytest.mark.asyncio
    async def test_cannot_publish_non_draft(self):
        svc = _mock_service()
        already_published = _make_config(status="published")
        svc.config_repo.get_by_id.return_value = already_published

        result = await svc.publish_config(1001)
        assert isinstance(result, str)
        assert "draft" in result.lower()

    @pytest.mark.asyncio
    async def test_cannot_disable_non_published(self):
        svc = _mock_service()
        draft = _make_config(status="draft")
        svc.config_repo.get_by_id.return_value = draft

        result = await svc.disable_config(1001)
        assert isinstance(result, str)
        assert "published" in result.lower()


# ---------------------------------------------------------------------------
# 3. Feature disabled
# ---------------------------------------------------------------------------


class TestSubmitDataFeatureDisabled:
    @pytest.mark.asyncio
    async def test_returns_error_when_feature_off(self):
        svc = _mock_service()
        with patch("app.services.data_filing_service.is_feature_enabled", new_callable=AsyncMock, return_value=False):
            result = await svc.submit_data(1001, {"field1": "val"}, 42)
        assert isinstance(result, str)
        assert "disabled" in result.lower()


# ---------------------------------------------------------------------------
# 4. Cannot submit to non-published config
# ---------------------------------------------------------------------------


class TestSubmitDataNotPublished:
    @pytest.mark.asyncio
    async def test_cannot_submit_to_draft(self):
        svc = _mock_service()
        svc.config_repo.get_by_id.return_value = _make_config(status="draft")
        with patch("app.services.data_filing_service.is_feature_enabled", new_callable=AsyncMock, return_value=True):
            result = await svc.submit_data(1001, {"field1": "val"}, 42)
        assert isinstance(result, str)
        assert "not published" in result.lower()

    @pytest.mark.asyncio
    async def test_cannot_submit_to_disabled(self):
        svc = _mock_service()
        svc.config_repo.get_by_id.return_value = _make_config(status="disabled")
        with patch("app.services.data_filing_service.is_feature_enabled", new_callable=AsyncMock, return_value=True):
            result = await svc.submit_data(1001, {"field1": "val"}, 42)
        assert isinstance(result, str)
        assert "not published" in result.lower()


# ---------------------------------------------------------------------------
# 5. Idempotency check
# ---------------------------------------------------------------------------


class TestIdempotencyCheck:
    @pytest.mark.asyncio
    async def test_duplicate_rejected(self):
        svc = _mock_service()
        svc.config_repo.get_by_id.return_value = _make_config(status="published")
        # Simulate existing duplicate
        svc.submission_repo.get_by_hash.return_value = _make_submission()
        svc.audit_repo.create.return_value = AsyncMock()

        with patch("app.services.data_filing_service.is_feature_enabled", new_callable=AsyncMock, return_value=True):
            result = await svc.submit_data(1001, {"field1": "val"}, 42)
        assert isinstance(result, str)
        assert "duplicate" in result.lower()


# ---------------------------------------------------------------------------
# 6. Payload validation
# ---------------------------------------------------------------------------


class TestValidatePayload:
    def test_missing_required_field(self):
        schema = {
            "fields": [
                {"name": "email", "required": True},
                {"name": "name", "required": False},
            ]
        }
        error = DataFilingService._validate_payload(schema, {"name": "Alice"})
        assert error is not None
        assert "email" in error

    def test_all_required_present(self):
        schema = {
            "fields": [
                {"name": "email", "required": True},
            ]
        }
        error = DataFilingService._validate_payload(schema, {"email": "a@b.com"})
        assert error is None

    def test_empty_schema_passes(self):
        error = DataFilingService._validate_payload({}, {"anything": "goes"})
        assert error is None


# ---------------------------------------------------------------------------
# 7. Audit record created on submit
# ---------------------------------------------------------------------------


class TestAuditOnSubmit:
    @pytest.mark.asyncio
    async def test_audit_created_on_successful_submit(self):
        svc = _mock_service()
        svc.config_repo.get_by_id.return_value = _make_config(status="published")
        svc.submission_repo.get_by_hash.return_value = None  # no duplicate
        svc.submission_repo.create.return_value = _make_submission()
        svc.audit_repo.create.return_value = AsyncMock()

        with patch("app.services.data_filing_service.is_feature_enabled", new_callable=AsyncMock, return_value=True):
            result = await svc.submit_data(1001, {"field1": "val"}, 42)

        assert isinstance(result, dict)
        svc.audit_repo.create.assert_called_once()
        call_kwargs = svc.audit_repo.create.call_args[1]
        assert call_kwargs["action"] == "submit"
        assert call_kwargs["outcome"] == "success"


# ---------------------------------------------------------------------------
# 8. Retry submission
# ---------------------------------------------------------------------------


class TestRetrySubmission:
    @pytest.mark.asyncio
    async def test_retry_resets_status(self):
        svc = _mock_service()
        failed = _make_submission(status="failed", retry_count=0)
        svc.submission_repo.get_by_id.return_value = failed
        retried = _make_submission(status="retrying", retry_count=1)
        svc.submission_repo.update_status.return_value = retried
        svc.audit_repo.create.return_value = AsyncMock()

        result = await svc.retry_submission(2001)
        assert isinstance(result, dict)
        assert result["status"] == "retrying"
        svc.submission_repo.update_status.assert_called_once_with(2001, "retrying", retry_count=1)

    @pytest.mark.asyncio
    async def test_cannot_retry_non_failed(self):
        svc = _mock_service()
        success = _make_submission(status="success")
        svc.submission_repo.get_by_id.return_value = success

        result = await svc.retry_submission(2001)
        assert isinstance(result, str)
        assert "failed" in result.lower()


# ---------------------------------------------------------------------------
# 9. All routes require auth
# ---------------------------------------------------------------------------


class TestAllRoutesRequireAuth:
    """Verify every data-filing route has get_current_user dependency."""

    def test_all_routes_require_auth(self):
        from app.routers.data_filing import router

        for route in router.routes:
            # Check that every route has a dependency that calls get_current_user
            deps = getattr(route, "dependant", None)
            assert deps is not None, f"Route {route.path} has no dependant"
            # Look for get_current_user in the dependencies
            dep_names = []
            for dep in deps.dependencies:
                if dep.call is not None:
                    dep_names.append(getattr(dep.call, "__name__", str(dep.call)))
            assert "get_current_user" in dep_names, (
                f"Route {route.path} does not require auth. Dependencies: {dep_names}"
            )
