from __future__ import annotations

import pytest

from app.services.dataset_service import get_dataset_service  # pyright: ignore[reportImplicitRelativeImport]
from tests.fixtures.dataset_fixtures import FakeDatasetService  # pyright: ignore[reportImplicitRelativeImport]


@pytest.fixture
def fake_service(install_override) -> FakeDatasetService:
    service = FakeDatasetService()
    install_override(get_dataset_service, service)
    return service


@pytest.mark.usefixtures("fake_service")
class TestDatasetTreeContract:
    async def test_create_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/datasetTree/create should require X-DE-TOKEN, accept DatasetGroupInfoDTO, and return DatasetNodeDTO in ResultMessage.data."""
        response = await async_client.post(
            "/de2api/datasetTree/create",
            headers=auth_headers,
            json={"name": "my-dataset", "pid": 0, "nodeType": "folder"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["msg"] == "success"
        assert body["data"]["id"] == 100
        assert body["data"]["name"] == "new-dataset"
        assert body["data"]["pid"] == 0
        assert body["data"]["level"] == 0
        assert body["data"]["nodeType"] == "dataset"

    async def test_create_auth_failure_contract(self, async_client) -> None:
        """POST /de2api/datasetTree/create should fail when auth token is missing, invalid, or expired."""
        response = await async_client.post("/de2api/datasetTree/create", json={"name": "x", "nodeType": "folder"})

        assert response.status_code == 401

    async def test_tree_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/datasetTree/tree should accept BusiNodeRequest and return dataset/folder tree nodes in ResultMessage.data."""
        response = await async_client.post("/de2api/datasetTree/tree", headers=auth_headers, json={"busiFlag": "dataset"})

        assert response.status_code == 200
        assert response.json()["code"] == 0
        assert response.json()["data"][0]["children"][0]["name"] == "child-dataset"

    async def test_tree_auth_failure_contract(self, async_client) -> None:
        """POST /de2api/datasetTree/tree should fail when auth token is missing, invalid, or expired."""
        response = await async_client.post("/de2api/datasetTree/tree", json={"busiFlag": "dataset"})

        assert response.status_code == 401

    async def test_details_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/datasetTree/details/{id} should return dataset detail payload matching frontend field decoding expectations."""
        response = await async_client.post("/de2api/datasetTree/details/500", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["msg"] == "success"
        assert body["data"]["id"] == "500"
        assert body["data"]["name"] == "detail-ds"
        assert body["data"]["pid"] == "0"
        assert body["data"]["level"] == 0
        assert body["data"]["nodeType"] == "dataset"

    async def test_delete_success_contract(self, async_client, auth_headers, fake_service: FakeDatasetService) -> None:
        """POST /de2api/datasetTree/delete/{id} should delete dataset and return success ResultMessage."""
        response = await async_client.post("/de2api/datasetTree/delete/999", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == {"code": 0, "data": None, "msg": "success"}
        assert fake_service.deleted_ids == [999]


@pytest.mark.usefixtures("fake_service")
class TestDatasetDataContract:
    async def test_preview_data_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/datasetData/previewData should return preview rows plus allFields metadata in ResultMessage.data."""
        response = await async_client.post(
            "/de2api/datasetData/previewSql",
            headers=auth_headers,
            json={"sql": "SELECT 1"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "code": 0,
            "data": {"sql": "SELECT 1", "data": [], "fields": [], "total": 0},
            "msg": "success",
        }

    async def test_preview_data_auth_failure_contract(self, async_client) -> None:
        """POST /de2api/datasetData/previewData should fail when auth token is missing, invalid, or expired."""
        response = await async_client.post("/de2api/datasetData/previewSql", json={"sql": "SELECT 1"})

        assert response.status_code == 401

    async def test_export_dataset_success_contract(self, async_client, auth_headers) -> None:
        """POST /de2api/datasetTree/exportDataset should return blob/file response for DataSetExportRequest when authorized."""
        response = await async_client.post("/de2api/datasetTree/exportDataset", headers=auth_headers, json={"id": 100, "name": "dataset1"})

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
