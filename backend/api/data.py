"""Data Management API — database stats, JSON export, and purging history."""

import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import UsageRecord, QuotaSnapshot, Account, AlertRule, GeminiQuotaConfig

router = APIRouter(tags=["Data Management"])


@router.get("/data/stats")
async def get_db_stats(session: AsyncSession = Depends(get_session)):
    """Get count of rows in each table."""
    try:
        usage_count = await session.scalar(select(func.count()).select_from(UsageRecord))
        snapshot_count = await session.scalar(select(func.count()).select_from(QuotaSnapshot))
        account_count = await session.scalar(select(func.count()).select_from(Account))
        alert_count = await session.scalar(select(func.count()).select_from(AlertRule))
        gemini_count = await session.scalar(select(func.count()).select_from(GeminiQuotaConfig))

        return {
            "usage_records": usage_count or 0,
            "quota_snapshots": snapshot_count or 0,
            "accounts": account_count or 0,
            "alert_rules": alert_count or 0,
            "gemini_configs": gemini_count or 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch db stats: {str(e)}")


@router.get("/data/export")
async def export_data(session: AsyncSession = Depends(get_session)):
    """Export all tables as a single JSON object."""
    try:
        accounts = (await session.execute(select(Account))).scalars().all()
        usages = (await session.execute(select(UsageRecord))).scalars().all()
        snapshots = (await session.execute(select(QuotaSnapshot))).scalars().all()
        alerts = (await session.execute(select(AlertRule))).scalars().all()
        gemini_configs = (await session.execute(select(GeminiQuotaConfig))).scalars().all()

        data = {
            "accounts": [a.to_dict() for a in accounts],
            "usage_records": [u.to_dict() for u in usages],
            "quota_snapshots": [q.to_dict() for q in snapshots],
            "alert_rules": [al.to_dict() for al in alerts],
            "gemini_configs": [g.to_dict() for g in gemini_configs],
        }
        
        # Format datetimes in JSON serialization friendly format
        return JSONResponse(
            content=data,
            headers={"Content-Disposition": "attachment; filename=quotalens_export.json"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")


@router.post("/data/purge")
async def purge_history(
    days: int = Query(30, description="Purge history older than N days"),
    session: AsyncSession = Depends(get_session)
):
    """Purge usage records and quota snapshots older than N days."""
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Purge UsageRecords
        q_usage = delete(UsageRecord).where(UsageRecord.timestamp < cutoff)
        res_usage = await session.execute(q_usage)
        
        # Purge QuotaSnapshots
        q_snapshot = delete(QuotaSnapshot).where(QuotaSnapshot.snapshot_at < cutoff)
        res_snapshot = await session.execute(q_snapshot)
        
        await session.commit()
        
        return {
            "message": f"Successfully purged records older than {days} days",
            "purged_usage_records": res_usage.rowcount,
            "purged_quota_snapshots": res_snapshot.rowcount,
        }
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to purge history: {str(e)}")
