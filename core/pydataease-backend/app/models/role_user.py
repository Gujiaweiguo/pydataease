from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


@final
class CoreRoleUser(Base):
    __tablename__ = "core_role_user"
    __table_args__ = (UniqueConstraint("role_id", "user_id", "oid", name="uq_core_role_user_binding"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    role_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("core_role.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("core_user.id"), nullable=False)
    oid: Mapped[int] = mapped_column(BigInteger, nullable=False)
