from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class VisualizationSubject(Base):
    __tablename__ = "visualization_subject"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255))
    type: Mapped[str | None] = mapped_column(String(255))
    details: Mapped[dict | None] = mapped_column(JSONB)
    delete_flag: Mapped[bool | None] = mapped_column(Boolean, default=False)
    cover_url: Mapped[str | None] = mapped_column(Text)
    create_num: Mapped[int] = mapped_column(Integer, default=0)
    create_time: Mapped[int | None] = mapped_column(BigInteger)
    create_by: Mapped[str | None] = mapped_column(String(255))
    update_time: Mapped[int | None] = mapped_column(BigInteger)
    update_by: Mapped[str | None] = mapped_column(String(255))
    delete_time: Mapped[int | None] = mapped_column(BigInteger)
    delete_by: Mapped[str | None] = mapped_column(String(255))
