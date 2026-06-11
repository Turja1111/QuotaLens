"""CRUD operations for alert rules."""

import uuid
from datetime import datetime, timedelta
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.alert_rule import AlertRule


async def get_all_alerts(
    session: AsyncSession, active_only: bool = False
) -> list[AlertRule]:
    stmt = select(AlertRule)
    if active_only:
        stmt = stmt.where(AlertRule.is_active == True)
    stmt = stmt.order_by(AlertRule.label)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_alert(session: AsyncSession, alert_id: str) -> AlertRule | None:
    result = await session.execute(
        select(AlertRule).where(AlertRule.id == uuid.UUID(alert_id))
    )
    return result.scalar_one_or_none()


async def create_alert(session: AsyncSession, data: dict) -> AlertRule:
    alert = AlertRule(id=uuid.uuid4(), **data)
    session.add(alert)
    await session.flush()
    return alert


async def update_alert(
    session: AsyncSession, alert_id: str, data: dict
) -> AlertRule | None:
    alert = await get_alert(session, alert_id)
    if not alert:
        return None
    for key, value in data.items():
        if hasattr(alert, key) and key != "id":
            setattr(alert, key, value)
    await session.flush()
    return alert


async def delete_alert(session: AsyncSession, alert_id: str) -> bool:
    result = await session.execute(
        delete(AlertRule).where(AlertRule.id == uuid.UUID(alert_id))
    )
    return result.rowcount > 0


async def get_fireable_alerts(session: AsyncSession) -> list[AlertRule]:
    """Get active alerts whose cooldown has expired."""
    now = datetime.utcnow()
    stmt = select(AlertRule).where(AlertRule.is_active == True)
    result = await session.execute(stmt)
    alerts = result.scalars().all()

    fireable = []
    for alert in alerts:
        if alert.last_fired_at is None:
            fireable.append(alert)
        elif now - alert.last_fired_at > timedelta(minutes=alert.cooldown_minutes):
            fireable.append(alert)

    return fireable


async def mark_alert_fired(session: AsyncSession, alert_id: uuid.UUID) -> None:
    alert = await session.get(AlertRule, alert_id)
    if alert:
        alert.last_fired_at = datetime.utcnow()
        await session.flush()
