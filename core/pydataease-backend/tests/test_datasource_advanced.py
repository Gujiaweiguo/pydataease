from __future__ import annotations

# pyright: reportMissingTypeArgument=false, reportCallIssue=false

from collections.abc import Generator

import pytest
from httpx import AsyncClient

from app.main import app  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.datasource import DatasourceResponse, DatasourceSimpleResponse, DatasourceTableResponse  # pyright: ignore[reportImplicitRelativeImport]
from app.services.datasource_service import get_datasource_service  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.auth_fixtures import _build_token  # pyright: ignore[reportImplicitRelativeImport]


class FakeAdvancedDatasourceService:
    def __init__(self) -> None:
        self.moved: list[tuple[int, int]] = []
        self.renamed: list[tuple[int, str]] = []
        self.created_folders: list[tuple[str, int, TokenUser]] = []

    async def move(self, datasource_id: int, pid: int) -> None:
        self.moved.append((datasource_id, pid))

    async def rename(self, datasource_id: int, name: str) -> None:
        self.renamed.append((datasource_id, name))

    async def create_folder(self, name: str, pid: int, user: TokenUser) -> DatasourceResponse:
        self.created_folders.append((name, pid, user))
        return DatasourceResponse(
            id=999,
            name=name,
            type="folder",
            configuration={},
            description=None,
            pid=pid if pid != 0 else None,
            edit_type=None,
            create_time=100,
            update_time=100,
            update_by=user.user_id,
            create_by=str(user.user_id),
            status="Success",
            qrtz_instance=None,
            task_status="WaitingForExecution",
            enable_data_fill=None,
        )

    async def get_full(self, datasource_id: int) -> DatasourceResponse:
        return DatasourceResponse(
            id=datasource_id,
            name="test-ds",
            type="pg",
            configuration={"host": "db", "port": 5432, "username": "admin", "password": "secret123"},
            description="test description",
            pid=None,
            edit_type=None,
            create_time=100,
            update_time=200,
            update_by=7,
            create_by="7",
            status="Success",
            qrtz_instance=None,
            task_status="WaitingForExecution",
            enable_data_fill=False,
        )

    async def get_hide_pw(self, datasource_id: int) -> DatasourceResponse:
        return DatasourceResponse(
            id=datasource_id,
            name="test-ds",
            type="pg",
            configuration={"host": "db", "port": 5432, "username": "admin", "password": "******"},
            description="test description",
            pid=None,
            edit_type=None,
            create_time=100,
            update_time=200,
            update_by=7,
            create_by="7",
            status="Success",
            qrtz_instance=None,
            task_status="WaitingForExecution",
            enable_data_fill=False,
        )

    async def get_simple(self, datasource_id: int) -> DatasourceSimpleResponse:
        return DatasourceSimpleResponse(
            id=datasource_id,
            name="test-ds",
            type="pg",
            description="test description",
        )

    async def validate_by_id(self, datasource_id: int) -> dict[str, str]:
        return {"status": "Success"}

    async def check_in_use(self, datasource_id: int) -> bool:
        return datasource_id == 100

    async def get_tables(self, datasource_id: int) -> list[DatasourceTableResponse]:
        return [DatasourceTableResponse(name="orders", schema_name="public")]

    # Required by existing endpoints that may be tested
    async def tree(self) -> list[dict]:
        return []

    async def query(self, keyword: str) -> list:
        return []

    async def save(self, payload: object, user: TokenUser) -> DatasourceResponse:
        return DatasourceResponse(
            id=1, name="x", type="pg", configuration={}, description=None,
            pid=None, edit_type=None, create_time=1, update_time=1,
            update_by=1, create_by="1", status="Success", qrtz_instance=None,
            task_status="WaitingForExecution", enable_data_fill=False,
        )

    async def update(self, payload: object, user: TokenUser) -> DatasourceResponse:
        return DatasourceResponse(
            id=1, name="x", type="pg", configuration={}, description=None,
            pid=None, edit_type=None, create_time=1, update_time=1,
            update_by=1, create_by="1", status="Success", qrtz_instance=None,
            task_status="WaitingForExecution", enable_data_fill=False,
        )

    async def delete(self, datasource_id: int) -> None:
        pass

    async def validate(self, payload: object) -> object:
        return object()

    async def get_fields(self, datasource_id: int, table_name: str) -> list:
        return []

    async def latest_use(self) -> list[str]:
        return []

    async def upload_file(self, file: object, id: str | None = None, edit_type: str | None = None) -> dict:
        return {}

    async def get_schemas_from_config(self, configuration: dict, ds_type: str = "postgresql") -> list[str]:
        return []


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": _build_token(uid=7, oid=9)}


