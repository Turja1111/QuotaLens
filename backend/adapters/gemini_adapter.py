"""Gemini adapter — local counter strategy + rate-limit header parser."""

import logging
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)

# Pacific timezone for Gemini quota resets
PACIFIC_TZ = ZoneInfo("America/Los_Angeles")

# Default free tier limits (also stored in gemini_quota_config table)
DEFAULT_LIMITS = {
    "gemini-3.5-flash": {"rpm": 10, "tpm": 250000, "rpd": 1500},
    "gemini-3-flash-preview": {"rpm": 10, "tpm": 250000, "rpd": 1500},
    "gemini-2.5-flash-preview": {"rpm": 15, "tpm": 1000000, "rpd": 1500},
    "gemini-3.1-pro-preview": {"rpm": 2, "tpm": 32000, "rpd": 50},
    "gemini-3-pro-preview": {"rpm": 2, "tpm": 32000, "rpd": 50},
    "gemini-2.5-pro": {"rpm": 5, "tpm": 250000, "rpd": 50},
}


class GeminiAdapter(BaseAdapter):
    """
    No official remaining-quota endpoint from Google.
    Maintains a local counter per API key / model / day in PostgreSQL.
    """

    def __init__(
        self,
        account_id: str,
        api_key: str | None = None,
        gmail_slot: str = "gmail1",
        db_session=None,
    ):
        super().__init__(account_id)
        self.api_key = api_key
        self.gmail_slot = gmail_slot
        self.db_session = db_session

    @staticmethod
    def get_reset_time() -> datetime:
        """Next midnight Pacific Time."""
        now_pacific = datetime.now(PACIFIC_TZ)
        tomorrow = now_pacific.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        return tomorrow

    async def fetch_quota(self) -> list[dict[str, Any]]:
        """
        Build quota snapshots from local counters.
        Each model gets a snapshot showing requests_used vs rpd limit.
        """
        if not self.api_key:
            return []

        reset_at = self.get_reset_time()
        snapshots = []

        for model_id, limits in DEFAULT_LIMITS.items():
            rpd = limits["rpd"]
            # In production, requests_used would come from the DB counter
            requests_used = 0  # Placeholder — actual count from DB

            snapshots.append(
                {
                    "account_id": self.account_id,
                    "source": "gemini",
                    "model_id": model_id,
                    "model_label": self._model_label(model_id),
                    "quota_remaining_pct": max(0.0, 1.0 - (requests_used / rpd)) if rpd > 0 else 1.0,
                    "is_exhausted": requests_used >= rpd,
                    "requests_used": requests_used,
                    "requests_total": rpd,
                    "credits_used": None,
                    "credits_total": None,
                    "reset_at": reset_at.isoformat(),
                    "reset_cadence": "daily",
                }
            )

        return snapshots

    async def fetch_usage(self, since: str | None = None) -> list[dict[str, Any]]:
        """Usage records come from the local counter — return empty for adapter."""
        return []

    @staticmethod
    def parse_rate_limit_headers(headers: dict) -> dict[str, Any] | None:
        """
        Parse x-ratelimit-remaining-requests and x-ratelimit-reset-requests
        from Gemini API response headers.
        """
        remaining = headers.get("x-ratelimit-remaining-requests")
        reset_str = headers.get("x-ratelimit-reset-requests")
        if remaining is not None:
            return {
                "remaining_requests": int(remaining),
                "reset": reset_str,
            }
        return None

    @staticmethod
    def _model_label(model_id: str) -> str:
        """Convert model ID to human-readable label."""
        labels = {
            "gemini-3.5-flash": "Gemini 3.5 Flash",
            "gemini-3-flash-preview": "Gemini 3 Flash Preview",
            "gemini-2.5-flash-preview": "Gemini 2.5 Flash Preview",
            "gemini-3.1-pro-preview": "Gemini 3.1 Pro Preview",
            "gemini-3-pro-preview": "Gemini 3 Pro Preview",
            "gemini-2.5-pro": "Gemini 2.5 Pro",
        }
        return labels.get(model_id, model_id)
