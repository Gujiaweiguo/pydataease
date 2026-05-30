from __future__ import annotations

import time
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuthProvider(Base):
    __tablename__ = "core_auth_provider"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, default=lambda: time.time_ns())
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="Human-readable provider name")
    type: Mapped[str] = mapped_column(String(20), nullable=False, comment="Provider type: ldap, oidc, cas, mock")
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict, comment="Provider-specific configuration")
    claim_mapping: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict, comment="Declarative claim mapping rules")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="This provider is the default login method")
    oid: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="Org scope, null=global")
    create_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    update_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
