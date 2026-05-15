from __future__ import annotations

import asyncio
import json
import logging
import random

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response

from app.services.stomp_handler import StompSession, parse_frame

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)

# SockJS protocol requires a 2048-byte whitespace preamble for xhr_streaming
_SOCKJS_PREAMBLE = "\n" * 2048
_sockjs_sessions: dict[str, StompSession] = {}
_sockjs_queues: dict[str, list[str]] = {}


@router.get("/websocket/info")
async def websocket_info():
    return {
        "entropy": random.randint(0, 2**32 - 1),
        "origins": ["*:*"],
        "cookie_needed": False,
        "websocket": True,
    }


@router.websocket("/websocket/{server_id}/{session_id}/websocket")
async def sockjs_websocket(websocket: WebSocket, server_id: str, session_id: str) -> None:
    """SockJS WebSocket transport: /websocket/{server}/{session}/websocket"""
    await _handle_sockjs_websocket(websocket, session_id)


@router.post("/websocket/{server_id}/{session_id}/xhr_streaming")
async def sockjs_xhr_streaming(server_id: str, session_id: str):
    """SockJS XHR streaming transport. Returns preamble + open frame."""
    queue = _sockjs_queues.setdefault(session_id, [])
    frames = ["o"]
    frames.extend(_sockjs_encode_message(frame) for frame in queue)
    queue.clear()
    content = _SOCKJS_PREAMBLE + "\n".join(frames) + "\n"
    return Response(content=content, media_type="text/plain")


@router.post("/websocket/{server_id}/{session_id}/xhr")
async def sockjs_xhr(server_id: str, session_id: str):
    """SockJS XHR transport (non-streaming). Returns open frame."""
    return Response(content="o\n", media_type="text/plain")


@router.post("/websocket/{server_id}/{session_id}/xhr_send")
async def sockjs_xhr_send(server_id: str, session_id: str, request: Request):
    """SockJS XHR send endpoint. Accepts SockJS JSON array of STOMP frames."""
    raw_body = await request.body()
    payload = json.loads(raw_body.decode("utf-8") or "[]")
    if not isinstance(payload, list):
        return Response(status_code=204)
    session = _sockjs_sessions.setdefault(session_id, StompSession())
    queue = _sockjs_queues.setdefault(session_id, [])
    transport = _SockJSTransport(queue)
    for raw_frame in payload:
        if not raw_frame.endswith("\x00"):
            raw_frame = f"{raw_frame}\x00"
        frame = parse_frame(raw_frame)
        if frame is None:
            continue
        await session.handle_frame(frame, transport)
    return Response(status_code=204)


@router.get("/websocket/{server_id}/{session_id}/eventsource")
async def sockjs_eventsource(server_id: str, session_id: str):
    """SockJS EventSource transport."""
    return Response(content="\r\ndata: o\r\n\r\n", media_type="text/event-stream")


@router.get("/websocket/{server_id}/{session_id}/htmlfile")
async def sockjs_htmlfile(server_id: str, session_id: str):
    """SockJS htmlfile transport (IE fallback)."""
    html = (
        "<!DOCTYPE html><html><head><meta http-equiv='X-UA-Compatible' content='IE=edge' />"
        "</head><body><script>document.domain=document.domain;</script></body></html>"
    )
    return Response(content=html, media_type="text/html")


@router.websocket("/websocket")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Direct WebSocket endpoint (backward compatible)."""
    await _handle_stomp_websocket(websocket)


async def _handle_stomp_websocket(websocket: WebSocket) -> None:
    """Common STOMP-over-WebSocket handling for both direct and SockJS connections."""
    await websocket.accept()
    session = StompSession()
    buffer = ""
    try:
        while True:
            data = await websocket.receive_text()
            if "\x00" not in data and not buffer and not data.lstrip().startswith(
                ("CONNECT", "SUBSCRIBE", "UNSUBSCRIBE", "SEND", "DISCONNECT")
            ):
                await websocket.send_text(f"echo: {data}")
                continue

            buffer += data
            while "\x00" in buffer:
                raw_frame, buffer = buffer.split("\x00", 1)
                frame = parse_frame(raw_frame + "\x00")
                if frame is None:
                    continue
                await session.handle_frame(frame, websocket)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except asyncio.CancelledError:
        raise
    finally:
        await session.close()


async def _handle_sockjs_websocket(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    await websocket.send_text("o")
    session = _sockjs_sessions.setdefault(session_id, StompSession())
    try:
        while True:
            data = await websocket.receive_text()
            for raw_frame in _decode_sockjs_messages(data):
                transport = _SockJSWebSocketTransport(websocket)
                if not raw_frame.endswith("\x00"):
                    raw_frame = f"{raw_frame}\x00"
                frame = parse_frame(raw_frame)
                if frame is None:
                    continue
                await session.handle_frame(frame, transport)
    except WebSocketDisconnect:
        logger.info("SockJS WebSocket disconnected")
    except asyncio.CancelledError:
        raise
    finally:
        await session.close()


class _SockJSTransport:
    def __init__(self, queue: list[str]) -> None:
        self.queue = queue

    async def send_text(self, data: str) -> None:
        self.queue.append(data)

    async def close(self) -> None:
        return None


class _SockJSWebSocketTransport:
    def __init__(self, websocket: WebSocket) -> None:
        self.websocket = websocket

    async def send_text(self, data: str) -> None:
        await self.websocket.send_text(_sockjs_encode_message(data))

    async def close(self) -> None:
        await self.websocket.close()


def _sockjs_encode_message(frame: str) -> str:
    return f"a[{json.dumps(frame)}]"


def _decode_sockjs_messages(data: str) -> list[str]:
    if not data:
        return []
    if data == "o":
        return []
    if data.startswith("a"):
        try:
            payload = json.loads(data[1:])
        except json.JSONDecodeError:
            return []
        return [item for item in payload if isinstance(item, str)]
    if data.startswith("["):
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            return [data]
        return [item for item in payload if isinstance(item, str)]
    return [data]
