from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class CoreLogOperate(Base):
    __tablename__ = "core_log_operate"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    uid: Mapped[int | None] = mapped_column(BigInteger)
    oid: Mapped[int | None] = mapped_column(BigInteger)
    op: Mapped[str | None] = mapped_column(String(255))
    op_text: Mapped[str | None] = mapped_column(String(255))
    op_detail: Mapped[str | None] = mapped_column(Text)
    name: Mapped[str | None] = mapped_column(String(255))
    ip: Mapped[str | None] = mapped_column(String(255))
    time: Mapped[int | None] = mapped_column(BigInteger)
    success: Mapped[bool | None] = mapped_column(Boolean)
    msg: Mapped[str | None] = mapped_column(Text)
    resource_id: Mapped[int | None] = mapped_column(BigInteger)
    resource_type: Mapped[str | None] = mapped_column(String(255))
    client: Mapped[str | None] = mapped_column(String(255))
