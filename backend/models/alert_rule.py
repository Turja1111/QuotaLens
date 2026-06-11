"""AlertRule model — configurable threshold alerts."""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from models.base import Base


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    label: Mapped[str] = mapped_column(String(128))

    account_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # null = applies to all accounts

    source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # null = all sources

    model_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # null = all models

    threshold_pct: Mapped[float] = mapped_column(Float)
    # 0.75 = fire when 75% of quota used

    channel: Mapped[str] = mapped_column(String(16))
    # "desktop" | "webhook" | "email"

    webhook_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=60)
    last_fired_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "label": self.label,
            "account_id": self.account_id,
            "source": self.source,
            "model_id": self.model_id,
            "threshold_pct": self.threshold_pct,
            "channel": self.channel,
            "webhook_url": self.webhook_url,
            "cooldown_minutes": self.cooldown_minutes,
            "last_fired_at": self.last_fired_at.isoformat() if self.last_fired_at else None,
            "is_active": self.is_active,
        }
