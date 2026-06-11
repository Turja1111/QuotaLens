"""Copilot adapter — GitHub Copilot REST API client."""

import logging
from datetime import datetime
from typing import Any

import httpx

from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)

BASE_URL = "https://api.github.com"
API_VERSION = "2026-03-10"


class CopilotAdapter(BaseAdapter):
    """GitHub Copilot usage via REST API."""

    def __init__(self, account_id: str, pat: str, org: str | None = None):
        super().__init__(account_id)
        self.pat = pat
        self.org = org
        self.headers = {
            "Authorization": f"Bearer {pat}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }

    async def fetch_quota(self) -> list[dict[str, Any]]:
        """Fetch billing/seat info for the Copilot plan."""
        if not self.pat:
            return []

        async with httpx.AsyncClient(timeout=15.0) as client:
            if self.org:
                resp = await client.get(
                    f"{BASE_URL}/orgs/{self.org}/copilot/billing",
                    headers=self.headers,
                )
            else:
                # Individual user — use preview endpoint
                resp = await client.get(
                    f"{BASE_URL}/user/copilot",
                    headers=self.headers,
                )

            if resp.status_code == 200:
                data = resp.json()
                return [
                    {
                        "account_id": self.account_id,
                        "source": "copilot",
                        "model_id": "copilot-plan",
                        "model_label": "GitHub Copilot",
                        "quota_remaining_pct": None,
                        "is_exhausted": False,
                        "requests_used": None,
                        "requests_total": None,
                        "credits_used": None,
                        "credits_total": None,
                        "reset_at": None,
                        "reset_cadence": "monthly",
                    }
                ]
            else:
                logger.warning(f"Copilot billing returned {resp.status_code}")
                return []

    async def fetch_usage(self, since: str | None = None) -> list[dict[str, Any]]:
        """Fetch daily usage with per-model breakdown."""
        if not self.pat:
            return []

        params = {}
        if since:
            params["since"] = since

        async with httpx.AsyncClient(timeout=15.0) as client:
            if self.org:
                url = f"{BASE_URL}/orgs/{self.org}/copilot/usage"
            else:
                url = f"{BASE_URL}/user/copilot/usage"

            resp = await client.get(url, headers=self.headers, params=params)

            if resp.status_code != 200:
                logger.warning(f"Copilot usage returned {resp.status_code}")
                return []

            data = resp.json()
            records = []

            for day_entry in data if isinstance(data, list) else data.get("usage", []):
                for breakdown in day_entry.get("breakdown", []):
                    records.append(
                        {
                            "account_id": self.account_id,
                            "source": "copilot",
                            "timestamp": day_entry.get("day", datetime.utcnow().isoformat()),
                            "model_id": breakdown.get("model", "unknown"),
                            "model_label": breakdown.get("model", "Unknown"),
                            "input_tokens": breakdown.get("input_tokens", 0),
                            "output_tokens": breakdown.get("output_tokens", 0),
                            "cache_tokens": breakdown.get("cache_tokens", 0),
                            "request_count": breakdown.get("suggestions_count", 0)
                            + breakdown.get("acceptances_count", 0),
                            "cost_usd": None,
                            "request_type": breakdown.get("language"),
                            "external_id": None,
                        }
                    )
            return records
