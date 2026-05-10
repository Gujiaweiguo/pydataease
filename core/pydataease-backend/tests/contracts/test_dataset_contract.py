class TestDatasetTreeContract:
    def test_create_success_contract(self) -> None:
        """POST /de2api/datasetTree/create should require X-DE-TOKEN, accept DatasetGroupInfoDTO, and return DatasetNodeDTO in ResultMessage.data."""
        raise NotImplementedError

    def test_create_auth_failure_contract(self) -> None:
        """POST /de2api/datasetTree/create should fail when auth token is missing, invalid, or expired."""
        raise NotImplementedError

    def test_tree_success_contract(self) -> None:
        """POST /de2api/datasetTree/tree should accept BusiNodeRequest and return dataset/folder tree nodes in ResultMessage.data."""
        raise NotImplementedError

    def test_tree_auth_failure_contract(self) -> None:
        """POST /de2api/datasetTree/tree should fail when auth token is missing, invalid, or expired."""
        raise NotImplementedError

    def test_details_success_contract(self) -> None:
        """POST /de2api/datasetTree/details/{id} should return dataset detail payload matching frontend field decoding expectations."""
        raise NotImplementedError

    def test_delete_success_contract(self) -> None:
        """POST /de2api/datasetTree/delete/{id} should delete dataset and return success ResultMessage."""
        raise NotImplementedError


class TestDatasetDataContract:
    def test_preview_data_success_contract(self) -> None:
        """POST /de2api/datasetData/previewData should return preview rows plus allFields metadata in ResultMessage.data."""
        raise NotImplementedError

    def test_preview_data_auth_failure_contract(self) -> None:
        """POST /de2api/datasetData/previewData should fail when auth token is missing, invalid, or expired."""
        raise NotImplementedError

    def test_export_dataset_success_contract(self) -> None:
        """POST /de2api/datasetTree/exportDataset should return blob/file response for DataSetExportRequest when authorized."""
        raise NotImplementedError
