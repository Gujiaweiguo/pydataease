"""Tests for data filing backbone: models, service, routes."""
# pyright: reportAttributeAccessIssue=false, reportCallIssue=false, reportArgumentType=false

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.data_filing import FilingAudit, FilingConfig, FilingSubmission
from app.schemas.data_filing import FilingConfigCreateRequest, FilingConfigUpdateRequest, FilingSubmitRequest
from app.services.data_filing_service import DataFilingService, get_data_filing_service
from tests.fixtures.auth_fixtures import _build_token


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
    for key, value in defaults.items():
        setattr(cfg, key, value)
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
    submission = MagicMock(spec=FilingSubmission)
    for key, value in defaults.items():
        setattr(submission, key, value)
    return submission


def _make_datasource(**overrides) -> MagicMock:
    defaults = {
        "id": 3001,
        "name": "target-ds",
        "type": "pg",
        "configuration": {"host": "localhost", "database": "demo"},
    }
    defaults.update(overrides)
    datasource = MagicMock()
    for key, value in defaults.items():
        setattr(datasource, key, value)
    return datasource


def _mock_service() -> DataFilingService:
    session = AsyncMock()
    svc = DataFilingService(session)
    svc.config_repo = AsyncMock()
    svc.submission_repo = AsyncMock()
    svc.audit_repo = AsyncMock()
    return svc


class TestFilingConfigModelFields:
    def test_config_has_expected_columns(self):
        mapper = FilingConfig.__table__.columns
        expected = [
            "id",
            "name",
            "status",
            "target_datasource_id",
            "target_table",
            "form_schema",
            "field_mapping",
            "idempotency_window_seconds",
            "oid",
            "creator_uid",
            "create_time",
            "update_time",
        ]
        for col_name in expected:
            assert col_name in mapper, f"Missing column: {col_name}"

    def test_submission_has_expected_columns(self):
        mapper = FilingSubmission.__table__.columns
        expected = [
            "id",
            "filing_id",
            "payload_hash",
            "payload",
            "status",
            "error_message",
            "submitter_uid",
            "retry_count",
            "create_time",
            "update_time",
        ]
        for col_name in expected:
            assert col_name in mapper, f"Missing column: {col_name}"

    def test_audit_has_expected_columns(self):
        mapper = FilingAudit.__table__.columns
        expected = [
            "id",
            "filing_id",
            "submission_id",
            "action",
            "actor_uid",
            "details",
            "outcome",
            "error_code",
            "create_time",
        ]
        for col_name in expected:
            assert col_name in mapper, f"Missing column: {col_name}"


class TestSchemas:
    def test_create_request_accepts_camel_and_snake_case(self):
        model = FilingConfigCreateRequest.model_validate(
            {
                "name": "demo",
                "targetDatasourceId": 1,
                "target_table": "orders",
                "formSchema": {"fields": []},
                "field_mapping": {"formField": "column_a"},
            }
        )

        dumped = model.model_dump(by_alias=True)
        assert dumped["targetDatasourceId"] == 1
        assert dumped["targetTable"] == "orders"
        assert dumped["fieldMapping"] == {"formField": "column_a"}

    def test_update_request_excludes_unset_fields(self):
        model = FilingConfigUpdateRequest.model_validate({"target_datasource_id": 9})
        assert model.model_dump(by_alias=True, exclude_unset=True) == {"targetDatasourceId": 9}

    def test_submit_request_allows_dynamic_fields(self):
        model = FilingSubmitRequest.model_validate({"anyField": "value", "another": 1})
        assert model.model_dump() == {"anyField": "value", "another": 1}


class TestFilingConfigStatusTransitions:
    @pytest.mark.asyncio
    async def test_draft_to_published(self):
        svc = _mock_service()
        svc.config_repo.get_by_id.return_value = _make_config(status="draft")
        svc.config_repo.update.return_value = _make_config(status="published")
        svc.audit_repo.create.return_value = AsyncMock()

        result = await svc.publish_config(1001)
        assert isinstance(result, dict)
        assert result["status"] == "published"
        svc.config_repo.update.assert_called_once_with(1001, status="published")

    @pytest.mark.asyncio
    async def test_published_to_disabled(self):
        svc = _mock_service()
        svc.config_repo.get_by_id.return_value = _make_config(status="published")
        svc.config_repo.update.return_value = _make_config(status="disabled")
        svc.audit_repo.create.return_value = AsyncMock()

        result = await svc.disable_config(1001)
        assert isinstance(result, dict)
        assert result["status"] == "disabled"

    @pytest.mark.asyncio
    async def test_delete_draft_config(self):
        svc = _mock_service()
        svc.config_repo.get_by_id.return_value = _make_config(status="draft")
        svc.config_repo.delete.return_value = True

        result = await svc.delete_config(1001)
        assert result is True
        svc.config_repo.delete.assert_awaited_once_with(1001)

    @pytest.mark.asyncio
    async def test_cannot_publish_non_draft(self):
        svc = _mock_service()
        svc.config_repo.get_by_id.return_value = _make_config(status="published")

        result = await svc.publish_config(1001)
        assert isinstance(result, str)
        assert "draft" in result.lower()

    @pytest.mark.asyncio
    async def test_cannot_disable_non_published(self):
        svc = _mock_service()
        svc.config_repo.get_by_id.return_value = _make_config(status="draft")

        result = await svc.disable_config(1001)
        assert isinstance(result, str)
        assert "published" in result.lower()

    @pytest.mark.asyncio
    async def test_cannot_delete_non_draft(self):
        svc = _mock_service()
        svc.config_repo.get_by_id.return_value = _make_config(status="published")

        result = await svc.delete_config(1001)
        assert isinstance(result, str)
        assert "draft" in result.lower()


