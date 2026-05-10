class TestExportCenterContract:
    def test_export_tasks_success_contract(self) -> None:
        """POST /de2api/exportCenter/exportTasks/{status}/{goPage}/{pageSize} should return paged ExportTaskDTO records in ResultMessage.data."""
        raise NotImplementedError

    def test_export_tasks_auth_failure_contract(self) -> None:
        """POST /de2api/exportCenter/exportTasks/{status}/{goPage}/{pageSize} should fail when auth token is missing, invalid, or expired."""
        raise NotImplementedError

    def test_download_success_contract(self) -> None:
        """GET /de2api/exportCenter/download/{id} should return blob/file payload for existing export task when authorized."""
        raise NotImplementedError

    def test_retry_success_contract(self) -> None:
        """POST /de2api/exportCenter/retry/{id} should resubmit a failed export task and return success ResultMessage."""
        raise NotImplementedError
