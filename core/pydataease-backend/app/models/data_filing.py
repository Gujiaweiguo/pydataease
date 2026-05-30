from __future__ import annotations

import time
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FilingConfig(Base):
    """Data filing form configuration."""

    __tablename__ = "core_filing_config"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, default=lambda: time.time_ns())
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="Filing form name")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", comment="draft, published, disabled")
    target_datasource_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="Target datasource for writes")
    target_table: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="Target table name")
    form_schema: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict, comment="Form field definitions and validation rules")
    field_mapping: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict, comment="Mapping from form fields to target table columns")
    idempotency_window_seconds: Mapped[int] = mapped_column(BigInteger, nullable=False, default=300, comment="Idempotency window in seconds")
    oid: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="Org scope")
    creator_uid: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="Creator user ID")
    create_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    update_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class FilingSubmission(Base):
    """Data filing submission record."""

    __tablename__ = "core_filing_submission"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, default=lambda: time.time_ns())
    filing_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True, comment="Reference to FilingConfig")
    payload_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="SHA-256 hash of payload for idempotency")
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True, comment="Submitted data")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", comment="pending, success, failed, retrying")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Error details if failed")
    submitter_uid: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="Submitting user ID")
    retry_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    create_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    update_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class FilingAudit(Base):
    """Audit trail for all filing operations."""

    __tablename__ = "core_filing_audit"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, default=lambda: time.time_ns())
    filing_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True, comment="Reference to FilingConfig")
    submission_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="Reference to FilingSubmission")
    action: Mapped[str] = mapped_column(String(30), nullable=False, comment="submit, publish, disable, retry, config_update")
    actor_uid: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="User who performed the action")
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True, comment="Action details")
    outcome: Mapped[str] = mapped_column(String(20), nullable=False, default="success", comment="success, failure")
    error_code: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="Error code if failed")
    create_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
