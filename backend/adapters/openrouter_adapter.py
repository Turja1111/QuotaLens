"""OpenRouter adapter — REST API client (dual-account support)."""

import logging
from datetime import datetime
from typing import Any

import httpx

from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class OpenRouterAdapter(BaseAdapter):
    """
    OpenRouter API client supporting free models.
    Each Gmail account has its own API key pair (inference + management).
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        account_id: str,
        api_key: str,
        mgmt_key: str | None = None,
        gmail_slot: str = "gmail1",
    ):
        super().__init__(account_id)
        self.api_key = api_key
        self.mgmt_key = mgmt_key
        self.gmail_slot = gmail_slot
        self.headers = {"Authorization": f"Bearer {api_key}"}

    async def fetch_quota(self) -> list[dict[str, Any]]:
        """Fetch rate limit status and optional credit balance."""
        snapshots = []

        async with httpx.AsyncClient(timeout=15.0) as client:
            # Key status — rate limits and daily remaining
            try:
                key_resp = await client.get(
                    f"{self.BASE_URL}/key", headers=self.headers
                )
                if key_resp.status_code == 200:
                    key_data = key_resp.json().get("data", {})
                    limit = key_data.get("limit", 1000)
                    usage_count = key_data.get("usage", 0)
                    rate_limit = key_data.get("rate_limit", {})

                    snapshots.append(
                        {
                            "account_id": self.account_id,
                            "source": "openrouter",
                            "model_id": "openrouter-daily",
                            "model_label": "Daily Free Requests",
                            "quota_remaining_pct": max(0.0, 1.0 - (usage_count / limit)) if limit > 0 else 1.0,
                            "is_exhausted": usage_count >= limit,
                            "requests_used": usage_count,
                            "requests_total": limit,
                            "credits_used": None,
                            "credits_total": None,
                            "reset_at": None,  # ~midnight UTC
                            "reset_cadence": "daily",
                        }
                    )
            except Exception as e:
                logger.warning(f"OpenRouter key fetch failed: {e}")

            # Credits (requires Management key)
            if self.mgmt_key:
                try:
                    credit_resp = await client.get(
                        f"{self.BASE_URL}/credits",
                        headers={"Authorization": f"Bearer {self.mgmt_key}"},
                    )
                    if credit_resp.status_code == 200:
                        credit_data = credit_resp.json().get("data", {})
                        total = credit_data.get("total_credits", 0)
                        used = credit_data.get("total_usage", 0)

                        snapshots.append(
                            {
                                "account_id": self.account_id,
                                "source": "openrouter",
                                "model_id": "openrouter-credits",
                                "model_label": "Credits",
                                "quota_remaining_pct": max(0.0, 1.0 - (used / total)) if total > 0 else 1.0,
                                "is_exhausted": used >= total,
                                "requests_used": None,
                                "requests_total": None,
                                "credits_used": used,
                                "credits_total": total,
                                "reset_at": None,
                                "reset_cadence": "monthly",
                            }
                        )
                except Exception as e:
                    logger.warning(f"OpenRouter credits fetch failed: {e}")

        return snapshots

    async def fetch_usage(self, since: str | None = None) -> list[dict[str, Any]]:
        """Fetch recent generation activity."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/generations",
                    params={"limit": 200},
                    headers=self.headers,
                )
                if resp.status_code != 200:
                    return []

                data = resp.json().get("data", [])
                records = []

                for gen in data:
                    timestamp = gen.get("created_at", datetime.utcnow().isoformat())

                    # Filter by since date if provided
                    if since and timestamp < since:
                        continue

                    records.append(
                        {
                            "account_id": self.account_id,
                            "source": "openrouter",
                            "timestamp": timestamp,
                            "model_id": gen.get("model", "unknown"),
                            "model_label": gen.get("model", "Unknown"),
                            "input_tokens": gen.get("tokens_prompt", 0),
                            "output_tokens": gen.get("tokens_completion", 0),
                            "cache_tokens": 0,
                            "request_count": 1,
                            "cost_usd": gen.get("total_cost"),
                            "request_type": "completion",
                            "external_id": gen.get("id"),
                        }
                    )

                return records

            except Exception as e:
                logger.error(f"OpenRouter usage fetch failed: {e}")
                return []
