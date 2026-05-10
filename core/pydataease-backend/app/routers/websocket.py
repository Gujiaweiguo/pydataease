from __future__ import annotations

import asyncio
import logging
import random

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.websocket import WSMessage
from app.services.stomp_handler import StompSession, parse_frame

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)


@router.get("/websocket/info")
async def websocket_info():
    return {
        "entropy": random.randint(0, 2**32 - 1),
        "origins": ["*:*"],
        "cookie_needed": False,
        "websocket": True,
    }


@router.get("/websocket/{path:path}")
async def websocket_transport_catchall(path: str):
    """SockJS transport fallback stub (xhr_streaming, eventsource, etc.)"""
    return {"body": ""}


@router.websocket("/websocket")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    welcome = WSMessage(type="welcome", content="WebSocket compatibility stub connected")
    await websocket.send_json(welcome.model_dump())
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
