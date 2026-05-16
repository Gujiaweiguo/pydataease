from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class VisualizationBackground(Base):
    __tablename__ = "visualization_background"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255))
    classification: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    remark: Mapped[str | None] = mapped_column(String(255))
    sort: Mapped[int | None] = mapped_column(Integer)
    upload_time: Mapped[int | None] = mapped_column(BigInteger)
    base_url: Mapped[str | None] = mapped_column(String(255))
    url: Mapped[str | None] = mapped_column(String(255))
