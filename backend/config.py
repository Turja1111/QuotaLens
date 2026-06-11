"""
QuotaLens — Configuration module.
Reads all settings from environment variables / .env file using pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database & Queue ─────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://quotalens:password@localhost:5432/model_quota"
    database_url_sync: str = "postgresql://quotalens:password@localhost:5432/model_quota"
    redis_url: str = "redis://localhost:6379/0"

    # ── Security ─────────────────────────────────────────────────────────
    secret_key: str = "change-this-to-a-random-64-char-string"
    admin_username: str = "admin"
    admin_password: str = "change-this-password"

    # ── Cursor ───────────────────────────────────────────────────────────
    cursor_api_key: Optional[str] = None

    # ── Antigravity ──────────────────────────────────────────────────────
    antigravity_dir_gmail1: str = "~/.gemini/antigravity"
    antigravity_dir_gmail2: str = "~/.gemini/techgravity"

    # ── GitHub Copilot ───────────────────────────────────────────────────
    github_pat: Optional[str] = None
    github_org: Optional[str] = None

    # ── Gemini API ───────────────────────────────────────────────────────
    gemini_api_key_gmail1: Optional[str] = None
    gemini_api_key_gmail2: Optional[str] = None

    # ── OpenRouter ───────────────────────────────────────────────────────
    openrouter_api_key_gmail1: Optional[str] = None
    openrouter_api_key_gmail2: Optional[str] = None
    openrouter_mgmt_key_gmail1: Optional[str] = None
    openrouter_mgmt_key_gmail2: Optional[str] = None

    # ── Alerts ───────────────────────────────────────────────────────────
    alert_threshold_warn: float = 0.75
    alert_threshold_critical: float = 0.90
    alert_webhook_url: Optional[str] = None

    # ── App ──────────────────────────────────────────────────────────────
    debug: bool = True
    log_level: str = "INFO"


settings = Settings()
