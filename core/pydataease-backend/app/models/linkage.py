from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class VisualizationLinkage(Base):
    __tablename__ = "visualization_linkage"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    dv_id: Mapped[int | None] = mapped_column(BigInteger)
    source_view_id: Mapped[int | None] = mapped_column(BigInteger)
    target_view_id: Mapped[int | None] = mapped_column(BigInteger)
    update_time: Mapped[int | None] = mapped_column(BigInteger)
    update_people: Mapped[str | None] = mapped_column(String(255))
    linkage_active: Mapped[bool | None] = mapped_column(Boolean)
    ext1: Mapped[str | None] = mapped_column(String(255))
    ext2: Mapped[str | None] = mapped_column(String(255))
    copy_from: Mapped[int | None] = mapped_column(BigInteger)
    copy_id: Mapped[int | None] = mapped_column(BigInteger)


@final
class VisualizationLinkageField(Base):
    __tablename__ = "visualization_linkage_field"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    linkage_id: Mapped[int | None] = mapped_column(BigInteger)
    source_field: Mapped[int | None] = mapped_column(BigInteger)
    target_field: Mapped[int | None] = mapped_column(BigInteger)
    update_time: Mapped[int | None] = mapped_column(BigInteger)
    copy_from: Mapped[int | None] = mapped_column(BigInteger)
    copy_id: Mapped[int | None] = mapped_column(BigInteger)


@final
class SnapshotVisualizationLinkage(Base):
    __tablename__ = "snapshot_visualization_linkage"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    dv_id: Mapped[int | None] = mapped_column(BigInteger)
    source_view_id: Mapped[int | None] = mapped_column(BigInteger)
    target_view_id: Mapped[int | None] = mapped_column(BigInteger)
    update_time: Mapped[int | None] = mapped_column(BigInteger)
    update_people: Mapped[str | None] = mapped_column(String(255))
    linkage_active: Mapped[bool | None] = mapped_column(Boolean)
    ext1: Mapped[str | None] = mapped_column(String(255))
    ext2: Mapped[str | None] = mapped_column(String(255))
    copy_from: Mapped[int | None] = mapped_column(BigInteger)
    copy_id: Mapped[int | None] = mapped_column(BigInteger)


@final
class SnapshotVisualizationLinkageField(Base):
    __tablename__ = "snapshot_visualization_linkage_field"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    linkage_id: Mapped[int | None] = mapped_column(BigInteger)
    source_field: Mapped[int | None] = mapped_column(BigInteger)
    target_field: Mapped[int | None] = mapped_column(BigInteger)
    update_time: Mapped[int | None] = mapped_column(BigInteger)
    copy_from: Mapped[int | None] = mapped_column(BigInteger)
    copy_id: Mapped[int | None] = mapped_column(BigInteger)
