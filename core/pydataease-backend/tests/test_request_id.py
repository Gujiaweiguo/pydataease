from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_response_includes_x_request_id_header(client: AsyncClient) -> None:
    """Every response should include an X-Request-ID header with a valid UUID."""
    response = await client.get("/de2api/dekey")
    assert response.status_code == 200

    request_id = response.headers.get("x-request-id")
    assert request_id is not None
    # Validate UUID format
    uuid.UUID(request_id)


@pytest.mark.asyncio
async def test_different_requests_get_different_ids(client: AsyncClient) -> None:
    """Two sequential requests should receive different request IDs."""
    r1 = await client.get("/de2api/dekey")
    r2 = await client.get("/de2api/dekey")

    id1 = r1.headers["x-request-id"]
    id2 = r2.headers["x-request-id"]
    assert id1 != id2


@pytest.mark.asyncio
async def test_incoming_request_id_is_echoed(client: AsyncClient) -> None:
    """If the client sends X-Request-ID, the same value is echoed back."""
    custom_id = "my-custom-trace-id-1234"
    response = await client.get(
        "/de2api/dekey",
        headers={"X-Request-ID": custom_id},
    )
    assert response.status_code == 200
    assert response.headers["x-request-id"] == custom_id


@pytest.mark.asyncio
async def test_non_http_requests_skip_request_id() -> None:
    """Non-HTTP scopes (e.g. lifespan) should not receive request IDs."""
    from app.middleware.request_id import RequestIDMiddleware
    from starlette.types import Scope, Receive, Send

    captured_scope: Scope | None = None

    async def inner_app(scope: Scope, receive: Receive, send: Send) -> None:
        nonlocal captured_scope
        captured_scope = scope
        # Send a minimal response
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    middleware = RequestIDMiddleware(inner_app)

    async def noop_send(msg):
        pass

    await middleware(
        {"type": "lifespan", "asgi": {"version": "3.0"}},
        noop_send,
        noop_send,
    )

    # State should NOT have request_id for non-HTTP scopes
    assert captured_scope is not None
    state = captured_scope.get("state", {})
    assert "request_id" not in state
