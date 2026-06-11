"""Quota API — current quota snapshot endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from crud import quota as quota_crud
from models import GeminiQuotaConfig

router = APIRouter(tags=["Quota"])


class GeminiLimitUpdate(BaseModel):
    rpm: int
    tpm: int
    rpd: int


@router.get("/quota")
async def get_all_quota(session: AsyncSession = Depends(get_session)):
    """All current quota snapshots across all sources and accounts."""
    snapshots = await quota_crud.get_latest_snapshots(session)
    return {"snapshots": [s.to_dict() for s in snapshots]}


@router.get("/quota/{source}/{account_id}")
async def get_quota_for_source(
    source: str, account_id: str, session: AsyncSession = Depends(get_session)
):
    """Quota for one source + account."""
    snapshots = await quota_crud.get_snapshots_for_source(session, source, account_id)
    return {"snapshots": [s.to_dict() for s in snapshots]}


@router.get("/quota/history/{account_id}/{model_id}")
async def get_quota_history(
    account_id: str,
    model_id: str,
    hours: int = 48,
    session: AsyncSession = Depends(get_session),
):
    """Quota history for a specific model over the last N hours."""
    history = await quota_crud.get_snapshot_history(
        session, account_id, model_id, hours
    )
    return {"history": [s.to_dict() for s in history]}


@router.get("/gemini/limits")
async def get_gemini_limits(session: AsyncSession = Depends(get_session)):
    """Get all Gemini quota configs."""
    result = await session.execute(select(GeminiQuotaConfig))
    configs = result.scalars().all()
    return {"configs": [c.to_dict() for c in configs]}


@router.put("/gemini/limits/{model_id}")
async def update_gemini_limit(
    model_id: str,
    body: GeminiLimitUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Update a Gemini quota config."""
    result = await session.execute(
        select(GeminiQuotaConfig).filter(GeminiQuotaConfig.model_id == model_id)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Gemini config not found")
    
    config.rpm = body.rpm
    config.tpm = body.tpm
    config.rpd = body.rpd
    await session.commit()
    return {"config": config.to_dict()}
