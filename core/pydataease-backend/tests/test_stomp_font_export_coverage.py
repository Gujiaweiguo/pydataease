# pyright: reportAttributeAccessIssue=false

from __future__ import annotations

import io
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi import HTTPException, UploadFile  # pyright: ignore[reportMissingImports]
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.font import CoreFont  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.auth import TokenUser  # pyright: ignore[reportImplicitRelativeImport]
from app.schemas.export import ExportTaskCreateRequest  # pyright: ignore[reportImplicitRelativeImport]
from app.services.export_service import ExportService  # pyright: ignore[reportImplicitRelativeImport]
from app.services.font_service import FontService, _fallback_font, _human_size  # pyright: ignore[reportImplicitRelativeImport]
from app.services.stomp_handler import StompFrame, StompSession, build_frame, parse_frame  # pyright: ignore[reportImplicitRelativeImport]


class FakeWebSocket:
    def __init__(self) -> None:
        self.sent: list[str] = []
        self.closed = False

    async def send_text(self, data: str) -> None:
        self.sent.append(data)

    async def close(self) -> None:
        self.closed = True


class FakeScalarResult:
    def __init__(self, values: list[Any]) -> None:
        self._values = values

    def all(self) -> list[Any]:
        return list(self._values)

    def first(self) -> Any:
        return self._values[0] if self._values else None

    def scalar_one_or_none(self) -> Any:
        return self.first()


class FakeExecuteResult:
    def __init__(self, values: list[Any]) -> None:
        self._values = values

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult(self._values)

    def scalar_one_or_none(self) -> Any:
        return self._values[0] if self._values else None


class FakeFontSession:
    def __init__(self, execute_results: list[Any] | None = None) -> None:
        self.execute_results = execute_results or []
        self.added: list[Any] = []
        self.deleted: list[Any] = []
        self.commit_count = 0
        self.executed: list[Any] = []

    async def execute(self, statement: Any) -> Any:
        self.executed.append(statement)
        if not self.execute_results:
            raise AssertionError("No fake execute result remaining")
        result = self.execute_results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    def add(self, entity: Any) -> None:
        self.added.append(entity)

    async def commit(self) -> None:
        self.commit_count += 1

    async def delete(self, entity: Any) -> None:
        self.deleted.append(entity)


class FakeExportRepo:
    def __init__(self) -> None:
        self.tasks: dict[str, Any] = {}
        self.deleted_by_ids: list[tuple[int, list[str]]] = []
        self.deleted_all_status: list[tuple[int, str]] = []
        self.deleted_all_from: list[tuple[int, int]] = []

    async def list_by_user_and_from(self, user_id: int, export_from: int) -> list[Any]:
        return [task for task in self.tasks.values() if task.user_id == user_id and task.export_from == export_from]

    async def count_by_user_grouped_by_status(self, user_id: int) -> dict[str, int]:
        return {"ALL": len([task for task in self.tasks.values() if task.user_id == user_id]), "SUCCESS": 1}

    async def list_paginated_by_user_and_status(
        self, user_id: int, status: str, offset: int, limit: int
    ) -> tuple[int, list[Any]]:
        tasks = [
            task for task in self.tasks.values() if task.user_id == user_id and (status == "ALL" or task.export_status == status)
        ]
        return len(tasks), tasks[offset : offset + limit]

    async def create(self, payload: dict[str, object]) -> Any:
        task = SimpleNamespace(file_size=None, file_size_unit=None, export_machine_name=None, msg=None, **payload)
        self.tasks[task.id] = task
        return task

    async def get_by_id(self, task_id: str) -> Any:
        return self.tasks.get(task_id)

    async def delete_by_id(self, task_id: str) -> None:
        self.tasks.pop(task_id, None)

    async def delete_by_ids(self, user_id: int, ids: list[str]) -> None:
        self.deleted_by_ids.append((user_id, ids))

    async def delete_all_by_user_and_from(self, user_id: int, export_from: int) -> None:
        self.deleted_all_from.append((user_id, export_from))

    async def delete_all_by_user_and_status(self, user_id: int, status: str) -> None:
        self.deleted_all_status.append((user_id, status))


