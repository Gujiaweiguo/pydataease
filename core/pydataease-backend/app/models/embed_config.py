from __future__ import annotations

import time
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EmbedConfig(Base):
    """Per-resource-type embedding configuration."""

    __tablename__ = "core_embed_config"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, default=lambda: time.time_ns())
    resource_type: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, comment="dashboard, chart, datav, dataFiling")
    embed_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="Allow embedding for this resource type")
    allowed_domains: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list, comment="List of allowed domains, empty = all")
    password_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="Require password for embedded access")
    ticket_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="Require ticket for embedded access")
    max_expiry_hours: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="Max embed link expiry in hours, null = unlimited")
    extra_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict, comment="Future extension config")
    create_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    update_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
