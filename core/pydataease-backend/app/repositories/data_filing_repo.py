from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data_filing import FilingAudit, FilingConfig, FilingSubmission


class FilingConfigRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, filing_id: int) -> FilingConfig | None:
        stmt = select(FilingConfig).where(FilingConfig.id == filing_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self) -> list[FilingConfig]:
        stmt = select(FilingConfig).order_by(FilingConfig.create_time.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(self, status: str) -> list[FilingConfig]:
        stmt = select(FilingConfig).where(FilingConfig.status == status).order_by(FilingConfig.create_time.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **kwargs) -> FilingConfig:
        config = FilingConfig(**kwargs)
        self.session.add(config)
        await self.session.commit()
        await self.session.refresh(config)
        return config

    async def update(self, filing_id: int, **kwargs) -> FilingConfig | None:
        config = await self.get_by_id(filing_id)
        if config is None:
            return None
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        await self.session.commit()
        await self.session.refresh(config)
        return config

    async def delete(self, filing_id: int) -> bool:
        config = await self.get_by_id(filing_id)
        if config is None:
            return False
        await self.session.delete(config)
        await self.session.commit()
        return True


class FilingSubmissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, submission_id: int) -> FilingSubmission | None:
        stmt = select(FilingSubmission).where(FilingSubmission.id == submission_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_filing(self, filing_id: int) -> list[FilingSubmission]:
        stmt = select(FilingSubmission).where(FilingSubmission.filing_id == filing_id).order_by(FilingSubmission.create_time.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_hash(self, filing_id: int, payload_hash: str, window_seconds: int = 300) -> FilingSubmission | None:
        """Find a submission with the same hash within the idempotency window."""
        from datetime import datetime, timedelta

        cutoff = datetime.utcnow() - timedelta(seconds=window_seconds)
        stmt = (
            select(FilingSubmission)
            .where(
                FilingSubmission.filing_id == filing_id,
                FilingSubmission.payload_hash == payload_hash,
                FilingSubmission.create_time >= cutoff,
            )
            .order_by(FilingSubmission.create_time.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, **kwargs) -> FilingSubmission:
        submission = FilingSubmission(**kwargs)
        self.session.add(submission)
        await self.session.commit()
        await self.session.refresh(submission)
        return submission

    async def update_status(self, submission_id: int, status: str, **kwargs) -> FilingSubmission | None:
        submission = await self.get_by_id(submission_id)
        if submission is None:
            return None
        submission.status = status
        for key, value in kwargs.items():
            if hasattr(submission, key):
                setattr(submission, key, value)
        await self.session.commit()
        await self.session.refresh(submission)
        return submission


class FilingAuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **kwargs) -> FilingAudit:
        audit = FilingAudit(**kwargs)
        self.session.add(audit)
        await self.session.commit()
        await self.session.refresh(audit)
        return audit

    async def get_by_filing(self, filing_id: int) -> list[FilingAudit]:
        stmt = select(FilingAudit).where(FilingAudit.filing_id == filing_id).order_by(FilingAudit.create_time.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_submission(self, submission_id: int) -> list[FilingAudit]:
        stmt = select(FilingAudit).where(FilingAudit.submission_id == submission_id).order_by(FilingAudit.create_time.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
