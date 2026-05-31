from __future__ import annotations

import time
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserAuthLink(Base):
    __tablename__ = "core_user_auth_link"
    __table_args__ = (
        UniqueConstraint("provider_id", "external_id", name="uq_provider_external"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, default=lambda: time.time_ns())
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    provider_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    external_username: Mapped[str | None] = mapped_column(String(255))
    external_email: Mapped[str | None] = mapped_column(String(255))
    create_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    update_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
