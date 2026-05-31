from __future__ import annotations

from collections.abc import Generator
from typing import cast

import pytest
from fastapi import HTTPException  # pyright: ignore[reportMissingImports]
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.export import ExportTaskResponse  # pyright: ignore[reportImplicitRelativeImport]
from app.services.dataset_service import get_dataset_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.datasource_service import get_datasource_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.export_service import get_export_service  # pyright: ignore[reportImplicitRelativeImport]
from app.services.permission_service import PermissionService, get_permission_service  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.dataset_fixtures import FakeDatasetService  # pyright: ignore[reportImplicitRelativeImport]


class RecordingPermissionService:
    def __init__(self, grants: dict[tuple[str, str], bool] | None = None) -> None:
        self.grants = grants or {}
        self.calls: list[tuple[int, str, str]] = []

    async def require_resource_access(self, user: TokenUser, resource_type: str, permission_type: str = "use") -> None:
        self.calls.append((user.user_id, resource_type, permission_type))
        if user.user_id == 1:
            return None
        if not self.grants.get((resource_type, permission_type), False):
            raise HTTPException(status_code=403, detail="Access denied")

    async def has_resource_permission(self, user: TokenUser, resource_type: str, permission_type: str = "use") -> bool:
        self.calls.append((user.user_id, resource_type, permission_type))
        if user.user_id == 1:
            return True
        return self.grants.get((resource_type, permission_type), False)

    async def get_effective_menu_ids(self, _user_id: int, _oid: int) -> set[int]:
        return set()


class FakeDatasourceService:
    def __init__(self) -> None:
        self.queries: list[str] = []
        self.saved: list[object] = []

    async def query(self, keyword: str) -> list[dict[str, object]]:
        self.queries.append(keyword)
        return [{"id": 1, "name": keyword}]

    async def save(self, payload: object, user: TokenUser) -> dict[str, object]:
        self.saved.append((payload, user))
        return {"id": 10, "name": getattr(payload, "name", "saved")}


class FakeExportService:
    def __init__(self) -> None:
        self.created_tasks: list[tuple[object, TokenUser]] = []

    async def create_task(self, payload: object, user: TokenUser) -> ExportTaskResponse:
        self.created_tasks.append((payload, user))
        return ExportTaskResponse(
            id="task-1",
            user_id=user.user_id,
            file_name="export.xlsx",
            file_size=None,
            file_size_unit=None,
            export_from=getattr(payload, "export_from", None),
            export_status="INITIATED",
            export_from_type=getattr(payload, "export_from_type", None),
            export_time=1,
            export_progress="0",
            export_machine_name=None,
            params=getattr(payload, "params", {}),
            msg=None,
        )


@pytest.fixture
def dataset_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def admin_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=1, oid=1)}


@pytest.fixture
def fake_dataset_service() -> Generator[FakeDatasetService, None, None]:
    service = FakeDatasetService()
    app.dependency_overrides[get_dataset_service] = lambda: service
    yield service
    _ = app.dependency_overrides.pop(get_dataset_service, None)


@pytest.fixture
def fake_datasource_service() -> Generator[FakeDatasourceService, None, None]:
    service = FakeDatasourceService()
    app.dependency_overrides[get_datasource_service] = lambda: service
    yield service
    _ = app.dependency_overrides.pop(get_datasource_service, None)


@pytest.fixture
def fake_export_service() -> Generator[FakeExportService, None, None]:
    service = FakeExportService()
    app.dependency_overrides[get_export_service] = lambda: service
    yield service
    _ = app.dependency_overrides.pop(get_export_service, None)


def install_permission_override(service: RecordingPermissionService) -> None:
    app.dependency_overrides[get_permission_service] = lambda: service


def clear_permission_override() -> None:
    _ = app.dependency_overrides.pop(get_permission_service, None)


@pytest.mark.asyncio
async def test_non_admin_without_manage_permission_gets_403_on_dataset_mutation(
    client: AsyncClient,
    dataset_headers: dict[str, str],
    fake_dataset_service: FakeDatasetService,
) -> None:
    permission_service = RecordingPermissionService({("dataset", "view"): True})
    install_permission_override(permission_service)
    try:
        response = await client.post(
            "/de2api/datasetTree/create",
            headers=dataset_headers,
            json={"name": "blocked", "pid": 0, "nodeType": "folder"},
        )
    finally:
        clear_permission_override()

    assert response.status_code == 403
    assert response.json()["msg"] == "Access denied"
    assert fake_dataset_service.created == []


@pytest.mark.asyncio
async def test_non_admin_view_only_can_read_but_not_mutate_datasource(
    client: AsyncClient,
    dataset_headers: dict[str, str],
    fake_datasource_service: FakeDatasourceService,
) -> None:
    permission_service = RecordingPermissionService({("datasource", "view"): True})
    install_permission_override(permission_service)
    try:
        read_response = await client.get("/de2api/datasource/query/demo", headers=dataset_headers)
        mutate_response = await client.post(
            "/de2api/datasource/save",
            headers=dataset_headers,
            json={"name": "blocked", "type": "mysql", "configuration": {}},
        )
    finally:
        clear_permission_override()

    assert read_response.status_code == 200
    assert read_response.json()["data"][0]["name"] == "demo"
    assert mutate_response.status_code == 403
    assert fake_datasource_service.queries == ["demo"]
    assert fake_datasource_service.saved == []


@pytest.mark.asyncio
async def test_admin_user_can_mutate_and_export_without_explicit_grants(
    client: AsyncClient,
    admin_headers: dict[str, str],
    fake_dataset_service: FakeDatasetService,
    fake_export_service: FakeExportService,
) -> None:
    permission_service = RecordingPermissionService()
    install_permission_override(permission_service)
    try:
        mutate_response = await client.post(
            "/de2api/datasetTree/create",
            headers=admin_headers,
            json={"name": "allowed", "pid": 0, "nodeType": "folder"},
        )
        export_response = await client.post(
            "/de2api/exportCenter/exportTasks/create",
            headers=admin_headers,
            json={"exportFrom": 1, "exportFromType": "dataset", "params": {}},
        )
    finally:
        clear_permission_override()

    assert mutate_response.status_code == 200
    assert export_response.status_code == 200
    assert len(fake_dataset_service.created) == 1
    assert len(fake_export_service.created_tasks) == 1


@pytest.mark.asyncio
async def test_check_permission_returns_false_when_user_lacks_permission(
    client: AsyncClient,
    dataset_headers: dict[str, str],
) -> None:
    permission_service = RecordingPermissionService({("dataset", "view"): False})
    install_permission_override(permission_service)
    try:
        response = await client.post(
            "/de2api/resource/checkPermission/3?resource_type=dataset&permission_type=view",
            headers=dataset_headers,
        )
    finally:
        clear_permission_override()

    assert response.status_code == 200
    assert response.json()["data"] is False


@pytest.mark.asyncio
async def test_permission_service_skips_checks_when_enforcement_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(PermissionService, "_enforcement_enabled", staticmethod(lambda: False))
    service = PermissionService(session=cast(AsyncSession, object()))

    assert await service.has_resource_permission(TokenUser(user_id=7, oid=9), "dataset", "manage") is True
    await service.require_resource_access(TokenUser(user_id=7, oid=9), "dataset", "manage")
