"""Dashboard API — GET /api/v1/dashboard summary."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from crud import quota as quota_crud
from crud import usage as usage_crud
from crud import accounts as accounts_crud

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
async def get_dashboard(session: AsyncSession = Depends(get_session)):
    """
    Summary cards — all tools, all accounts.
    Returns: today's totals, current quota snapshots, account list,
    exhausted count, nearest reset.
    """
    accounts = await accounts_crud.get_all_accounts(session)
    snapshots = await quota_crud.get_latest_snapshots(session)
    today_totals = await usage_crud.get_today_totals(session)
    exhausted_count = sum(1 for s in snapshots if s.is_exhausted)

    from datetime import datetime
    now = datetime.utcnow()
    upcoming_resets = [
        s.reset_at for s in snapshots if s.reset_at and s.reset_at > now
    ]
    nearest_reset = min(upcoming_resets).isoformat() if upcoming_resets else None

    # Group snapshots by source
    by_source = {}
    for s in snapshots:
        src = s.source
        if src not in by_source:
            by_source[src] = []
        by_source[src].append(s.to_dict())

    return {
        "accounts": [a.to_dict() for a in accounts],
        "today": today_totals,
        "exhausted_count": exhausted_count,
        "nearest_reset": nearest_reset,
        "quota_by_source": by_source,
        "snapshot_count": len(snapshots),
    }
