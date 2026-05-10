class TestChartViewContract:
    def test_get_chart_success_contract(self) -> None:
        """POST /de2api/chart/getChart/{id} should return ChartViewDTO for the requested chart id."""
        raise NotImplementedError

    def test_get_chart_auth_failure_contract(self) -> None:
        """POST /de2api/chart/getChart/{id} should fail when auth token is missing, invalid, or expired."""
        raise NotImplementedError

    def test_save_chart_success_contract(self) -> None:
        """POST /de2api/chart/save should persist ChartViewDTO and return saved chart payload in ResultMessage.data."""
        raise NotImplementedError

    def test_save_chart_auth_failure_contract(self) -> None:
        """POST /de2api/chart/save should fail when auth token is missing, invalid, or expired."""
        raise NotImplementedError


class TestChartDataContract:
    def test_get_data_success_contract(self) -> None:
        """POST /de2api/chartData/getData should accept ChartViewDTO and return chart query result in ResultMessage.data."""
        raise NotImplementedError

    def test_get_data_auth_failure_contract(self) -> None:
        """POST /de2api/chartData/getData should fail when auth token is missing, invalid, or expired."""
        raise NotImplementedError

    def test_export_details_success_contract(self) -> None:
        """POST /de2api/chartData/innerExportDetails should return blob/file response for ChartExcelRequest when authorized."""
        raise NotImplementedError
