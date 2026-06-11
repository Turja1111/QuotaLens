"""Celery app configuration with Redis broker."""

from celery import Celery
from celery.schedules import crontab
from config import settings

app = Celery(
    "quotalens",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["scheduler.tasks"],
)

app.conf.update(
    timezone="UTC",
    enable_utc=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    worker_hijack_root_logger=False,
)

# Periodic task schedule
app.conf.beat_schedule = {
    "poll-antigravity": {
        "task": "scheduler.tasks.poll_antigravity",
        "schedule": 300,  # every 5 minutes
    },
    "poll-openrouter": {
        "task": "scheduler.tasks.poll_openrouter",
        "schedule": 900,  # every 15 minutes
    },
    "poll-cursor": {
        "task": "scheduler.tasks.poll_cursor",
        "schedule": 900,  # every 15 minutes
    },
    "poll-gemini": {
        "task": "scheduler.tasks.poll_gemini",
        "schedule": 3600,  # every 1 hour
    },
    "poll-copilot": {
        "task": "scheduler.tasks.poll_copilot",
        "schedule": crontab(hour=2, minute=0),  # 02:00 UTC daily
    },
    "check-alerts": {
        "task": "scheduler.tasks.check_alerts",
        "schedule": 60,  # every 1 minute
    },
}
