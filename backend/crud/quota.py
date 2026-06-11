"""CRUD operations for quota snapshots."""

from datetime import datetime
from sqlalchemy import select, func, and_, distinct
from sqlalchemy.ext.asyncio import AsyncSession

from models.quota_snapshot import QuotaSnapshot


async def get_latest_snapshots(
    session: AsyncSession,
    source: str | None = None,
    account_id: str | None = None,
) -> list[QuotaSnapshot]:
    """Get the most recent snapshot per account + model combination."""
    # Subquery for latest snapshot_at per account_id + model_id
    subq = (
        select(
            QuotaSnapshot.account_id,
            QuotaSnapshot.model_id,
            func.max(QuotaSnapshot.snapshot_at).label("max_at"),
        )
        .group_by(QuotaSnapshot.account_id, QuotaSnapshot.model_id)
    )

    if source:
        subq = subq.where(QuotaSnapshot.source == source)
    if account_id:
        subq = subq.where(QuotaSnapshot.account_id == account_id)

    subq = subq.subquery()

    stmt = (
        select(QuotaSnapshot)
        .join(
            subq,
            and_(
                QuotaSnapshot.account_id == subq.c.account_id,
                QuotaSnapshot.model_id == subq.c.model_id,
                QuotaSnapshot.snapshot_at == subq.c.max_at,
            ),
        )
        .order_by(QuotaSnapshot.source, QuotaSnapshot.account_id, QuotaSnapshot.model_id)
    )

    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_snapshots_for_source(
    session: AsyncSession, source: str, account_id: str
) -> list[QuotaSnapshot]:
    """Get latest snapshots for one source + account."""
    return await get_latest_snapshots(session, source=source, account_id=account_id)


async def add_quota_snapshots(
    session: AsyncSession, snapshots: list[QuotaSnapshot]
) -> int:
    """Bulk insert quota snapshots."""
    for snapshot in snapshots:
        session.add(snapshot)
    await session.flush()
    return len(snapshots)


async def get_snapshot_history(
    session: AsyncSession,
    account_id: str,
    model_id: str,
    hours: int = 48,
) -> list[QuotaSnapshot]:
    """Get snapshot history for a specific model over the last N hours."""
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    stmt = (
        select(QuotaSnapshot)
        .where(
            QuotaSnapshot.account_id == account_id,
            QuotaSnapshot.model_id == model_id,
            QuotaSnapshot.snapshot_at >= cutoff,
        )
        .order_by(QuotaSnapshot.snapshot_at.asc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_exhausted_count(session: AsyncSession) -> int:
    """Count currently exhausted quotas."""
    snapshots = await get_latest_snapshots(session)
    return sum(1 for s in snapshots if s.is_exhausted)


async def get_nearest_reset(session: AsyncSession) -> datetime | None:
    """Find the nearest upcoming reset time."""
    snapshots = await get_latest_snapshots(session)
    now = datetime.utcnow()
    upcoming = [
        s.reset_at for s in snapshots
        if s.reset_at and s.reset_at > now
    ]
    return min(upcoming) if upcoming else None
