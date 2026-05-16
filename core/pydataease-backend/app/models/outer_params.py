from __future__ import annotations

from typing import final

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class VisualizationOuterParams(Base):
    __tablename__ = "visualization_outer_params"

    params_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    visualization_id: Mapped[str | None] = mapped_column(String(50))
    checked: Mapped[bool | None] = mapped_column(Boolean)
    remark: Mapped[str | None] = mapped_column(String(255))
    copy_from: Mapped[str | None] = mapped_column(String(50))
    copy_id: Mapped[str | None] = mapped_column(String(50))


@final
class VisualizationOuterParamsInfo(Base):
    __tablename__ = "visualization_outer_params_info"

    params_info_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    params_id: Mapped[str | None] = mapped_column(String(50))
    param_name: Mapped[str | None] = mapped_column(String(255))
    checked: Mapped[bool | None] = mapped_column(Boolean)
    required: Mapped[bool | None] = mapped_column(Boolean)
    default_value: Mapped[str | None] = mapped_column(String(2048))
    enabled_default: Mapped[bool | None] = mapped_column(Boolean)
    copy_from: Mapped[str | None] = mapped_column(String(50))
    copy_id: Mapped[str | None] = mapped_column(String(50))


@final
class VisualizationOuterParamsTargetViewInfo(Base):
    __tablename__ = "visualization_outer_params_target_view_info"

    target_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    params_info_id: Mapped[str | None] = mapped_column(String(50))
    target_view_id: Mapped[str | None] = mapped_column(String(50))
    target_ds_id: Mapped[str | None] = mapped_column(String(50))
    target_field_id: Mapped[str | None] = mapped_column(String(50))
    copy_from: Mapped[str | None] = mapped_column(String(50))
    copy_id: Mapped[str | None] = mapped_column(String(50))
    match_mode: Mapped[str | None] = mapped_column(String(50))


@final
class SnapshotVisualizationOuterParams(Base):
    __tablename__ = "snapshot_visualization_outer_params"

    params_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    visualization_id: Mapped[str | None] = mapped_column(String(50))
    checked: Mapped[bool | None] = mapped_column(Boolean)
    remark: Mapped[str | None] = mapped_column(String(255))
    copy_from: Mapped[str | None] = mapped_column(String(50))
    copy_id: Mapped[str | None] = mapped_column(String(50))


@final
class SnapshotVisualizationOuterParamsInfo(Base):
    __tablename__ = "snapshot_visualization_outer_params_info"

    params_info_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    params_id: Mapped[str | None] = mapped_column(String(50))
    param_name: Mapped[str | None] = mapped_column(String(255))
    checked: Mapped[bool | None] = mapped_column(Boolean)
    required: Mapped[bool | None] = mapped_column(Boolean)
    default_value: Mapped[str | None] = mapped_column(String(2048))
    enabled_default: Mapped[bool | None] = mapped_column(Boolean)
    copy_from: Mapped[str | None] = mapped_column(String(50))
    copy_id: Mapped[str | None] = mapped_column(String(50))


@final
class SnapshotVisualizationOuterParamsTargetViewInfo(Base):
    __tablename__ = "snapshot_visualization_outer_params_target_view_info"

    target_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    params_info_id: Mapped[str | None] = mapped_column(String(50))
    target_view_id: Mapped[str | None] = mapped_column(String(50))
    target_ds_id: Mapped[str | None] = mapped_column(String(50))
    target_field_id: Mapped[str | None] = mapped_column(String(50))
    copy_from: Mapped[str | None] = mapped_column(String(50))
    copy_id: Mapped[str | None] = mapped_column(String(50))
    match_mode: Mapped[str | None] = mapped_column(String(50))
