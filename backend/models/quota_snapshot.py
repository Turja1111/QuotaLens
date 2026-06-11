"""QuotaSnapshot model — point-in-time quota readings."""

import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Integer, Float, Boolean, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from models.base import Base


class QuotaSnapshot(Base):
    __tablename__ = "quota_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_id: Mapped[str] = mapped_column(String(64), index=True)
    source: Mapped[str] = mapped_column(String(32), index=True)
    model_id: Mapped[str] = mapped_column(String(128), index=True)
    model_label: Mapped[str] = mapped_column(String(128))
    snapshot_at: Mapped[datetime] = mapped_column(DateTime, index=True)

    # For quota-bar tools (Antigravity): 0.0 = empty, 1.0 = full
    quota_remaining_pct: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    is_exhausted: Mapped[bool] = mapped_column(Boolean, default=False)

    # For request-count tools (Gemini free, OpenRouter free)
    requests_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    requests_total: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # For credit-based tools (OpenRouter paid, Cursor)
    credits_used: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 6), nullable=True
    )
    credits_total: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 6), nullable=True
    )

    # Refresh timing
    reset_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reset_cadence: Mapped[str] = mapped_column(String(16))
    # "5h" | "daily" | "weekly" | "monthly"

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "account_id": self.account_id,
            "source": self.source,
            "model_id": self.model_id,
            "model_label": self.model_label,
            "snapshot_at": self.snapshot_at.isoformat() if self.snapshot_at else None,
            "quota_remaining_pct": self.quota_remaining_pct,
            "is_exhausted": self.is_exhausted,
            "requests_used": self.requests_used,
            "requests_total": self.requests_total,
            "credits_used": float(self.credits_used) if self.credits_used else None,
            "credits_total": float(self.credits_total) if self.credits_total else None,
            "reset_at": self.reset_at.isoformat() if self.reset_at else None,
            "reset_cadence": self.reset_cadence,
        }
