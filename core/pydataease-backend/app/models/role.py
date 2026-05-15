from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


@final
class CoreRole(Base):
    __tablename__ = "core_role"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    oid: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    create_time: Mapped[int | None] = mapped_column(BigInteger)
    update_time: Mapped[int | None] = mapped_column(BigInteger)
