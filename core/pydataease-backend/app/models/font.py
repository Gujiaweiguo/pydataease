from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class CoreFont(Base):
    __tablename__ = "core_font"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_trans_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_default: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    update_time: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    is_builtin: Mapped[bool | None] = mapped_column("is_BuiltIn", Boolean, nullable=True)
    size: Mapped[float | None] = mapped_column(Float, nullable=True)
    size_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
