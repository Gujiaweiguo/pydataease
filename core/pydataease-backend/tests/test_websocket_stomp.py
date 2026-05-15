from __future__ import annotations

import pytest

from app.routers.websocket import websocket_endpoint
from app.services.stomp_handler import StompFrame, StompSession, build_frame, parse_frame


class FakeWebSocket:
    def __init__(self) -> None:
        self.accepted = False
        self.sent_json: list[dict[str, object]] = []
        self.sent_text: list[str] = []
        self.closed = False
        self._incoming: list[str] = []

    async def accept(self) -> None:
        self.accepted = True

    async def send_json(self, payload: dict[str, object]) -> None:
        self.sent_json.append(payload)

    async def send_text(self, data: str) -> None:
        self.sent_text.append(data)

    async def close(self) -> None:
        self.closed = True

    async def receive_text(self) -> str:
        if not self._incoming:
            raise RuntimeError("No incoming data configured")
        item = self._incoming.pop(0)
        if item == "__disconnect__":
            from fastapi import WebSocketDisconnect

            raise WebSocketDisconnect()
        return item


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            "SEND\ndestination:/topic/updates\nreceipt:r-1\n\nhello\x00",
            StompFrame(
                command="SEND",
                headers={"destination": "/topic/updates", "receipt": "r-1"},
                body="hello",
            ),
        ),
        ("\x00", None),
        ("\nheader:value\n\nbody\x00", None),
    ],
)
def test_parse_frame(raw: str, expected: StompFrame | None) -> None:
    assert parse_frame(raw) == expected


def test_build_frame() -> None:
    assert (
        build_frame("MESSAGE", {"destination": "/topic/updates", "subscription": "sub-1"}, "hello")
        == "MESSAGE\ndestination:/topic/updates\nsubscription:sub-1\n\nhello\x00"
    )


@pytest.mark.asyncio
async def test_session_connect_handling() -> None:
    websocket = FakeWebSocket()
    session = StompSession()

    await session.handle_frame(
        StompFrame(command="CONNECT", headers={"accept-version": "1.2,1.1", "heart-beat": "100,100"}),
        websocket,
    )

    assert session.connected is True
    assert websocket.sent_text[0].startswith("CONNECTED\n")
    assert "version:1.2" in websocket.sent_text[0]
    assert "heart-beat:100,100" in websocket.sent_text[0]
    await session.close()


@pytest.mark.asyncio
async def test_session_subscribe_and_unsubscribe_with_receipts() -> None:
    websocket = FakeWebSocket()
    session = StompSession()

    await session.handle_frame(
        StompFrame(
            command="SUBSCRIBE",
            headers={"id": "sub-1", "destination": "/topic/updates", "receipt": "receipt-1"},
        ),
        websocket,
    )
    assert session.subscriptions == {"sub-1": "/topic/updates"}
    assert websocket.sent_text[-1] == "RECEIPT\nreceipt-id:receipt-1\n\n\x00"

    await session.handle_frame(
        StompFrame(command="UNSUBSCRIBE", headers={"id": "sub-1", "receipt": "receipt-2"}),
        websocket,
    )
    assert session.subscriptions == {}
    assert websocket.sent_text[-1] == "RECEIPT\nreceipt-id:receipt-2\n\n\x00"


@pytest.mark.asyncio
async def test_session_send_echoes_to_matching_subscription() -> None:
    websocket = FakeWebSocket()
    session = StompSession()
    session.subscriptions["sub-1"] = "/topic/updates"

    await session.handle_frame(
        StompFrame(
            command="SEND",
            headers={"destination": "/topic/updates", "receipt": "receipt-3"},
            body="payload",
        ),
        websocket,
    )

    assert websocket.sent_text[0].startswith("MESSAGE\n")
    assert "subscription:sub-1" in websocket.sent_text[0]
    assert websocket.sent_text[1] == "RECEIPT\nreceipt-id:receipt-3\n\n\x00"


@pytest.mark.asyncio
async def test_session_disconnect_closes_socket() -> None:
    websocket = FakeWebSocket()
    session = StompSession()

    await session.handle_frame(
        StompFrame(command="DISCONNECT", headers={"receipt": "receipt-4"}),
        websocket,
    )

    assert websocket.sent_text == ["RECEIPT\nreceipt-id:receipt-4\n\n\x00"]
    assert websocket.closed is True


@pytest.mark.asyncio
async def test_websocket_endpoint_handles_partial_stomp_frames() -> None:
    websocket = FakeWebSocket()
    websocket._incoming = [
        "CONNECT\naccept-version:1.2\nheart-beat:0,0\n\n",
        "\x00",
        "SUBSCRIBE\nid:sub-1\ndestination:/topic/updates\nreceipt:r-1\n\n\x00",
        "SEND\ndestination:/topic/updates\n\npa",
        "yload\x00",
        "__disconnect__",
    ]

    await websocket_endpoint(websocket)  # type: ignore[arg-type]

    assert websocket.accepted is True
    assert websocket.sent_text[0].startswith("CONNECTED\n")
    assert websocket.sent_text[1] == "RECEIPT\nreceipt-id:r-1\n\n\x00"
    assert websocket.sent_text[2].startswith("MESSAGE\n")


@pytest.mark.asyncio
async def test_websocket_endpoint_preserves_plain_text_echo() -> None:
    websocket = FakeWebSocket()
    websocket._incoming = ["hello", "__disconnect__"]

    await websocket_endpoint(websocket)  # type: ignore[arg-type]

    assert websocket.sent_text == ["echo: hello"]
