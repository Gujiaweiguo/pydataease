from __future__ import annotations

import asyncio
import contextlib
import logging
from dataclasses import dataclass, field
from itertools import count
from typing import Protocol


class StompWebSocket(Protocol):
    async def send_text(self, data: str) -> None: ...

    async def close(self) -> None: ...

logger = logging.getLogger(__name__)
_SESSION_COUNTER = count(1)
_MESSAGE_COUNTER = count(1)


@dataclass(slots=True)
class StompFrame:
    command: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""


def parse_frame(raw: str) -> StompFrame | None:
    frame_text = raw.rstrip("\x00")
    if not frame_text.strip():
        return None

    normalized = frame_text.replace("\r\n", "\n")
    lines = normalized.split("\n")
    command = lines[0].strip()
    if not command:
        return None

    headers: dict[str, str] = {}
    body_index = len(lines)
    for index, line in enumerate(lines[1:], start=1):
        if line == "":
            body_index = index + 1
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        headers[key.strip()] = value.strip()

    body = "\n".join(lines[body_index:]) if body_index <= len(lines) else ""
    return StompFrame(command=command.upper(), headers=headers, body=body)


def build_frame(command: str, headers: dict[str, str] | None = None, body: str = "") -> str:
    header_lines = [command]
    for key, value in (headers or {}).items():
        header_lines.append(f"{key}:{value}")
    return "\n".join([*header_lines, "", body]) + "\x00"


class StompSession:
    def __init__(self) -> None:
        self.session_id = f"stomp-session-{next(_SESSION_COUNTER)}"
        self.subscriptions: dict[str, str] = {}
        self.connected = False
        self.heartbeat_task: asyncio.Task[None] | None = None
        self.heartbeat_ms = 0

    async def handle_frame(self, frame: StompFrame, websocket: StompWebSocket) -> None:
        command = frame.command.upper()
        if command == "CONNECT":
            await self._handle_connect(frame, websocket)
            return
        if command == "SUBSCRIBE":
            await self._handle_subscribe(frame, websocket)
            return
        if command == "UNSUBSCRIBE":
            await self._handle_unsubscribe(frame, websocket)
            return
        if command == "SEND":
            await self._handle_send(frame, websocket)
            return
        if command == "DISCONNECT":
            await self._handle_disconnect(frame, websocket)
            return

        await websocket.send_text(
            build_frame(
                "ERROR",
                {"message": f"Unsupported command: {frame.command}"},
                f"Unsupported STOMP command: {frame.command}",
            )
        )

    async def close(self) -> None:
        if self.heartbeat_task is not None:
            self.heartbeat_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.heartbeat_task
            self.heartbeat_task = None

    async def _handle_connect(self, frame: StompFrame, websocket: StompWebSocket) -> None:
        self.connected = True
        self.heartbeat_ms = self._negotiate_heartbeat(frame.headers.get("heart-beat", "0,0"))
        await websocket.send_text(
            build_frame(
                "CONNECTED",
                {
                    "version": frame.headers.get("accept-version", "1.2").split(",")[0] or "1.2",
                    "session": self.session_id,
                    "heart-beat": f"{self.heartbeat_ms},{self.heartbeat_ms}",
                },
            )
        )
        if self.heartbeat_ms > 0:
            await self._start_heartbeat(websocket)

    async def _handle_subscribe(self, frame: StompFrame, websocket: StompWebSocket) -> None:
        subscription_id = frame.headers.get("id")
        destination = frame.headers.get("destination")
        if not subscription_id or not destination:
            await websocket.send_text(
                build_frame(
                    "ERROR",
                    {"message": "SUBSCRIBE requires id and destination headers"},
                    "Missing required SUBSCRIBE headers",
                )
            )
            return
        self.subscriptions[subscription_id] = destination
        await self._maybe_send_receipt(frame, websocket)

    async def _handle_unsubscribe(self, frame: StompFrame, websocket: StompWebSocket) -> None:
        subscription_id = frame.headers.get("id")
        if not subscription_id:
            await websocket.send_text(
                build_frame(
                    "ERROR",
                    {"message": "UNSUBSCRIBE requires id header"},
                    "Missing required UNSUBSCRIBE id header",
                )
            )
            return
        self.subscriptions.pop(subscription_id, None)
        await self._maybe_send_receipt(frame, websocket)

    async def _handle_send(self, frame: StompFrame, websocket: StompWebSocket) -> None:
        destination = frame.headers.get("destination")
        if not destination:
            await websocket.send_text(
                build_frame(
                    "ERROR",
                    {"message": "SEND requires destination header"},
                    "Missing required SEND destination header",
                )
            )
            return
        logger.info("STOMP SEND destination=%s body=%s", destination, frame.body)
        for subscription_id, subscribed_destination in self.subscriptions.items():
            if subscribed_destination != destination:
                continue
            await websocket.send_text(
                build_frame(
                    "MESSAGE",
                    {
                        "subscription": subscription_id,
                        "destination": destination,
                        "message-id": f"msg-{next(_MESSAGE_COUNTER)}",
                    },
                    frame.body,
                )
            )
        await self._maybe_send_receipt(frame, websocket)

    async def _handle_disconnect(self, frame: StompFrame, websocket: StompWebSocket) -> None:
        await self._maybe_send_receipt(frame, websocket)
        await self.close()
        await websocket.close()

    async def _maybe_send_receipt(self, frame: StompFrame, websocket: StompWebSocket) -> None:
        receipt = frame.headers.get("receipt")
        if receipt:
            await websocket.send_text(build_frame("RECEIPT", {"receipt-id": receipt}))

    def _negotiate_heartbeat(self, requested: str) -> int:
        try:
            cx, cy = requested.split(",", 1)
            client_outgoing = int(cx)
            client_incoming = int(cy)
        except (ValueError, AttributeError):
            return 0
        requested_interval = max(client_outgoing, client_incoming)
        return requested_interval if requested_interval > 0 else 0

    async def _start_heartbeat(self, websocket: StompWebSocket) -> None:
        await self.close()

        async def _heartbeat() -> None:
            assert self.heartbeat_ms > 0
            try:
                while True:
                    await asyncio.sleep(self.heartbeat_ms / 1000)
                    await websocket.send_text("\n")
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.debug("Stopping STOMP heartbeat for %s", self.session_id, exc_info=True)

        self.heartbeat_task = asyncio.create_task(_heartbeat())
