"""Alerts API — CRUD for alert rules."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from crud import alerts as alerts_crud

router = APIRouter(tags=["Alerts"])


class AlertCreate(BaseModel):
    label: str
    account_id: str | None = None
    source: str | None = None
    model_id: str | None = None
    threshold_pct: float = 0.75
    channel: str = "desktop"
    webhook_url: str | None = None
    cooldown_minutes: int = 60


class AlertUpdate(BaseModel):
    label: str | None = None
    threshold_pct: float | None = None
    channel: str | None = None
    webhook_url: str | None = None
    cooldown_minutes: int | None = None
    is_active: bool | None = None


@router.get("/alerts")
async def list_alerts(session: AsyncSession = Depends(get_session)):
    """List all alert rules."""
    alerts = await alerts_crud.get_all_alerts(session)
    return {"alerts": [a.to_dict() for a in alerts]}


@router.post("/alerts")
async def create_alert(
    body: AlertCreate, session: AsyncSession = Depends(get_session)
):
    """Create a new alert rule."""
    alert = await alerts_crud.create_alert(session, body.model_dump())
    return {"alert": alert.to_dict()}


@router.put("/alerts/{alert_id}")
async def update_alert(
    alert_id: str,
    body: AlertUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Update an alert rule."""
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    alert = await alerts_crud.update_alert(session, alert_id, data)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"alert": alert.to_dict()}


@router.delete("/alerts/{alert_id}")
async def delete_alert(
    alert_id: str, session: AsyncSession = Depends(get_session)
):
    """Delete an alert rule."""
    deleted = await alerts_crud.delete_alert(session, alert_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert deleted"}


@router.post("/alerts/{alert_id}/test")
async def test_alert(
    alert_id: str, session: AsyncSession = Depends(get_session)
):
    """Test fire an alert rule."""
    alert = await alerts_crud.get_alert(session, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    msg = f"[TEST] QuotaLens Alert Triggered: {alert.label} (Threshold: {alert.threshold_pct * 100}%)"
    
    if alert.channel == "desktop":
        try:
            from plyer import notification
            notification.notify(
                title="QuotaLens Test Alert",
                message=msg,
                timeout=5,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Desktop notification failed: {str(e)}")
    elif alert.channel == "webhook" and alert.webhook_url:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(
                    alert.webhook_url,
                    json={
                        "text": msg,
                        "content": msg,
                        "username": "QuotaLens Test",
                    },
                    timeout=5.0,
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Webhook delivery failed: {str(e)}")
            
    return {"ok": True, "message": "Test notification triggered"}
