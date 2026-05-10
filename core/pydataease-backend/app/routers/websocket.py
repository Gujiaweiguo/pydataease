from __future__ import annotations

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.websocket import WSMessage

router = APIRouter(tags=["websocket"])
logger = logging.getLogger(__name__)


@router.websocket("/websocket")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    logger.warning("WebSocket connected - STOMP compatibility not yet implemented")
    welcome = WSMessage(type="welcome", content="WebSocket compatibility stub connected")
    await websocket.send_json(welcome.model_dump())
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"echo: {data}")
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
