"""Cursor adapter — REST API client + CSV parser."""

import csv
import io
import logging
from datetime import datetime
from typing import Any

import httpx

from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)

BASE_URL = "https://api.cursor.com"


class CursorAdapter(BaseAdapter):
    """
    Cursor Teams/Enterprise: full REST API at api.cursor.com.
    Individual Pro: CSV export uploaded manually.
    """

    def __init__(self, account_id: str, api_key: str | None = None):
        super().__init__(account_id)
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    async def fetch_quota(self) -> list[dict[str, Any]]:
        if not self.api_key:
            return []

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{BASE_URL}/v1/me", headers=self.headers
            )
            resp.raise_for_status()
            data = resp.json()

            return [
                {
                    "account_id": self.account_id,
                    "source": "cursor",
                    "model_id": "cursor-plan",
                    "model_label": data.get("plan", {}).get("name", "Cursor Pro"),
                    "credits_used": None,
                    "credits_total": None,
                    "reset_at": data.get("billing_cycle_end"),
                    "reset_cadence": "monthly",
                    "quota_remaining_pct": None,
                    "is_exhausted": False,
                }
            ]

    async def fetch_usage(self, since: str | None = None) -> list[dict[str, Any]]:
        if not self.api_key:
            return []

        params = {}
        if since:
            params["start"] = since

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{BASE_URL}/analytics/team/usage",
                headers=self.headers,
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

            records = []
            for entry in data.get("usage", []):
                records.append(
                    {
                        "account_id": self.account_id,
                        "source": "cursor",
                        "timestamp": entry.get("date", datetime.utcnow().isoformat()),
                        "model_id": entry.get("model", "unknown"),
                        "model_label": entry.get("model_name", entry.get("model", "Unknown")),
                        "input_tokens": entry.get("input_tokens", 0),
                        "output_tokens": entry.get("output_tokens", 0),
                        "cache_tokens": entry.get("cache_tokens", 0),
                        "request_count": entry.get("request_count", 1),
                        "cost_usd": entry.get("cost_usd"),
                        "request_type": entry.get("request_type"),
                        "external_id": entry.get("request_id"),
                    }
                )
            return records

    @staticmethod
    def parse_csv(csv_content: str, account_id: str = "cursor") -> list[dict[str, Any]]:
        """
        Parse a CSV export from cursor.com/dashboard.
        Returns a list of usage record dicts.
        """
        records = []
        reader = csv.DictReader(io.StringIO(csv_content))
        for row in reader:
            try:
                records.append(
                    {
                        "account_id": account_id,
                        "source": "cursor",
                        "timestamp": row.get("date", row.get("Date", "")),
                        "model_id": row.get("model", row.get("Model", "unknown")),
                        "model_label": row.get("model_name", row.get("Model", "Unknown")),
                        "input_tokens": int(row.get("input_tokens", row.get("Input Tokens", 0))),
                        "output_tokens": int(row.get("output_tokens", row.get("Output Tokens", 0))),
                        "cache_tokens": int(row.get("cache_tokens", row.get("Cache Tokens", 0))),
                        "request_count": int(row.get("requests", row.get("Requests", 1))),
                        "cost_usd": float(row.get("cost", row.get("Cost (USD)", 0))) or None,
                        "request_type": row.get("type", row.get("Type")),
                        "external_id": None,
                    }
                )
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping malformed CSV row: {e}")
                continue
        return records
