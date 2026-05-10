from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

type JSONValue = dict[str, object] | list[object]


@final
class XpackShare(Base):
    __tablename__ = "xpack_share"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    creator: Mapped[int] = mapped_column(BigInteger, nullable=False)
    time: Mapped[int] = mapped_column(BigInteger, nullable=False)
    exp: Mapped[int | None] = mapped_column(BigInteger)
    uuid: Mapped[str] = mapped_column(String(16), nullable=False)
    pwd: Mapped[str | None] = mapped_column(String(255))
    resource_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    oid: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    auto_pwd: Mapped[bool | None] = mapped_column(Boolean)
    ticket_require: Mapped[bool | None] = mapped_column(Boolean)


@final
class CoreShareTicket(Base):
    __tablename__ = "core_share_ticket"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    uuid: Mapped[str] = mapped_column(String(255), nullable=False)
    ticket: Mapped[str] = mapped_column(String(255), nullable=False)
    exp: Mapped[int | None] = mapped_column(BigInteger)
    args: Mapped[JSONValue | None] = mapped_column(JSONB)
    access_time: Mapped[int | None] = mapped_column(BigInteger)
