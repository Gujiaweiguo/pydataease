from __future__ import annotations

from fastapi.routing import APIWebSocketRoute
from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_still_works() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_websocket_route_exists() -> None:
    routes = [route for route in app.routes if isinstance(route, APIWebSocketRoute)]

    assert any(route.path == "/websocket" for route in routes)


def test_websocket_accepts_connection() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/websocket") as websocket:
            websocket.send_text("ping")
            response = websocket.receive_text()

    assert response == "echo: ping"


def test_websocket_echo() -> None:
    with TestClient(app) as client:
        with client.websocket_connect("/websocket") as websocket:
            websocket.send_text("hello")
            response = websocket.receive_text()

    assert response == "echo: hello"
