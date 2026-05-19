from __future__ import annotations

from io import BytesIO
from typing import cast

import pytest
from openpyxl import Workbook

from app.models.datasource import CoreDatasource
from app.schemas.datasource import DatasourceFieldResponse
from app.services.dataset_service import DatasetService
from app.services.datasource_service import DatasourceService


def _build_workbook_bytes() -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet.title = "orders"
    sheet.append(["id", "amount", "name"])
    sheet.append([1, 10.5, "alice"])
    sheet.append([2, 20.0, "bob"])
    output = BytesIO()
    workbook.save(output)
    return output.getvalue()


class _Upload:
    def __init__(self, filename: str, content: bytes) -> None:
        self.filename = filename
        self._content = content

    async def read(self) -> bytes:
        return self._content


@pytest.mark.asyncio
async def test_excel_upload_parses_sheet_metadata() -> None:
    service = DatasourceService(session=None, repository=None)  # type: ignore[arg-type]

    payload = cast(dict[str, object], await service.upload_file(_Upload("orders.xlsx", _build_workbook_bytes())))
    sheets = cast(list[dict[str, object]], payload["sheets"])

    assert payload["excelLabel"] == "orders.xlsx"
    assert len(sheets) == 1
    sheet = sheets[0]
    fields = cast(list[dict[str, object]], sheet["fields"])
    rows = cast(list[dict[str, object]], sheet["jsonArray"])
    assert sheet["tableName"] == "orders"
    assert fields[0]["originName"] == "id"
    assert rows[0]["name"] == "alice"


def test_excel_preview_and_table_helpers() -> None:
    service = DatasourceService(session=None, repository=None)  # type: ignore[arg-type]
    configuration: object = [
        {
            "sheetId": "1",
            "tableName": "orders",
            "fields": [
                {"originName": "id", "name": "id", "fieldType": "LONG", "deExtractType": 2},
                {"originName": "amount", "name": "amount", "fieldType": "DOUBLE", "deExtractType": 3},
            ],
            "jsonArray": [{"id": 1, "amount": 10.5}],
        }
    ]

    sheets = service._excel_sheets(configuration)
    assert sheets[0]["tableName"] == "orders"
    first_field = cast(list[dict[str, object]], sheets[0]["fields"])[0]
    preview_field = service._excel_preview_field(first_field)
    assert preview_field == {"name": "id", "originName": "id", "deType": 2, "fieldType": "LONG"}


def test_excel_datasource_fields_map_to_dataset_fields() -> None:
    field = DatasourceFieldResponse(name="created_at", origin_name="created_at", data_type="DATETIME", de_type=1, type="DATETIME", nullable=True)

    mapped = DatasetService._datasource_field_to_dataset_field(field, datasource_id=42)

    assert mapped.datasource_id == 42
    assert mapped.origin_name == "created_at"
    assert mapped.name == "created_at"
    assert mapped.type == "DATETIME"
    assert mapped.de_type == 1
    assert mapped.checked is True


@pytest.mark.asyncio
async def test_load_remote_csv_file(monkeypatch: pytest.MonkeyPatch) -> None:
    service = DatasourceService(session=None, repository=None)  # type: ignore[arg-type]

    def fake_download(url: str, username: str, password: str) -> tuple[bytes, str]:
        assert url == "https://example.com/orders.csv"
        assert username == "alice"
        assert password == "secret"
        return b"id,name\n1,alice\n", "orders.csv"

    monkeypatch.setattr(DatasourceService, "_download_remote_file", staticmethod(fake_download))

    payload = await service.load_remote_file(
        {
            "url": "https://example.com/orders.csv",
            "userName": "YWxpY2U=",
            "passwd": "c2VjcmV0",
        }
    )

    sheets = cast(list[dict[str, object]], payload["sheets"])
    assert payload["excelLabel"] == "orders.csv"
    assert sheets[0]["tableName"] == "orders"
    rows = cast(list[dict[str, object]], sheets[0]["jsonArray"])
    assert rows[0]["name"] == "alice"


def test_persistable_excel_remote_configuration_wraps_sheet_list() -> None:
    service = DatasourceService(session=None, repository=None)  # type: ignore[arg-type]

    config = service._persistable_configuration(
        "ExcelRemote",
        [{"tableName": "orders", "fields": [], "jsonArray": []}],
        {"syncRate": "SIMPLE_CRON", "simpleCronValue": "1"},
    )

    assert isinstance(config, dict)
    assert config["sheets"] == [{"tableName": "orders", "fields": [], "jsonArray": []}]
    assert config["syncSetting"] == {"syncRate": "SIMPLE_CRON", "simpleCronValue": "1"}


def test_decorate_api_datasource_response_splits_api_and_params() -> None:
    service = DatasourceService(session=None, repository=None)  # type: ignore[arg-type]

    entity = CoreDatasource(
        id=1,
        name="api-ds",
        type="API",
        configuration=[
            {"name": "orders", "type": "table", "deTableName": "api_orders"},
            {"name": "runtime", "type": "params", "serialNumber": 2},
        ],
        description=None,
        pid=None,
        edit_type=None,
        create_time=1,
        update_time=2,
        update_by=7,
        create_by="7",
        status="Success",
        qrtz_instance=None,
        task_status="WaitingForExecution",
        enable_data_fill=False,
    )

    data = cast(dict[str, object], service._decorate_datasource_response(entity))

    assert data["configuration"] == {}
    assert data["apiConfigurationStr"] == [{"name": "orders", "type": "table", "deTableName": "api_orders"}]
    assert data["paramsStr"] == [{"name": "runtime", "type": "params", "serialNumber": 2}]
    sync_setting = cast(dict[str, object], data["syncSetting"])
    assert sync_setting["syncRate"] == "SIMPLE_CRON"
