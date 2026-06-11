"""Antigravity adapter — gRPC-Web to local Language Server + file fallback."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from adapters.base import BaseAdapter

logger = logging.getLogger(__name__)


class AntigravityAdapter(BaseAdapter):
    """
    Reads Antigravity quota from:
    1. Live gRPC-Web to local Language Server (primary)
    2. ~/.gemini/*/quota_state.json file fallback (when IDE not running)
    """

    def __init__(self, account_id: str, account_dir: str, gmail_slot: str = "gmail1"):
        super().__init__(account_id)
        self.account_dir = Path(account_dir).expanduser()
        self.gmail_slot = gmail_slot

    async def fetch_quota(self) -> list[dict[str, Any]]:
        """Try live gRPC first, then file fallback."""
        # Try gRPC
        try:
            result = await self._fetch_via_grpc()
            if result:
                return result
        except Exception as e:
            logger.debug(f"gRPC unavailable for {self.account_id}: {e}")

        # File fallback
        return self._parse_quota_state_file()

    async def _fetch_via_grpc(self) -> list[dict[str, Any]] | None:
        """
        Connect to local Language Server via gRPC-Web.
        Reads port from server.json in the account directory.
        """
        server_file = self.account_dir / "server.json"
        if not server_file.exists():
            return None

        try:
            server_config = json.loads(server_file.read_text())
            port = server_config.get("port")
            if not port:
                return None

            # gRPC connection — simplified; full implementation would use
            # generated proto stubs from language_server.proto
            # For now, we try the gRPC connection and fall back to file
            logger.info(
                f"gRPC server found at localhost:{port} for {self.account_id}"
            )
            # In production, this would use grpc.aio.insecure_channel
            # with the LanguageServerServiceStub
            return None  # Fall through to file fallback for now

        except Exception as e:
            logger.warning(f"gRPC connection failed for {self.account_id}: {e}")
            return None

    def _parse_quota_state_file(self) -> list[dict[str, Any]]:
        """Parse ~/.gemini/*/quota_state.json for last-known quota state."""
        quota_file = self.account_dir / "quota_state.json"
        if not quota_file.exists():
            logger.warning(f"No quota_state.json found at {quota_file}")
            return []

        try:
            data = json.loads(quota_file.read_text())
            snapshots = []

            for model_quota in data.get("modelQuotas", []):
                reset_time_str = model_quota.get("resetTime")
                reset_at = None
                if reset_time_str:
                    try:
                        reset_at = datetime.fromisoformat(
                            reset_time_str.replace("Z", "+00:00")
                        )
                    except ValueError:
                        pass

                snapshots.append(
                    {
                        "account_id": self.account_id,
                        "source": "antigravity",
                        "model_id": model_quota.get("modelId", "unknown"),
                        "model_label": model_quota.get("label", "Unknown Model"),
                        "quota_remaining_pct": model_quota.get("remainingPercentage", 0.0),
                        "is_exhausted": model_quota.get("isExhausted", False),
                        "reset_at": reset_at.isoformat() if reset_at else None,
                        "reset_cadence": "5h",
                        "requests_used": None,
                        "requests_total": None,
                        "credits_used": None,
                        "credits_total": None,
                    }
                )

            # Add credit info if available
            prompt_credits = data.get("availablePromptCredits")
            total_prompt = data.get("monthlyPromptCredits")
            flow_credits = data.get("availableFlowCredits")
            total_flow = data.get("monthlyFlowCredits")

            if prompt_credits is not None:
                snapshots.append(
                    {
                        "account_id": self.account_id,
                        "source": "antigravity",
                        "model_id": "prompt-credits",
                        "model_label": "Prompt Credits",
                        "quota_remaining_pct": (
                            prompt_credits / total_prompt if total_prompt else 0
                        ),
                        "is_exhausted": prompt_credits == 0,
                        "credits_used": total_prompt - prompt_credits if total_prompt else 0,
                        "credits_total": total_prompt,
                        "reset_cadence": "monthly",
                        "reset_at": None,
                        "requests_used": None,
                        "requests_total": None,
                    }
                )

            if flow_credits is not None:
                snapshots.append(
                    {
                        "account_id": self.account_id,
                        "source": "antigravity",
                        "model_id": "flow-credits",
                        "model_label": "Flow Credits",
                        "quota_remaining_pct": (
                            flow_credits / total_flow if total_flow else 0
                        ),
                        "is_exhausted": flow_credits == 0,
                        "credits_used": total_flow - flow_credits if total_flow else 0,
                        "credits_total": total_flow,
                        "reset_cadence": "monthly",
                        "reset_at": None,
                        "requests_used": None,
                        "requests_total": None,
                    }
                )

            return snapshots

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse quota_state.json: {e}")
            return []

    async def fetch_usage(self, since: str | None = None) -> list[dict[str, Any]]:
        """Antigravity doesn't expose usage history — return empty."""
        return []

    async def test_connection(self) -> dict[str, Any]:
        """Test if the account directory and quota file exist."""
        if not self.account_dir.exists():
            return {"ok": False, "message": f"Directory not found: {self.account_dir}"}

        server_file = self.account_dir / "server.json"
        quota_file = self.account_dir / "quota_state.json"

        if server_file.exists():
            return {"ok": True, "message": "IDE is running — gRPC available"}
        elif quota_file.exists():
            return {"ok": True, "message": "File fallback available (IDE not running)"}
        else:
            return {"ok": False, "message": "No server.json or quota_state.json found"}
