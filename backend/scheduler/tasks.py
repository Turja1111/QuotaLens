"""Celery polling tasks and alert checker."""

import asyncio
import logging
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from scheduler.celery_app import app
from config import settings
from models import Base
from models.quota_snapshot import QuotaSnapshot
from models.usage_record import UsageRecord
from models.alert_rule import AlertRule
from normalizer.schema import normalize_quota_snapshot, normalize_usage_record

logger = logging.getLogger(__name__)

# Sync session for Celery tasks
sync_engine = create_engine(settings.database_url_sync, pool_pre_ping=True)
SyncSession = sessionmaker(bind=sync_engine)


def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@app.task(name="scheduler.tasks.poll_antigravity")
def poll_antigravity():
    """Poll Antigravity quota for both Gmail accounts."""
    from adapters.antigravity_adapter import AntigravityAdapter

    accounts = [
        ("gmail1_antigravity", settings.antigravity_dir_gmail1, "gmail1"),
        ("gmail2_antigravity", settings.antigravity_dir_gmail2, "gmail2"),
    ]

    with SyncSession() as session:
        for account_id, dir_path, slot in accounts:
            try:
                adapter = AntigravityAdapter(account_id, dir_path, slot)
                raw_snapshots = _run_async(adapter.fetch_quota())

                for raw in raw_snapshots:
                    snapshot = normalize_quota_snapshot(raw)
                    session.add(snapshot)

                logger.info(
                    f"Antigravity {slot}: {len(raw_snapshots)} quota snapshots saved"
                )
            except Exception as e:
                logger.error(f"Antigravity {slot} poll failed: {e}")

        session.commit()


@app.task(name="scheduler.tasks.poll_openrouter")
def poll_openrouter():
    """Poll OpenRouter for both Gmail accounts."""
    from adapters.openrouter_adapter import OpenRouterAdapter

    accounts = [
        (
            "gmail1_openrouter",
            settings.openrouter_api_key_gmail1,
            settings.openrouter_mgmt_key_gmail1,
            "gmail1",
        ),
        (
            "gmail2_openrouter",
            settings.openrouter_api_key_gmail2,
            settings.openrouter_mgmt_key_gmail2,
            "gmail2",
        ),
    ]

    with SyncSession() as session:
        for account_id, api_key, mgmt_key, slot in accounts:
            if not api_key:
                continue
            try:
                adapter = OpenRouterAdapter(account_id, api_key, mgmt_key, slot)

                # Quota snapshots
                raw_snapshots = _run_async(adapter.fetch_quota())
                for raw in raw_snapshots:
                    snapshot = normalize_quota_snapshot(raw)
                    session.add(snapshot)

                # Usage records
                raw_usage = _run_async(adapter.fetch_usage())
                for raw in raw_usage:
                    record = normalize_usage_record(raw)
                    # Deduplication by external_id
                    if record.external_id:
                        from sqlalchemy import select
                        existing = session.execute(
                            select(UsageRecord.id).where(
                                UsageRecord.external_id == record.external_id
                            )
                        ).scalar_one_or_none()
                        if existing:
                            continue
                    session.add(record)

                logger.info(f"OpenRouter {slot}: polled successfully")
            except Exception as e:
                logger.error(f"OpenRouter {slot} poll failed: {e}")

        session.commit()


@app.task(name="scheduler.tasks.poll_cursor")
def poll_cursor():
    """Poll Cursor API."""
    from adapters.cursor_adapter import CursorAdapter

    if not settings.cursor_api_key:
        logger.debug("Cursor API key not configured — skipping")
        return

    with SyncSession() as session:
        try:
            adapter = CursorAdapter("cursor", settings.cursor_api_key)

            raw_snapshots = _run_async(adapter.fetch_quota())
            for raw in raw_snapshots:
                snapshot = normalize_quota_snapshot(raw)
                session.add(snapshot)

            raw_usage = _run_async(adapter.fetch_usage())
            for raw in raw_usage:
                record = normalize_usage_record(raw)
                session.add(record)

            session.commit()
            logger.info("Cursor: polled successfully")
        except Exception as e:
            logger.error(f"Cursor poll failed: {e}")


