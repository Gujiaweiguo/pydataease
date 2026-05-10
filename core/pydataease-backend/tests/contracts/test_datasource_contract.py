from __future__ import annotations

import pytest

from app.services.datasource_service import get_datasource_service
from tests.test_datasource_routes import FakeDatasourceService


@pytest.fixture
def fake_service(install_override) -> FakeDatasourceService:
    service = FakeDatasourceService()
    install_override(get_datasource_service, service)
    return service


@pytest.mark.usefixtures("fake_service")
class TestDatasourceCrudContract:
    async def test_tree_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/datasource/tree should require X-DE-TOKEN, accept BusiNodeRequest, and return datasource tree nodes in ResultMessage.data."""
        response = await async_client.get("/de2api/datasource/query/ware", headers=auth_headers)

        assert response.status_code == 200
        assert response.json()["code"] == 0
        assert response.json()["data"][0]["name"] == "ware-warehouse"

    async def test_tree_auth_failure_contract(self, async_client) -> None:
        """POST /de2api/datasource/tree should fail when auth token is missing, invalid, or expired."""
        response = await async_client.get("/de2api/datasource/query/ware")

        assert response.status_code == 401

    async def test_save_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/datasource/save should create datasource from BusiDsRequest and return DatasourceDTO in ResultMessage.data."""
        response = await async_client.post(
            "/de2api/datasource/save",
            headers=auth_headers,
            json={
                "name": "warehouse",
                "type": "pg",
                "configuration": {
                    "host": "db",
                    "port": 5432,
                    "username": "demo",
                    "password": "pwd",
                    "database": "analytics",
                    "schema": "public",
                },
                "description": "created",
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["msg"] == "success"
        assert body["data"]["id"] == 202
        assert body["data"]["name"] == "warehouse"
        assert body["data"]["type"] == "pg"
        assert body["data"]["configuration"] == {"host": "db", "database": "analytics", "schema": "public"}
        assert body["data"]["description"] == "created"

    async def test_save_auth_failure_contract(self, async_client) -> None:
        """POST /de2api/datasource/save should fail when auth token is missing, invalid, or expired."""
        response = await async_client.post("/de2api/datasource/save", json={"name": "warehouse", "type": "pg", "configuration": {}})

        assert response.status_code == 401

    async def test_update_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/datasource/update should update datasource from BusiDsRequest and return DatasourceDTO."""
        response = await async_client.post(
            "/de2api/datasource/update",
            headers=auth_headers,
            json={
                "id": 202,
                "name": "warehouse-updated",
                "configuration": {
                    "host": "db",
                    "port": 5432,
                    "username": "demo",
                    "password": "pwd",
                    "database": "analytics",
                    "schema": "public",
                },
            },
        )

        assert response.status_code == 200
        assert response.json()["code"] == 0
        assert response.json()["data"]["name"] == "warehouse-updated"

    async def test_update_auth_failure_contract(self, async_client) -> None:
        """POST /de2api/datasource/update should fail when auth token is missing, invalid, or expired."""
        response = await async_client.post("/de2api/datasource/update", json={"id": 202, "name": "warehouse-updated", "configuration": {}})

        assert response.status_code == 401

    async def test_delete_success_contract(self, async_client, auth_headers, fake_service: FakeDatasourceService) -> None:
        """GET /de2api/datasource/delete/{datasourceId} should delete datasource and return success ResultMessage."""
        response = await async_client.post("/de2api/datasource/delete/202", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == {"code": 0, "data": None, "msg": "success"}
        assert fake_service.deleted_ids == [202]

    async def test_delete_auth_failure_contract(self, async_client) -> None:
        """GET /de2api/datasource/delete/{datasourceId} should fail when auth token is missing, invalid, or expired."""
        response = await async_client.post("/de2api/datasource/delete/202")

        assert response.status_code == 401


@pytest.mark.usefixtures("fake_service")
class TestDatasourceValidationContract:
    async def test_validate_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/datasource/validate should validate connection request and return DatasourceDTO diagnostic payload."""
        response = await async_client.post(
            "/de2api/datasource/validate",
            headers=auth_headers,
            json={
                "name": "warehouse",
                "type": "pg",
                "configuration": {
                    "host": "db",
                    "port": 5432,
                    "username": "demo",
                    "password": "pwd",
                    "database": "analytics",
                    "schema": "public",
                },
            },
        )

        assert response.status_code == 200
        assert response.json() == {
            "code": 0,
            "data": {"success": True, "message": "Connection successful", "datasource_type": "pg"},
            "msg": "success",
        }

    @pytest.mark.skip(reason="Endpoint not yet implemented")
    async def test_upload_file_success_contract(self) -> None:
        """POST /de2api/datasource/uploadFile should accept multipart file,id,editType and return parsed ExcelFileData in ResultMessage.data."""