@pytest.fixture
def fake_service() -> Generator[FakeAdvancedDatasourceService, None, None]:
    service = FakeAdvancedDatasourceService()
    app.dependency_overrides[get_datasource_service] = lambda: service
    yield service
    _ = app.dependency_overrides.pop(get_datasource_service, None)


@pytest.mark.asyncio
async def test_move_datasource(
    client: AsyncClient, auth_headers: dict[str, str], fake_service: FakeAdvancedDatasourceService
) -> None:
    response = await client.post(
        "/de2api/datasource/move",
        headers=auth_headers,
        json={"id": 42, "pid": 10},
    )
    assert response.status_code == 200
    assert response.json()["data"] is None
    assert fake_service.moved == [(42, 10)]


@pytest.mark.asyncio
async def test_rename_datasource(
    client: AsyncClient, auth_headers: dict[str, str], fake_service: FakeAdvancedDatasourceService
) -> None:
    response = await client.post(
        "/de2api/datasource/reName",
        headers=auth_headers,
        json={"id": 42, "name": "new-name"},
    )
    assert response.status_code == 200
    assert response.json()["data"] is None
    assert fake_service.renamed == [(42, "new-name")]


@pytest.mark.asyncio
async def test_list_datasource_types(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    response = await client.get("/de2api/datasource/types", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 6
    types_list = [item["type"] for item in data]
    assert "mysql" in types_list
    assert "pg" in types_list
    assert "Excel" in types_list
    assert "ExcelRemote" in types_list
    assert data[0] == {"type": "folder", "name": "folder", "category": "folder"}


@pytest.mark.asyncio
async def test_get_tables_post(
    client: AsyncClient, auth_headers: dict[str, str], fake_service: FakeAdvancedDatasourceService
) -> None:
    response = await client.post(
        "/de2api/datasource/getTables",
        headers=auth_headers,
        json={"datasourceId": 42},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "orders"


@pytest.mark.asyncio
async def test_validate_by_id(
    client: AsyncClient, auth_headers: dict[str, str], fake_service: FakeAdvancedDatasourceService
) -> None:
    response = await client.get("/de2api/datasource/validate/42", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"] == {"status": "Success"}


@pytest.mark.asyncio
async def test_get_datasource(
    client: AsyncClient, auth_headers: dict[str, str], fake_service: FakeAdvancedDatasourceService
) -> None:
    response = await client.get("/de2api/datasource/get/42", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 42
    assert data["name"] == "test-ds"
    assert data["configuration"]["password"] == "secret123"


@pytest.mark.asyncio
async def test_get_datasource_hide_pw(
    client: AsyncClient, auth_headers: dict[str, str], fake_service: FakeAdvancedDatasourceService
) -> None:
    response = await client.get("/de2api/datasource/hidePw/42", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["configuration"]["password"] == "******"


@pytest.mark.asyncio
async def test_create_folder(
    client: AsyncClient, auth_headers: dict[str, str], fake_service: FakeAdvancedDatasourceService
) -> None:
    response = await client.post(
        "/de2api/datasource/createFolder",
        headers=auth_headers,
        json={"name": "My Folder", "pid": 5},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 999
    assert data["name"] == "My Folder"
    assert data["type"] == "folder"
    assert len(fake_service.created_folders) == 1


@pytest.mark.asyncio
async def test_pre_delete_in_use(
    client: AsyncClient, auth_headers: dict[str, str], fake_service: FakeAdvancedDatasourceService
) -> None:
    response = await client.post("/de2api/datasource/perDelete/100", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"] == {"inUse": True}


@pytest.mark.asyncio
async def test_pre_delete_not_in_use(
    client: AsyncClient, auth_headers: dict[str, str], fake_service: FakeAdvancedDatasourceService
) -> None:
    response = await client.post("/de2api/datasource/perDelete/200", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["data"] == {"inUse": False}


@pytest.mark.asyncio
async def test_get_simple_datasource(
    client: AsyncClient, auth_headers: dict[str, str], fake_service: FakeAdvancedDatasourceService
) -> None:
    response = await client.get("/de2api/datasource/getSimpleDs/42", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 42
    assert data["name"] == "test-ds"
    assert data["type"] == "pg"
    assert data["description"] == "test description"
    assert "configuration" not in data


@pytest.mark.asyncio
async def test_types_require_auth(client: AsyncClient) -> None:
    response = await client.get("/de2api/datasource/types")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_move_requires_auth(client: AsyncClient) -> None:
    response = await client.post("/de2api/datasource/move", json={"id": 1, "pid": 2})
    assert response.status_code == 401
