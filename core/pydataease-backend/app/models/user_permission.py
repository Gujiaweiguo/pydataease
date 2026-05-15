from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


@final
class CoreUserPermission(Base):
    __tablename__ = "core_user_permission"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    permission_point_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    create_time: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
