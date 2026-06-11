"""Base adapter — abstract interface for all data source adapters."""

from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    """All source adapters inherit from this base."""

    def __init__(self, account_id: str):
        self.account_id = account_id

    @abstractmethod
    async def fetch_quota(self) -> list[dict[str, Any]]:
        """
        Fetch current quota state for this account.
        Returns a list of dicts, each representing one model's quota snapshot.
        """
        ...

    @abstractmethod
    async def fetch_usage(self, since: str | None = None) -> list[dict[str, Any]]:
        """
        Fetch usage records for this account.
        Returns a list of dicts, each representing one usage record.
        """
        ...

    async def test_connection(self) -> dict[str, Any]:
        """
        Test connectivity to the data source.
        Returns {"ok": True/False, "message": "..."}.
        """
        try:
            result = await self.fetch_quota()
            return {"ok": True, "message": f"Connected — {len(result)} model(s) found"}
        except Exception as e:
            return {"ok": False, "message": str(e)}
