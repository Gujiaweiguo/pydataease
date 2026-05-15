from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

type JSONValue = dict[str, object] | list[object]


@final
class CoreDeEngine(Base):
    __tablename__ = "core_de_engine"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(String(50))
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    configuration: Mapped[JSONValue] = mapped_column(JSONB, nullable=False)
    create_time: Mapped[int | None] = mapped_column(BigInteger)
    update_time: Mapped[int | None] = mapped_column(BigInteger)
    create_by: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str | None] = mapped_column(String(45))
    enable_data_fill: Mapped[bool | None] = mapped_column(Boolean)
