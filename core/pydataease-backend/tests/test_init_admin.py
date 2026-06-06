"""Tests for the init_admin CLI module."""
from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.commands.init_admin import _init_admin, main
from app.utils.password_utils import verify_password


@pytest.mark.asyncio
async def test_create_admin_when_none_exists():
    """Admin user is created when no existing admin is found."""
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result
    mock_session.commit = AsyncMock()
    mock_session.add = MagicMock()

    mock_session_ctx = AsyncMock()
    mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

    mock_factory = MagicMock(return_value=mock_session_ctx)
    mock_engine = AsyncMock()
    mock_engine.dispose = AsyncMock()

    with (
        patch("app.commands.init_admin.create_async_engine", return_value=mock_engine),
        patch("app.commands.init_admin.async_sessionmaker", return_value=mock_factory),
        patch("app.commands.init_admin.get_settings") as mock_settings,
    ):
        mock_settings.return_value = MagicMock(database_url="postgresql+asyncpg://test:test@localhost/test")
        await _init_admin("TestPassword123!")

    mock_session.add.assert_called_once()
    added_user = mock_session.add.call_args[0][0]
    assert added_user.account == "admin"
    assert added_user.name == "Administrator"
    assert added_user.oid == 1
    assert added_user.enable is True
    assert added_user.origin == 0
    assert added_user.mfa_enable is False
    assert added_user.language == "zh-CN"
    assert verify_password("TestPassword123!", added_user.password)
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_skip_when_admin_already_exists():
    """No new user is created when admin already exists in the database."""
    existing_admin = MagicMock()
    existing_admin.account = "admin"

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = existing_admin
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result

    mock_session_ctx = AsyncMock()
    mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

    mock_factory = MagicMock(return_value=mock_session_ctx)
    mock_engine = AsyncMock()
    mock_engine.dispose = AsyncMock()

    with (
        patch("app.commands.init_admin.create_async_engine", return_value=mock_engine),
        patch("app.commands.init_admin.async_sessionmaker", return_value=mock_factory),
        patch("app.commands.init_admin.get_settings") as mock_settings,
    ):
        mock_settings.return_value = MagicMock(database_url="postgresql+asyncpg://test:test@localhost/test")
        await _init_admin("SomePassword123!")

    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()


def test_error_when_admin_password_empty():
    """SystemExit is raised when DE_ADMIN_PASSWORD is not set or empty."""
    with (
        patch.dict(os.environ, {}, clear=False),
        patch("app.commands.init_admin.os.environ", {}),
    ):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1


def test_error_when_admin_password_whitespace_only():
    """SystemExit is raised when DE_ADMIN_PASSWORD is whitespace only."""
    with (
        patch.dict(os.environ, {"DE_ADMIN_PASSWORD": "   "}),
    ):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1
