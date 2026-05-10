class TestDatasourceCrudContract:
    def test_tree_success_contract(self) -> None:
        """POST /de2api/datasource/tree should require X-DE-TOKEN, accept BusiNodeRequest, and return datasource tree nodes in ResultMessage.data."""
        raise NotImplementedError

    def test_tree_auth_failure_contract(self) -> None:
        """POST /de2api/datasource/tree should fail when auth token is missing, invalid, or expired."""
        raise NotImplementedError

    def test_save_success_contract(self) -> None:
        """POST /de2api/datasource/save should create datasource from BusiDsRequest and return DatasourceDTO in ResultMessage.data."""
        raise NotImplementedError

    def test_save_auth_failure_contract(self) -> None:
        """POST /de2api/datasource/save should fail when auth token is missing, invalid, or expired."""
        raise NotImplementedError

    def test_update_success_contract(self) -> None:
        """POST /de2api/datasource/update should update datasource from BusiDsRequest and return DatasourceDTO."""
        raise NotImplementedError

    def test_update_auth_failure_contract(self) -> None:
        """POST /de2api/datasource/update should fail when auth token is missing, invalid, or expired."""
        raise NotImplementedError

    def test_delete_success_contract(self) -> None:
        """GET /de2api/datasource/delete/{datasourceId} should delete datasource and return success ResultMessage."""
        raise NotImplementedError

    def test_delete_auth_failure_contract(self) -> None:
        """GET /de2api/datasource/delete/{datasourceId} should fail when auth token is missing, invalid, or expired."""
        raise NotImplementedError


class TestDatasourceValidationContract:
    def test_validate_success_contract(self) -> None:
        """POST /de2api/datasource/validate should validate connection request and return DatasourceDTO diagnostic payload."""
        raise NotImplementedError

    def test_upload_file_success_contract(self) -> None:
        """POST /de2api/datasource/uploadFile should accept multipart file,id,editType and return parsed ExcelFileData in ResultMessage.data."""
        raise NotImplementedError
