"""Account model — represents a tool + Gmail binding."""

from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    # e.g. "gmail1_antigravity", "gmail2_openrouter", "cursor", "copilot"

    label: Mapped[str] = mapped_column(String(128))
    # e.g. "Gmail 1 — Antigravity"

    email: Mapped[str | None] = mapped_column(String(256), nullable=True)
    gmail_slot: Mapped[str | None] = mapped_column(String(16), nullable=True)
    # "gmail1" | "gmail2" | null (for Cursor / Copilot)

    source: Mapped[str] = mapped_column(String(32))
    # "antigravity" | "openrouter" | "gemini" | "cursor" | "copilot"

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "email": self.email,
            "gmail_slot": self.gmail_slot,
            "source": self.source,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
