from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class CoreUser(Base):
    __tablename__ = "core_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    account: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(255))
    phone_prefix: Mapped[str | None] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    enable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    oid: Mapped[int | None] = mapped_column(BigInteger)
    origin: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mfa_enable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    language: Mapped[str | None] = mapped_column(String(255))
    create_time: Mapped[int | None] = mapped_column(BigInteger)
    update_time: Mapped[int | None] = mapped_column(BigInteger)
