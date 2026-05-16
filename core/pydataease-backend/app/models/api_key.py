from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class XpackApiKey(Base):
    __tablename__ = "xpack_api_key"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    access_key: Mapped[str] = mapped_column(String(255), nullable=False)
    access_secret: Mapped[str] = mapped_column(String(255), nullable=False)
    enable: Mapped[bool] = mapped_column(Boolean, default=True)
    create_time: Mapped[int | None] = mapped_column(BigInteger)
    creator: Mapped[int | None] = mapped_column(BigInteger)
