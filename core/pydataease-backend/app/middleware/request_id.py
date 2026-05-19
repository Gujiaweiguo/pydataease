from __future__ import annotations

import uuid
from typing import cast

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import request_id_ctx

HEADER_NAME = b"x-request-id"
HEADER_NAME_STR = "X-Request-ID"


class RequestIDMiddleware:
    """Assign every HTTP request a unique ID.

    * If the inbound request already carries an ``X-Request-ID`` header, the
      value is reused (useful for distributed tracing).
    * Otherwise a new UUID4 is generated.
    * The ID is stored in ``scope["state"]["request_id"]`` *and* in a
      ``ContextVar`` so that the structured-logging filter can pick it up.
    * The ID is echoed back as a response header.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Resolve or generate request ID
        request_id = self._get_existing_id(scope) or str(uuid.uuid4())

        # Store in scope state (accessible to downstream middleware / routes)
        scope.setdefault("state", {})
        scope["state"]["request_id"] = request_id

        # Store in ContextVar for structured logging
        token = request_id_ctx.set(request_id)

        # Inject X-Request-ID into the response headers
        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(cast(list[tuple[bytes, bytes]], message.get("headers", [])))
                headers.append((HEADER_NAME, request_id.encode()))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        finally:
            request_id_ctx.reset(token)

    @staticmethod
    def _get_existing_id(scope: Scope) -> str:
        """Return the first ``X-Request-ID`` header value, validated."""
        for key, value in scope.get("headers", []):
            if key.lower() == HEADER_NAME:
                raw = value.decode("latin-1")
                # BUG-065 fix: Validate format and length
                if len(raw) <= 64 and all(c.isalnum() or c in "-_" for c in raw):
                    return raw
        return ""
