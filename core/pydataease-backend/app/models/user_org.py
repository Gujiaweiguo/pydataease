from __future__ import annotations

from typing import final

from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


@final
class CoreUserOrg(Base):
    __tablename__ = "core_user_org"
    __table_args__ = (UniqueConstraint("user_id", "org_id", name="uq_core_user_org_user_org"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("core_user.id"), nullable=False)
    org_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("core_org.id"), nullable=False)
