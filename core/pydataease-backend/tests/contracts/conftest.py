from __future__ import annotations

import pytest


@pytest.fixture
def api_prefix() -> str:
    return "/de2api"


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-DE-TOKEN": "stub-jwt-token"}


@pytest.fixture
def share_headers() -> dict[str, str]:
    return {"X-DE-LINK-TOKEN": "stub-link-token"}


@pytest.fixture
async def async_client() -> object | None:
    """Placeholder AsyncClient fixture for future FastAPI app wiring."""
    return None
