"""GeminiQuotaConfig model — editable free tier limits per model."""

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from models.base import Base


class GeminiQuotaConfig(Base):
    __tablename__ = "gemini_quota_config"

    model_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    # e.g. "gemini-3.5-flash", "gemini-2.5-pro"

    model_label: Mapped[str] = mapped_column(String(128))
    # Human-readable: "Gemini 3.5 Flash"

    rpm: Mapped[int] = mapped_column(Integer)
    # Requests per minute

    tpm: Mapped[int] = mapped_column(Integer)
    # Tokens per minute

    rpd: Mapped[int] = mapped_column(Integer)
    # Requests per day

    def to_dict(self) -> dict:
        return {
            "model_id": self.model_id,
            "model_label": self.model_label,
            "rpm": self.rpm,
            "tpm": self.tpm,
            "rpd": self.rpd,
        }
