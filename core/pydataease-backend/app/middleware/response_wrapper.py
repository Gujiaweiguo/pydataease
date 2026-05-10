from __future__ import annotations

import json
from typing import Any, cast

from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.middleware.whitelist import API_PREFIXES
from app.schemas.response import ResultMessage


class ResultMessageMiddleware:
    app: ASGIApp

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = cast(str, scope.get("path", ""))
        if not self._should_wrap(path):
            await self.app(scope, receive, send)
            return

        status_code = 200
        headers: list[tuple[bytes, bytes]] = []
        body = bytearray()
        skip_wrap = False

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code, headers, skip_wrap
            if message["type"] == "http.response.start":
                status_code = cast(int, message["status"])
                headers = list(cast(list[tuple[bytes, bytes]], message.get("headers", [])))
                content_type = self._header_value(headers, b"content-type")
                transfer_encoding = self._header_value(headers, b"transfer-encoding")
                skip_wrap = (
                    path == "/health"
                    or "text/event-stream" in content_type
                    or transfer_encoding.lower() == "chunked"
                )
                if skip_wrap:
                    await send(message)
                return

            if message["type"] != "http.response.body":
                await send(message)
                return

            if skip_wrap:
                await send(message)
                return

            body.extend(cast(bytes, message.get("body", b"")))
            if message.get("more_body", False):
                return

            wrapped = self._wrap_body(bytes(body), status_code, headers)
            await wrapped(scope, receive, send)

        await self.app(scope, receive, send_wrapper)

    @staticmethod
    def _should_wrap(path: str) -> bool:
        return path != "/health" and any(path.startswith(prefix) for prefix in API_PREFIXES)

    def _wrap_body(self, body: bytes, status_code: int, headers: list[tuple[bytes, bytes]]) -> Response:
        content_type = self._header_value(headers, b"content-type")
        header_map = self._to_header_map(headers)
        if content_type and "application/octet-stream" in content_type:
            return Response(content=body, status_code=status_code, headers=header_map, media_type=content_type)

        payload = self._decode_body(body)
        if isinstance(payload, dict) and {"code", "data", "msg"}.issubset(payload):
            return JSONResponse(status_code=status_code, content=payload, headers=header_map)

        if status_code >= 400:
            detail = payload.get("detail") if isinstance(payload, dict) else payload
            if isinstance(detail, list):
                detail = "; ".join(str(item) for item in detail)
            result = ResultMessage(code=status_code, data=None, msg=str(detail or "Request failed"))
        else:
            result = ResultMessage(code=0, data=payload, msg="success")

        return JSONResponse(status_code=status_code, content=result.model_dump(), headers=header_map)

    @staticmethod
    def _decode_body(body: bytes) -> Any:
        if not body:
            return None
        text = body.decode("utf-8")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text

    @staticmethod
    def _header_value(headers: list[tuple[bytes, bytes]], key: bytes) -> str:
        key_lower = key.lower()
        for header_key, header_value in headers:
            if header_key.lower() == key_lower:
                return header_value.decode("latin-1")
        return ""

    @staticmethod
    def _to_header_map(headers: list[tuple[bytes, bytes]]) -> dict[str, str]:
        excluded = {b"content-length", b"content-type"}
        return {
            key.decode("latin-1"): value.decode("latin-1")
            for key, value in headers
            if key.lower() not in excluded
        }
