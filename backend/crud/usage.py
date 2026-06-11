"""CRUD operations for usage records."""

from datetime import datetime
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.usage_record import UsageRecord


async def get_usage_records(
    session: AsyncSession,
    source: str | None = None,
    account_id: str | None = None,
    model_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 500,
    offset: int = 0,
) -> list[UsageRecord]:
    stmt = select(UsageRecord)
    filters = []

    if source:
        filters.append(UsageRecord.source == source)
    if account_id:
        filters.append(UsageRecord.account_id == account_id)
    if model_id:
        filters.append(UsageRecord.model_id == model_id)
    if start_date:
        filters.append(UsageRecord.timestamp >= datetime.fromisoformat(start_date))
    if end_date:
        filters.append(UsageRecord.timestamp <= datetime.fromisoformat(end_date))

    if filters:
        stmt = stmt.where(and_(*filters))

    stmt = stmt.order_by(UsageRecord.timestamp.desc()).limit(limit).offset(offset)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_usage_summary(
    session: AsyncSession,
    source: str | None = None,
    account_id: str | None = None,
    days: int = 30,
) -> list[dict]:
    """Aggregate usage per model per day."""
    cutoff = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    from datetime import timedelta
    cutoff = cutoff - timedelta(days=days)

    stmt = (
        select(
            func.date_trunc("day", UsageRecord.timestamp).label("day"),
            UsageRecord.source,
            UsageRecord.model_id,
            UsageRecord.model_label,
            UsageRecord.account_id,
            func.sum(UsageRecord.input_tokens).label("total_input"),
            func.sum(UsageRecord.output_tokens).label("total_output"),
            func.sum(UsageRecord.cache_tokens).label("total_cache"),
            func.sum(UsageRecord.request_count).label("total_requests"),
            func.sum(UsageRecord.cost_usd).label("total_cost"),
        )
        .where(UsageRecord.timestamp >= cutoff)
    )

    if source:
        stmt = stmt.where(UsageRecord.source == source)
    if account_id:
        stmt = stmt.where(UsageRecord.account_id == account_id)

    stmt = stmt.group_by(
        func.date_trunc("day", UsageRecord.timestamp),
        UsageRecord.source,
        UsageRecord.model_id,
        UsageRecord.model_label,
        UsageRecord.account_id,
    ).order_by(func.date_trunc("day", UsageRecord.timestamp).desc())

    result = await session.execute(stmt)
    rows = result.all()

    return [
        {
            "day": row.day.isoformat() if row.day else None,
            "source": row.source,
            "model_id": row.model_id,
            "model_label": row.model_label,
            "account_id": row.account_id,
            "total_input": int(row.total_input or 0),
            "total_output": int(row.total_output or 0),
            "total_cache": int(row.total_cache or 0),
            "total_requests": int(row.total_requests or 0),
            "total_cost": float(row.total_cost) if row.total_cost else 0.0,
        }
        for row in rows
    ]


async def get_today_totals(session: AsyncSession) -> dict:
    """Get aggregate token totals for today."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    stmt = select(
        func.sum(UsageRecord.input_tokens).label("input"),
        func.sum(UsageRecord.output_tokens).label("output"),
        func.sum(UsageRecord.cache_tokens).label("cache"),
        func.sum(UsageRecord.request_count).label("requests"),
        func.sum(UsageRecord.cost_usd).label("cost"),
    ).where(UsageRecord.timestamp >= today)

    result = await session.execute(stmt)
    row = result.one()

    return {
        "total_input_tokens": int(row.input or 0),
        "total_output_tokens": int(row.output or 0),
        "total_cache_tokens": int(row.cache or 0),
        "total_requests": int(row.requests or 0),
        "total_cost_usd": float(row.cost) if row.cost else 0.0,
    }


async def add_usage_records(session: AsyncSession, records: list[UsageRecord]) -> int:
    """Bulk insert usage records, skipping duplicates by external_id."""
    added = 0
    for record in records:
        if record.external_id:
            existing = await session.execute(
                select(UsageRecord.id).where(
                    UsageRecord.external_id == record.external_id
                )
            )
            if existing.scalar_one_or_none():
                continue
        session.add(record)
        added += 1
    await session.flush()
    return added
