from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


@final
class CoreStore(Base):
    __tablename__ = "core_store"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    resource_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    uid: Mapped[int] = mapped_column(BigInteger, nullable=False)
    resource_type: Mapped[int] = mapped_column(Integer, nullable=False)
    time: Mapped[int] = mapped_column(BigInteger, nullable=False)