@app.task(name="scheduler.tasks.poll_gemini")
def poll_gemini():
    """Poll Gemini API quota for both Gmail accounts."""
    from adapters.gemini_adapter import GeminiAdapter

    accounts = [
        ("gmail1_gemini", settings.gemini_api_key_gmail1, "gmail1"),
        ("gmail2_gemini", settings.gemini_api_key_gmail2, "gmail2"),
    ]

    with SyncSession() as session:
        for account_id, api_key, slot in accounts:
            if not api_key:
                continue
            try:
                adapter = GeminiAdapter(account_id, api_key, slot)
                raw_snapshots = _run_async(adapter.fetch_quota())
                for raw in raw_snapshots:
                    snapshot = normalize_quota_snapshot(raw)
                    session.add(snapshot)

                logger.info(f"Gemini {slot}: {len(raw_snapshots)} snapshots saved")
            except Exception as e:
                logger.error(f"Gemini {slot} poll failed: {e}")

        session.commit()


@app.task(name="scheduler.tasks.poll_copilot")
def poll_copilot():
    """Poll GitHub Copilot API — runs daily."""
    from adapters.copilot_adapter import CopilotAdapter

    if not settings.github_pat:
        logger.debug("GitHub PAT not configured — skipping Copilot poll")
        return

    with SyncSession() as session:
        try:
            adapter = CopilotAdapter("copilot", settings.github_pat, settings.github_org)

            raw_snapshots = _run_async(adapter.fetch_quota())
            for raw in raw_snapshots:
                snapshot = normalize_quota_snapshot(raw)
                session.add(snapshot)

            raw_usage = _run_async(adapter.fetch_usage())
            for raw in raw_usage:
                record = normalize_usage_record(raw)
                session.add(record)

            session.commit()
            logger.info("Copilot: polled successfully")
        except Exception as e:
            logger.error(f"Copilot poll failed: {e}")


@app.task(name="scheduler.tasks.check_alerts")
def check_alerts():
    """Check all active alert rules against latest quota snapshots."""
    from sqlalchemy import select

    with SyncSession() as session:
        # Get active alerts with expired cooldown
        alerts = session.execute(
            select(AlertRule).where(AlertRule.is_active == True)
        ).scalars().all()

        if not alerts:
            return

        # Get latest snapshots (simplified — get most recent per model)
        from sqlalchemy import func, and_
        subq = (
            select(
                QuotaSnapshot.account_id,
                QuotaSnapshot.model_id,
                func.max(QuotaSnapshot.snapshot_at).label("max_at"),
            )
            .group_by(QuotaSnapshot.account_id, QuotaSnapshot.model_id)
            .subquery()
        )
        snapshots = session.execute(
            select(QuotaSnapshot).join(
                subq,
                and_(
                    QuotaSnapshot.account_id == subq.c.account_id,
                    QuotaSnapshot.model_id == subq.c.model_id,
                    QuotaSnapshot.snapshot_at == subq.c.max_at,
                ),
            )
        ).scalars().all()

        now = datetime.utcnow()

        for alert in alerts:
            # Check cooldown
            if alert.last_fired_at:
                from datetime import timedelta
                if now - alert.last_fired_at < timedelta(minutes=alert.cooldown_minutes):
                    continue

            # Match snapshots
            for snap in snapshots:
                if alert.account_id and snap.account_id != alert.account_id:
                    continue
                if alert.source and snap.source != alert.source:
                    continue
                if alert.model_id and snap.model_id != alert.model_id:
                    continue

                # Calculate usage percentage
                usage_pct = 0.0
                if snap.quota_remaining_pct is not None:
                    usage_pct = 1.0 - snap.quota_remaining_pct
                elif snap.requests_used and snap.requests_total:
                    usage_pct = snap.requests_used / snap.requests_total
                elif snap.credits_used and snap.credits_total:
                    usage_pct = float(snap.credits_used) / float(snap.credits_total)

                if usage_pct >= alert.threshold_pct:
                    _fire_alert(alert, snap, usage_pct)
                    alert.last_fired_at = now
                    break

        session.commit()


def _fire_alert(alert: AlertRule, snapshot: QuotaSnapshot, usage_pct: float):
    """Fire an alert notification."""
    msg = (
        f"⚠️ QuotaLens Alert: {alert.label}\n"
        f"{snapshot.model_label} ({snapshot.source}) — "
        f"{usage_pct:.0%} used"
    )
    logger.warning(msg)

    if alert.channel == "desktop":
        try:
            from plyer import notification
            notification.notify(
                title="QuotaLens Alert",
                message=msg,
                timeout=10,
            )
        except Exception as e:
            logger.error(f"Desktop notification failed: {e}")

    elif alert.channel == "webhook" and alert.webhook_url:
        try:
            import httpx
            httpx.post(
                alert.webhook_url,
                json={
                    "text": msg,
                    "content": msg,
                    "username": "QuotaLens",
                },
                timeout=10.0,
            )
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
