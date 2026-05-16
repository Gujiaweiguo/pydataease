from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class VisualizationLinkJump(Base):
    __tablename__ = "visualization_link_jump"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    source_dv_id: Mapped[int | None] = mapped_column(BigInteger)
    source_view_id: Mapped[int | None] = mapped_column(BigInteger)
    link_jump_info: Mapped[str | None] = mapped_column(String(255))
    checked: Mapped[bool | None] = mapped_column(Boolean)
    copy_from: Mapped[int | None] = mapped_column(BigInteger)
    copy_id: Mapped[int | None] = mapped_column(BigInteger)


@final
class VisualizationLinkJumpInfo(Base):
    __tablename__ = "visualization_link_jump_info"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    link_jump_id: Mapped[int | None] = mapped_column(BigInteger)
    link_type: Mapped[str | None] = mapped_column(String(255))
    jump_type: Mapped[str | None] = mapped_column(String(255))
    window_size: Mapped[str | None] = mapped_column(String(255))
    target_dv_id: Mapped[int | None] = mapped_column(BigInteger)
    source_field_id: Mapped[int | None] = mapped_column(BigInteger)
    content: Mapped[str | None] = mapped_column(String(2048))
    checked: Mapped[bool | None] = mapped_column(Boolean)
    attach_params: Mapped[bool | None] = mapped_column(Boolean)
    copy_from: Mapped[int | None] = mapped_column(BigInteger)
    copy_id: Mapped[int | None] = mapped_column(BigInteger)


@final
class VisualizationLinkJumpTargetViewInfo(Base):
    __tablename__ = "visualization_link_jump_target_view_info"

    target_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    link_jump_info_id: Mapped[int | None] = mapped_column(BigInteger)
    source_field_active_id: Mapped[int | None] = mapped_column(BigInteger)
    target_view_id: Mapped[str | None] = mapped_column(String(255))
    target_field_id: Mapped[str | None] = mapped_column(String(255))
    copy_from: Mapped[int | None] = mapped_column(BigInteger)
    copy_id: Mapped[int | None] = mapped_column(BigInteger)
    target_type: Mapped[str | None] = mapped_column(String(255))
