"""Normalizer — converts raw adapter output into ORM model instances."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from models.usage_record import UsageRecord
from models.quota_snapshot import QuotaSnapshot


def normalize_usage_record(raw: dict[str, Any]) -> UsageRecord:
    """Convert a raw adapter dict into a UsageRecord model instance."""
    timestamp = raw.get("timestamp")
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            timestamp = datetime.utcnow()
    elif timestamp is None:
        timestamp = datetime.utcnow()

    cost = raw.get("cost_usd")
    if cost is not None:
        cost = Decimal(str(cost))

    return UsageRecord(
        id=uuid.uuid4(),
        account_id=raw["account_id"],
        source=raw["source"],
        timestamp=timestamp,
        model_id=raw.get("model_id", "unknown"),
        model_label=raw.get("model_label", "Unknown"),
        input_tokens=int(raw.get("input_tokens", 0)),
        output_tokens=int(raw.get("output_tokens", 0)),
        cache_tokens=int(raw.get("cache_tokens", 0)),
        request_count=int(raw.get("request_count", 1)),
        cost_usd=cost,
        request_type=raw.get("request_type"),
        external_id=raw.get("external_id"),
    )


def normalize_quota_snapshot(raw: dict[str, Any]) -> QuotaSnapshot:
    """Convert a raw adapter dict into a QuotaSnapshot model instance."""
    reset_at = raw.get("reset_at")
    if isinstance(reset_at, str):
        try:
            reset_at = datetime.fromisoformat(reset_at.replace("Z", "+00:00"))
        except ValueError:
            reset_at = None

    credits_used = raw.get("credits_used")
    credits_total = raw.get("credits_total")
    if credits_used is not None:
        credits_used = Decimal(str(credits_used))
    if credits_total is not None:
        credits_total = Decimal(str(credits_total))

    return QuotaSnapshot(
        id=uuid.uuid4(),
        account_id=raw["account_id"],
        source=raw["source"],
        model_id=raw.get("model_id", "unknown"),
        model_label=raw.get("model_label", "Unknown"),
        snapshot_at=datetime.utcnow(),
        quota_remaining_pct=raw.get("quota_remaining_pct"),
        is_exhausted=raw.get("is_exhausted", False),
        requests_used=raw.get("requests_used"),
        requests_total=raw.get("requests_total"),
        credits_used=credits_used,
        credits_total=credits_total,
        reset_at=reset_at,
        reset_cadence=raw.get("reset_cadence", "daily"),
    )


def normalize_batch(
    raw_records: list[dict[str, Any]], record_type: str = "usage"
) -> list[UsageRecord | QuotaSnapshot]:
    """Normalize a batch of raw dicts into model instances."""
    if record_type == "usage":
        return [normalize_usage_record(r) for r in raw_records]
    elif record_type == "quota":
        return [normalize_quota_snapshot(r) for r in raw_records]
    else:
        raise ValueError(f"Unknown record_type: {record_type}")
