from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


@final
class CorePermissionWhitelist(Base):
    __tablename__ = "core_permission_whitelist"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    dataset_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="0 means all datasets")
    scope: Mapped[str] = mapped_column(String(20), nullable=False, comment="row/column/both")
    create_time: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