class TestSubmitDataFeatureDisabled:
    @pytest.mark.asyncio
    async def test_returns_error_when_feature_off(self):
        svc = _mock_service()
        with patch("app.services.data_filing_service.is_feature_enabled", new_callable=AsyncMock, return_value=False):
            result = await svc.submit_data(1001, {"field1": "val"}, 42)
        assert isinstance(result, str)
        assert "disabled" in result.lower()


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


class TestIdempotencyCheck:
    @pytest.mark.asyncio
    async def test_duplicate_rejected(self):
        svc = _mock_service()
        svc.config_repo.get_by_id.return_value = _make_config(status="published")
        svc.submission_repo.get_by_hash.return_value = _make_submission()
        svc.audit_repo.create.return_value = AsyncMock()

        with patch("app.services.data_filing_service.is_feature_enabled", new_callable=AsyncMock, return_value=True):
            result = await svc.submit_data(1001, {"field1": "val"}, 42)
        assert isinstance(result, str)
        assert "duplicate" in result.lower()


class TestValidatePayload:
    def test_missing_required_field(self):
        schema = {"fields": [{"name": "email", "required": True}, {"name": "name", "required": False}]}
        error = DataFilingService._validate_payload(schema, {"name": "Alice"})
        assert error is not None
        assert "email" in error

    def test_all_required_present(self):
        schema = {"fields": [{"name": "email", "required": True}]}
        error = DataFilingService._validate_payload(schema, {"email": "a@b.com"})
        assert error is None

    def test_empty_schema_passes(self):
        error = DataFilingService._validate_payload({}, {"anything": "goes"})
        assert error is None


class TestWriteBackExecution:
    @pytest.mark.asyncio
    async def test_submit_writes_to_datasource_and_marks_success(self):
        svc = _mock_service()
        config = _make_config(
            status="published",
            target_datasource_id=3001,
            target_table="orders",
            field_mapping={"formField": "target_col"},
        )
        svc.config_repo.get_by_id.return_value = config
        svc.submission_repo.get_by_hash.return_value = None
        svc.submission_repo.create.return_value = _make_submission(status="pending", payload={"formField": "value"})
        svc.submission_repo.update_status.return_value = _make_submission(status="success", payload={"formField": "value"})
        svc.audit_repo.create.return_value = AsyncMock()

        conn = AsyncMock()
        with (
            patch("app.services.data_filing_service.is_feature_enabled", new_callable=AsyncMock, return_value=True),
            patch("app.services.data_filing_service.DatasourceRepository") as repo_cls,
            patch("app.services.data_filing_service.open_connection", new=AsyncMock(return_value=conn)),
        ):
            repo_cls.return_value.get_by_id = AsyncMock(return_value=_make_datasource())
            result = await svc.submit_data(1001, {"formField": "value"}, 42)

        assert isinstance(result, dict)
        assert result["status"] == "success"
        conn.execute.assert_awaited_once_with('INSERT INTO "orders" ("target_col") VALUES ($1)', "value")
        conn.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_submit_write_failure_marks_failed(self):
        svc = _mock_service()
        svc.config_repo.get_by_id.return_value = _make_config(status="published")
        svc.submission_repo.get_by_hash.return_value = None
        svc.submission_repo.create.return_value = _make_submission(status="pending")
        svc.submission_repo.update_status.return_value = _make_submission(status="failed", error_message="boom")
        svc.audit_repo.create.return_value = AsyncMock()

        with (
            patch("app.services.data_filing_service.is_feature_enabled", new_callable=AsyncMock, return_value=True),
            patch.object(svc, "_write_to_datasource", new=AsyncMock(side_effect=RuntimeError("boom"))),
        ):
            result = await svc.submit_data(1001, {"field1": "val"}, 42)

        assert isinstance(result, dict)
        assert result["status"] == "failed"
        assert result["errorMessage"] == "boom"

    @pytest.mark.asyncio
    async def test_retry_executes_write_back_and_marks_success(self):
        svc = _mock_service()
        failed = _make_submission(status="failed", retry_count=0)
        svc.submission_repo.get_by_id.return_value = failed
        svc.config_repo.get_by_id.return_value = _make_config(status="published")
        svc.submission_repo.update_status.side_effect = [
            _make_submission(status="retrying", retry_count=1),
            _make_submission(status="success", retry_count=1),
        ]
        svc.audit_repo.create.return_value = AsyncMock()

        with patch.object(svc, "_write_to_datasource", new=AsyncMock()) as write_mock:
            result = await svc.retry_submission(2001)

        assert isinstance(result, dict)
        assert result["status"] == "success"
        write_mock.assert_awaited_once_with(svc.config_repo.get_by_id.return_value, failed.payload)

    @pytest.mark.asyncio
    async def test_retry_failure_marks_failed_and_increments_retry_count(self):
        svc = _mock_service()
        failed = _make_submission(status="failed", retry_count=1)
        svc.submission_repo.get_by_id.return_value = failed
        svc.config_repo.get_by_id.return_value = _make_config(status="published")
        svc.submission_repo.update_status.side_effect = [
            _make_submission(status="retrying", retry_count=2),
            _make_submission(status="failed", retry_count=2, error_message="boom"),
        ]
        svc.audit_repo.create.return_value = AsyncMock()

        with patch.object(svc, "_write_to_datasource", new=AsyncMock(side_effect=RuntimeError("boom"))):
            result = await svc.retry_submission(2001)

        assert isinstance(result, dict)
        assert result["status"] == "failed"
        assert result["retryCount"] == 2
        assert result["errorMessage"] == "boom"