class FakeAsyncSession:
    def __init__(self) -> None:
        self.commit_count = 0

    async def commit(self) -> None:
        self.commit_count += 1


def _export_service(repo: FakeExportRepo | None = None, session: FakeAsyncSession | None = None) -> ExportService:
    service = ExportService.__new__(ExportService)
    service.session = cast(AsyncSession, cast(object, session or FakeAsyncSession()))
    service.task_repo = repo or FakeExportRepo()
    return service


def _export_task(task_id: str, **overrides: Any) -> Any:
    payload = {
        "id": task_id,
        "user_id": 7,
        "file_name": "report.xlsx",
        "file_size": 1.5,
        "file_size_unit": "MB",
        "export_from": 2,
        "export_status": "SUCCESS",
        "export_from_type": "panel",
        "export_time": 123456,
        "export_progress": "100",
        "export_machine_name": None,
        "params": {"k": "v"},
        "msg": None,
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


class TestStompCoverage:
    @pytest.mark.asyncio
    async def test_parse_frame_returns_none_for_blank_payload(self) -> None:
        assert parse_frame("\n\x00") is None

    @pytest.mark.asyncio
    async def test_parse_frame_parses_headers_and_body(self) -> None:
        frame = parse_frame("send\r\ndestination:/topic/demo\r\nreceipt:r1\r\n\r\nhello\r\nworld\x00")

        assert frame is not None
        assert frame.command == "SEND"
        assert frame.headers == {"destination": "/topic/demo", "receipt": "r1"}
        assert frame.body == "hello\nworld"

    @pytest.mark.asyncio
    async def test_build_frame_appends_headers_body_and_terminator(self) -> None:
        assert build_frame("RECEIPT", {"receipt-id": "abc"}, "done") == "RECEIPT\nreceipt-id:abc\n\ndone\x00"

    @pytest.mark.asyncio
    async def test_handle_connect_sets_state_and_replies_connected(self) -> None:
        session = StompSession()
        websocket = FakeWebSocket()

        await session.handle_frame(
            StompFrame("CONNECT", {"accept-version": "1.1,1.2", "heart-beat": "0,0"}),
            websocket,
        )

        assert session.connected is True
        assert session.heartbeat_ms == 0
        assert len(websocket.sent) == 1
        connected = parse_frame(websocket.sent[0])
        assert connected is not None
        assert connected.command == "CONNECTED"

    @pytest.mark.asyncio
    async def test_handle_subscribe_send_and_unsubscribe_flow(self) -> None:
        session = StompSession()
        websocket = FakeWebSocket()

        await session.handle_frame(
            StompFrame("SUBSCRIBE", {"id": "sub-1", "destination": "/topic/a", "receipt": "r1"}),
            websocket,
        )
        await session.handle_frame(
            StompFrame("SEND", {"destination": "/topic/a", "receipt": "r2"}, "payload"),
            websocket,
        )
        await session.handle_frame(StompFrame("UNSUBSCRIBE", {"id": "sub-1", "receipt": "r3"}), websocket)

        frames = [parse_frame(message) for message in websocket.sent]
        assert session.subscriptions == {}
        assert [frame.command for frame in frames if frame is not None] == ["RECEIPT", "MESSAGE", "RECEIPT", "RECEIPT"]
        assert frames[1] is not None and frames[1].headers["subscription"] == "sub-1"
        assert frames[1] is not None and frames[1].body == "payload"

    @pytest.mark.asyncio
    async def test_subscribe_without_required_headers_sends_error(self) -> None:
        session = StompSession()
        websocket = FakeWebSocket()

        await session.handle_frame(StompFrame("SUBSCRIBE", {"id": "only-id"}), websocket)

        error = parse_frame(websocket.sent[0])
        assert error is not None
        assert error.command == "ERROR"
        assert error.body == "Missing required SUBSCRIBE headers"

    @pytest.mark.asyncio
    async def test_unsupported_command_sends_error(self) -> None:
        session = StompSession()
        websocket = FakeWebSocket()

        await session.handle_frame(StompFrame("ACK", {}), websocket)

        frame = parse_frame(websocket.sent[0])
        assert frame is not None
        assert frame.command == "ERROR"
        assert frame.headers["message"] == "Unsupported command: ACK"

    @pytest.mark.asyncio
    async def test_disconnect_closes_socket_and_cancels_heartbeat(self) -> None:
        session = StompSession()
        websocket = FakeWebSocket()
        session.heartbeat_ms = 1
        await session._start_heartbeat(websocket)

        await session.handle_frame(StompFrame("DISCONNECT", {"receipt": "bye"}), websocket)

        assert websocket.closed is True
        assert session.heartbeat_task is None
        receipt = parse_frame(websocket.sent[0])
        assert receipt is not None
        assert receipt.command == "RECEIPT"

    @pytest.mark.asyncio
    async def test_negotiate_heartbeat_handles_invalid_and_uses_maximum(self) -> None:
        session = StompSession()

        assert session._negotiate_heartbeat("bad") == 0
        assert session._negotiate_heartbeat("10,25") == 25


class TestFontServiceCoverage:
    @pytest.mark.asyncio
    async def test_list_fonts_returns_fallback_when_query_fails(self) -> None:
        service = FontService(cast(AsyncSession, cast(object, FakeFontSession([SQLAlchemyError()]))) )

        assert await service.list_fonts() == _fallback_font()

    @pytest.mark.asyncio
    async def test_list_fonts_serializes_rows_and_default_fonts_prefers_marked_default(self) -> None:
        rows = [
            CoreFont(id=1, name="PingFang", file_name=None, file_trans_name=None, is_default=True, update_time=1, is_builtin=True, size=None, size_type=None),
            CoreFont(id=2, name="Roboto", file_name="r.ttf", file_trans_name="r1.ttf", is_default=False, update_time=2, is_builtin=False, size=12.3, size_type="KB"),
        ]
        session = FakeFontSession([FakeExecuteResult(rows), FakeExecuteResult(rows)])
        service = FontService(cast(AsyncSession, cast(object, session)))

        fonts = await service.list_fonts()
        defaults = await service.default_fonts()

        assert fonts[0]["id"] == "1"
        assert fonts[1]["fileTransName"] == "r1.ttf"
        assert defaults == [fonts[0]]

    @pytest.mark.asyncio
    async def test_create_font_skips_duplicate_name(self) -> None:
        session = FakeFontSession([FakeExecuteResult([SimpleNamespace(id=1)])])
        service = FontService(cast(AsyncSession, cast(object, session)))

        await service.create_font({"name": "PingFang"})

        assert session.added == []
        assert session.commit_count == 0

    @pytest.mark.asyncio
    async def test_create_font_persists_new_font(self) -> None:
        session = FakeFontSession([FakeExecuteResult([])])
        service = FontService(cast(AsyncSession, cast(object, session)))

        await service.create_font({"name": "Inter", "fileName": "inter.ttf", "isDefault": True, "size": 1.2, "sizeType": "KB"})

        assert len(session.added) == 1
        assert session.added[0].name == "Inter"
        assert session.commit_count == 1

    @pytest.mark.asyncio
    async def test_edit_font_without_id_delegates_to_create(self, monkeypatch: pytest.MonkeyPatch) -> None:
        service = FontService(cast(AsyncSession, cast(object, FakeFontSession())))
        captured: list[dict[str, Any]] = []

        async def fake_create_font(data: dict[str, Any]) -> None:
            captured.append(data)

        monkeypatch.setattr(service, "create_font", fake_create_font)
        await service.edit_font({"name": "Fallback"})

        assert captured == [{"name": "Fallback"}]

    @pytest.mark.asyncio
    async def test_edit_font_updates_fields_and_clears_existing_defaults(self) -> None:
        font = CoreFont(id=2, name="Old", file_name="old.ttf", file_trans_name="old-1.ttf", is_default=False, update_time=1, is_builtin=False, size=1.0, size_type="KB")
        session = FakeFontSession([FakeExecuteResult([]), FakeExecuteResult([font])])
        service = FontService(cast(AsyncSession, cast(object, session)))

        await service.edit_font({"id": "2", "name": "New", "isDefault": True, "size": 3.5, "sizeType": "MB"})

        assert font.name == "New"
        assert font.is_default is True
        assert font.size == 3.5
        assert font.size_type == "MB"
        assert session.commit_count == 1

    @pytest.mark.asyncio
    async def test_delete_font_removes_db_row_and_file(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        stored = tmp_path / "font.ttf"
        stored.write_bytes(b"font-data")
        font = CoreFont(id=3, name="Delete", file_name="font.ttf", file_trans_name="font.ttf", is_default=False, update_time=1, is_builtin=False, size=1.0, size_type="KB")
        session = FakeFontSession([FakeExecuteResult([font])])
        service = FontService(cast(AsyncSession, cast(object, session)))
        monkeypatch.setattr("app.services.font_service.FONT_PATH", str(tmp_path))

        await service.delete_font(3)

        assert session.deleted == [font]
        assert session.commit_count == 1
        assert not stored.exists()

    @pytest.mark.asyncio
    async def test_upload_file_rejects_non_ttf_and_writes_ttf(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        service = FontService(cast(AsyncSession, cast(object, FakeFontSession())))
        monkeypatch.setattr("app.services.font_service.FONT_PATH", str(tmp_path))
        monkeypatch.setattr("app.services.font_service.uuid.uuid4", lambda: SimpleNamespace(hex="abc123"))

        rejected = await service.upload_file(UploadFile(filename="bad.otf", file=io.BytesIO(b"x")))
        uploaded = await service.upload_file(UploadFile(filename="good.ttf", file=io.BytesIO(b"a" * 2048)))

        assert rejected == {}
        assert uploaded == {"fileTransName": "abc123.ttf", "size": 2.0, "sizeType": "KB", "name": "good"}
        assert (tmp_path / "abc123.ttf").read_bytes() == b"a" * 2048

    @pytest.mark.asyncio
    async def test_human_size_uses_kb_mb_and_gb_thresholds(self) -> None:
        assert _human_size(1024) == (1.0, "KB")
        assert _human_size(2 * 1024 * 1024) == (2.0, "MB")
        assert _human_size(3 * 1024 * 1024 * 1024) == (3.0, "GB")


class TestExportServiceCoverage:
    @pytest.mark.asyncio
    async def test_list_methods_and_pagination_normalize_output(self) -> None:
        repo = FakeExportRepo()
        repo.tasks = {
            "t1": _export_task("t1", export_status="SUCCESS"),
            "t2": _export_task("t2", export_status="FAILED"),
        }
        service = _export_service(repo=repo)
        user = TokenUser(user_id=7, oid=9)

        tasks = await service.list_tasks(2, user)
        counts = await service.list_task_records(user)
        paged = await service.list_tasks_paginated("SUCCESS", 0, 0, user)
        records = cast(list[dict[str, Any]], paged["records"])
        assert len(tasks) == 2
        assert counts["ALL"] == 2
        assert paged["total"] == 1
        assert records[0]["export_status"] == "SUCCESS"

    @pytest.mark.asyncio
    async def test_create_delete_and_bulk_delete_paths(self) -> None:
        repo = FakeExportRepo()
        service = _export_service(repo=repo)
        user = TokenUser(user_id=7, oid=9)

        created = await service.create_task(
            ExportTaskCreateRequest(file_name="report.xlsx", export_from=2, export_from_type="panel", params={"x": 1}),
            user,
        )
        await service.delete_task(created.id)
        await service.delete_tasks(["a", "b"], user)
        await service.delete_all(9, user)
        await service.delete_all_by_status("FAILED", ["c"], user)
        await service.delete_all_by_status("FAILED", [], user)
        assert created.file_name == "report.xlsx"
        assert created.export_status == "INITIATED"
        assert repo.deleted_by_ids == [(7, ["a", "b"]), (7, ["c"])]
        assert repo.deleted_all_from == [(7, 9)]
        assert repo.deleted_all_status == [(7, "FAILED")]

    @pytest.mark.asyncio
    async def test_delete_task_and_generate_uri_raise_for_missing_task(self) -> None:
        service = _export_service(repo=FakeExportRepo())

        with pytest.raises(HTTPException) as delete_exc:
            await service.delete_task("missing")
        with pytest.raises(HTTPException) as uri_exc:
            await service.generate_download_uri("missing")
        assert delete_exc.value.status_code == 404
        assert uri_exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_generate_download_uri_and_export_limit(self) -> None:
        repo = FakeExportRepo()
        repo.tasks["task-1"] = _export_task("task-1")
        service = _export_service(repo=repo)

        assert await service.generate_download_uri("task-1") == {"uri": "/de2api/exportCenter/download/task-1"}
        assert await service.export_limit() is True

    @pytest.mark.asyncio
    async def test_retry_task_rejects_missing_or_non_failed_task_and_resets_failed_task(self) -> None:
        repo = FakeExportRepo()
        repo.tasks["done"] = _export_task("done", export_status="SUCCESS")
        repo.tasks["failed"] = _export_task("failed", export_status="FAILED", export_progress="88", msg="boom")
        session = FakeAsyncSession()
        service = _export_service(repo=repo, session=session)

        with pytest.raises(HTTPException) as missing_exc:
            await service.retry_task("missing")
        with pytest.raises(HTTPException) as invalid_exc:
            await service.retry_task("done")
        retried = await service.retry_task("failed")
        assert missing_exc.value.status_code == 404
        assert invalid_exc.value.status_code == 400
        assert retried["export_status"] == "INITIATED"
        assert retried["export_progress"] == "0"
        assert retried["msg"] is None
        assert session.commit_count == 1

    @pytest.mark.asyncio
    async def test_download_handles_missing_and_non_ready_cases(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        repo = FakeExportRepo()
        repo.tasks["pending"] = _export_task("pending", export_status="RUNNING", msg=None)
        repo.tasks["nometa"] = _export_task("nometa", file_name=None)
        repo.tasks["nofile"] = _export_task("nofile", file_name="missing.xlsx")
        service = _export_service(repo=repo)
        monkeypatch.setenv("DE_EXPORT_DIR", str(tmp_path))

        assert (await service.download("pending"))["msg"] == "Export file is not ready"
        assert (await service.download("nometa"))["msg"] == "Export file metadata is missing"
        assert (await service.download("nofile"))["msg"] == "Export file not found"

    @pytest.mark.asyncio
    async def test_download_returns_file_metadata_when_export_exists(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        repo = FakeExportRepo()
        (tmp_path / "report.xlsx").write_bytes(b"ok")
        repo.tasks["task-1"] = _export_task("task-1", file_name="nested/report.xlsx", file_size=2.5, msg="ready")
        service = _export_service(repo=repo)
        monkeypatch.setenv("DE_EXPORT_DIR", str(tmp_path))

        payload = await service.download("task-1")
        assert payload == {
            "id": "task-1",
            "status": "SUCCESS",
            "path": str(tmp_path / "report.xlsx"),
            "file_name": "report.xlsx",
            "file_size": 2.5,
            "msg": "ready",
        }
