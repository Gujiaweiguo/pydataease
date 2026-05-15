from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


@final
class CoreOrg(Base):
    __tablename__ = "core_org"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    pid: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    create_time: Mapped[int | None] = mapped_column(BigInteger)
    update_time: Mapped[int | None] = mapped_column(BigInteger)