class TestAuditOnSubmit:
    @pytest.mark.asyncio
    async def test_audit_created_on_successful_submit(self):
        svc = _mock_service()
        svc.config_repo.get_by_id.return_value = _make_config(status="published")
        svc.submission_repo.get_by_hash.return_value = None
        svc.submission_repo.create.return_value = _make_submission(status="pending")
        svc.submission_repo.update_status.return_value = _make_submission(status="success")
        svc.audit_repo.create.return_value = AsyncMock()

        with (
            patch("app.services.data_filing_service.is_feature_enabled", new_callable=AsyncMock, return_value=True),
            patch.object(svc, "_write_to_datasource", new=AsyncMock()),
        ):
            result = await svc.submit_data(1001, {"field1": "val"}, 42)

        assert isinstance(result, dict)
        svc.audit_repo.create.assert_called_once()
        call_kwargs = svc.audit_repo.create.call_args.kwargs
        assert call_kwargs["action"] == "submit"
        assert call_kwargs["outcome"] == "success"


class TestRetrySubmission:
    @pytest.mark.asyncio
    async def test_cannot_retry_non_failed(self):
        svc = _mock_service()
        svc.submission_repo.get_by_id.return_value = _make_submission(status="success")

        result = await svc.retry_submission(2001)
        assert isinstance(result, str)
        assert "failed" in result.lower()


class FakeDataFilingService:
    def __init__(self) -> None:
        self.deleted: list[int] = []

    async def list_configs(self, status: str | None = None) -> list[dict[str, object]]:
        return []

    async def get_config(self, filing_id: int) -> dict[str, object]:
        return {"id": filing_id}

    async def create_config(self, payload: dict[str, object]) -> dict[str, object]:
        return payload

    async def update_config(self, filing_id: int, payload: dict[str, object]) -> dict[str, object]:
        return {"id": filing_id, **payload}

    async def delete_config(self, filing_id: int) -> bool:
        self.deleted.append(filing_id)
        return True

    async def publish_config(self, filing_id: int) -> dict[str, object]:
        return {"id": filing_id}

    async def disable_config(self, filing_id: int) -> dict[str, object]:
        return {"id": filing_id}

    async def submit_data(self, filing_id: int, payload: dict[str, object], submitter_uid: int) -> dict[str, object]:
        return {"id": filing_id, "payload": payload, "submitterUid": submitter_uid}

    async def list_submissions(self, filing_id: int) -> list[dict[str, object]]:
        return []

    async def get_submission(self, submission_id: int) -> dict[str, object]:
        return {"id": submission_id}

    async def retry_submission(self, submission_id: int) -> dict[str, object]:
        return {"id": submission_id}

    async def list_audit(self, filing_id: int) -> list[dict[str, object]]:
        return []


class TestDeleteRoute:
    @pytest.mark.asyncio
    async def test_delete_route_calls_service(self):
        fake = FakeDataFilingService()
        app.dependency_overrides[get_data_filing_service] = lambda: fake
        headers = {"X-DE-TOKEN": _build_token(uid=1, oid=1)}
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.delete("/de2api/data-filing/config/123", headers=headers)
            assert response.status_code == 200
            assert response.json()["data"] is True
            assert fake.deleted == [123]
        finally:
            app.dependency_overrides.clear()


class TestAllRoutesRequireAuth:
    def test_all_routes_require_auth(self):
        from app.routers.data_filing import router

        for route in router.routes:
            deps = getattr(route, "dependant", None)
            assert deps is not None, f"Route {route.path} has no dependant"
            dep_names = []
            for dep in deps.dependencies:
                if dep.call is not None:
                    dep_names.append(getattr(dep.call, "__name__", str(dep.call)))
            assert "get_current_user" in dep_names, (
                f"Route {route.path} does not require auth. Dependencies: {dep_names}"
            )
