"""UsageRecord model — per-request or per-period token usage data."""

import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, BigInteger, Integer, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from models.base import Base


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_id: Mapped[str] = mapped_column(String(64), index=True)
    source: Mapped[str] = mapped_column(String(32), index=True)
    # "cursor" | "antigravity" | "openrouter" | "gemini" | "copilot"

    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)
    model_id: Mapped[str] = mapped_column(String(128), index=True)
    # e.g. "gemini-3.5-flash-high", "claude-sonnet-4-6-thinking"

    model_label: Mapped[str] = mapped_column(String(128))
    # Human-readable: "Gemini 3.5 Flash (High)"

    input_tokens: Mapped[int] = mapped_column(BigInteger, default=0)
    output_tokens: Mapped[int] = mapped_column(BigInteger, default=0)
    cache_tokens: Mapped[int] = mapped_column(BigInteger, default=0)
    request_count: Mapped[int] = mapped_column(Integer, default=1)
    cost_usd: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 8), nullable=True
    )
    request_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # "agent" | "chat" | "autocomplete" | "completion"

    external_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    # OpenRouter generation ID, Cursor request ID — for deduplication

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "account_id": self.account_id,
            "source": self.source,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "model_id": self.model_id,
            "model_label": self.model_label,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_tokens": self.cache_tokens,
            "request_count": self.request_count,
            "cost_usd": float(self.cost_usd) if self.cost_usd else None,
            "request_type": self.request_type,
            "external_id": self.external_id,
        }
