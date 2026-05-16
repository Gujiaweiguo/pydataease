from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class VisualizationWatermark(Base):
    __tablename__ = "visualization_watermark"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    version: Mapped[str | None] = mapped_column(String(255))
    setting_content: Mapped[str | None] = mapped_column(Text)
    create_by: Mapped[str | None] = mapped_column(String(255))
    create_time: Mapped[int | None] = mapped_column(BigInteger)
