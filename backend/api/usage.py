"""Usage API — historical usage records + CSV import."""

from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from crud import usage as usage_crud
from adapters.cursor_adapter import CursorAdapter
from normalizer.schema import normalize_usage_record

router = APIRouter(tags=["Usage"])


@router.get("/usage")
async def get_usage(
    source: str | None = Query(None),
    account_id: str | None = Query(None),
    model_id: str | None = Query(None),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    limit: int = Query(500, le=5000),
    offset: int = Query(0),
    session: AsyncSession = Depends(get_session),
):
    """Historical usage records with filters."""
    records = await usage_crud.get_usage_records(
        session,
        source=source,
        account_id=account_id,
        model_id=model_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return {"records": [r.to_dict() for r in records], "count": len(records)}


@router.get("/usage/summary")
async def get_usage_summary(
    source: str | None = Query(None),
    account_id: str | None = Query(None),
    days: int = Query(30, le=365),
    session: AsyncSession = Depends(get_session),
):
    """Aggregated usage totals per model per day."""
    summary = await usage_crud.get_usage_summary(
        session, source=source, account_id=account_id, days=days
    )
    return {"summary": summary}


@router.post("/cursor/import")
async def import_cursor_csv(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
):
    """Upload Cursor CSV export (Individual Pro fallback)."""
    content = await file.read()
    csv_text = content.decode("utf-8")

    raw_records = CursorAdapter.parse_csv(csv_text, account_id="cursor")
    orm_records = [normalize_usage_record(r) for r in raw_records]
    added = await usage_crud.add_usage_records(session, orm_records)

    return {
        "message": f"Imported {added} records from CSV",
        "total_parsed": len(raw_records),
        "added": added,
    }
