"""
QuotaLens — Seed script.
Populates the database with realistic demo data so the dashboard works
immediately without live API connections.

Usage:
    cd backend
    python seed.py
"""

import uuid
import random
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings
from models import Base, Account, UsageRecord, QuotaSnapshot, AlertRule, GeminiQuotaConfig

engine = create_engine(settings.database_url_sync)
Session = sessionmaker(bind=engine)


def seed():
    Base.metadata.create_all(engine)
    session = Session()

    # Clear existing seed data
    session.query(UsageRecord).delete()
    session.query(QuotaSnapshot).delete()
    session.query(AlertRule).delete()
    session.query(GeminiQuotaConfig).delete()
    session.query(Account).delete()
    session.commit()

    # ── Accounts ─────────────────────────────────────────────────────────
    accounts_data = [
        Account(id="gmail1_antigravity", label="Gmail 1 — Antigravity", email="user1@gmail.com", gmail_slot="gmail1", source="antigravity"),
        Account(id="gmail2_antigravity", label="Gmail 2 — Antigravity", email="user2@gmail.com", gmail_slot="gmail2", source="antigravity"),
        Account(id="gmail1_openrouter", label="Gmail 1 — OpenRouter", email="user1@gmail.com", gmail_slot="gmail1", source="openrouter"),
        Account(id="gmail2_openrouter", label="Gmail 2 — OpenRouter", email="user2@gmail.com", gmail_slot="gmail2", source="openrouter"),
        Account(id="gmail1_gemini", label="Gmail 1 — Gemini API", email="user1@gmail.com", gmail_slot="gmail1", source="gemini"),
        Account(id="gmail2_gemini", label="Gmail 2 — Gemini API", email="user2@gmail.com", gmail_slot="gmail2", source="gemini"),
        Account(id="cursor", label="Cursor Pro", email="user@cursor.sh", gmail_slot=None, source="cursor"),
        Account(id="copilot", label="GitHub Copilot", email="user@github.com", gmail_slot=None, source="copilot"),
    ]
    session.add_all(accounts_data)

    # ── Gemini Quota Config ──────────────────────────────────────────────
    gemini_configs = [
        GeminiQuotaConfig(model_id="gemini-3.5-flash", model_label="Gemini 3.5 Flash", rpm=10, tpm=250000, rpd=1500),
        GeminiQuotaConfig(model_id="gemini-3-flash-preview", model_label="Gemini 3 Flash Preview", rpm=10, tpm=250000, rpd=1500),
        GeminiQuotaConfig(model_id="gemini-2.5-flash-preview", model_label="Gemini 2.5 Flash Preview", rpm=15, tpm=1000000, rpd=1500),
        GeminiQuotaConfig(model_id="gemini-3.1-pro-preview", model_label="Gemini 3.1 Pro Preview", rpm=2, tpm=32000, rpd=50),
        GeminiQuotaConfig(model_id="gemini-3-pro-preview", model_label="Gemini 3 Pro Preview", rpm=2, tpm=32000, rpd=50),
        GeminiQuotaConfig(model_id="gemini-2.5-pro", model_label="Gemini 2.5 Pro", rpm=5, tpm=250000, rpd=50),
    ]
    session.add_all(gemini_configs)

    # ── Antigravity Quota Snapshots (current) ────────────────────────────
    now = datetime.utcnow()
    ag_models = [
        ("gemini-3.5-flash-high", "Gemini 3.5 Flash (High)", 0.62),
        ("gemini-3.5-flash-low", "Gemini 3.5 Flash (Low)", 0.58),
        ("gemini-3.5-flash-medium", "Gemini 3.5 Flash (Medium)", 0.50),
        ("gemini-3.1-pro-high", "Gemini 3.1 Pro (High)", 0.48),
        ("gemini-3.1-pro-low", "Gemini 3.1 Pro (Low)", 0.40),
        ("claude-sonnet-4-6-thinking", "Claude Sonnet 4.6 (Thinking)", 0.22),
        ("claude-opus-4-6-thinking", "Claude Opus 4.6 (Thinking)", 0.14),
        ("gpt-oss-120b-medium", "GPT-OSS 120B (Medium)", 0.31),
    ]

    for slot, acct_id in [("gmail1", "gmail1_antigravity"), ("gmail2", "gmail2_antigravity")]:
        reset_5h = now + timedelta(hours=random.uniform(0.5, 4.5))
        for model_id, label, base_pct in ag_models:
            pct = max(0.0, min(1.0, base_pct + random.uniform(-0.15, 0.15)))
            if slot == "gmail2":
                pct = max(0.0, min(1.0, pct + random.uniform(-0.2, 0.1)))

            session.add(QuotaSnapshot(
                id=uuid.uuid4(), account_id=acct_id, source="antigravity",
                model_id=model_id, model_label=label, snapshot_at=now,
                quota_remaining_pct=round(pct, 3), is_exhausted=pct < 0.02,
                reset_at=reset_5h, reset_cadence="5h",
            ))

        # Prompt & flow credits
        session.add(QuotaSnapshot(
            id=uuid.uuid4(), account_id=acct_id, source="antigravity",
            model_id="prompt-credits", model_label="Prompt Credits", snapshot_at=now,
            quota_remaining_pct=0.73, credits_used=Decimal("666"), credits_total=Decimal("2500"),
            reset_cadence="monthly",
        ))
        session.add(QuotaSnapshot(
            id=uuid.uuid4(), account_id=acct_id, source="antigravity",
            model_id="flow-credits", model_label="Flow Credits", snapshot_at=now,
            quota_remaining_pct=0.82, credits_used=Decimal("88"), credits_total=Decimal("500"),
            reset_cadence="monthly",
        ))

    # ── OpenRouter Quota Snapshots ───────────────────────────────────────
    for slot, acct_id in [("gmail1", "gmail1_openrouter"), ("gmail2", "gmail2_openrouter")]:
        used = random.randint(120, 600)
        session.add(QuotaSnapshot(
            id=uuid.uuid4(), account_id=acct_id, source="openrouter",
            model_id="openrouter-daily", model_label="Daily Free Requests",
            snapshot_at=now, quota_remaining_pct=round(1.0 - used / 1000, 3),
            is_exhausted=used >= 1000, requests_used=used, requests_total=1000,
            reset_cadence="daily",
        ))
        session.add(QuotaSnapshot(
            id=uuid.uuid4(), account_id=acct_id, source="openrouter",
            model_id="openrouter-credits", model_label="Credits",
            snapshot_at=now, credits_used=Decimal(str(round(random.uniform(0.5, 4.0), 2))),
            credits_total=Decimal("10.00"), reset_cadence="monthly",
        ))

    # ── Gemini API Snapshots ─────────────────────────────────────────────
    gemini_models = [
        ("gemini-3.5-flash", "Gemini 3.5 Flash", 1500),
        ("gemini-2.5-flash-preview", "Gemini 2.5 Flash Preview", 1500),
        ("gemini-3.1-pro-preview", "Gemini 3.1 Pro Preview", 50),
        ("gemini-2.5-pro", "Gemini 2.5 Pro", 50),
    ]
    from adapters.gemini_adapter import GeminiAdapter
    reset_at = GeminiAdapter.get_reset_time()

    for slot, acct_id in [("gmail1", "gmail1_gemini"), ("gmail2", "gmail2_gemini")]:
        for model_id, label, rpd in gemini_models:
            used = random.randint(0, int(rpd * 0.7))
            session.add(QuotaSnapshot(
                id=uuid.uuid4(), account_id=acct_id, source="gemini",
                model_id=model_id, model_label=label, snapshot_at=now,
                quota_remaining_pct=round(1.0 - used / rpd, 3),
                requests_used=used, requests_total=rpd,
                reset_at=reset_at, reset_cadence="daily",
            ))

    # ── Cursor Snapshot ──────────────────────────────────────────────────
    session.add(QuotaSnapshot(
        id=uuid.uuid4(), account_id="cursor", source="cursor",
        model_id="cursor-plan", model_label="Cursor Pro",
        snapshot_at=now, reset_cadence="monthly",
        reset_at=now.replace(day=1) + timedelta(days=32),
    ))

    # ── Copilot Snapshot ─────────────────────────────────────────────────
    session.add(QuotaSnapshot(
        id=uuid.uuid4(), account_id="copilot", source="copilot",
        model_id="copilot-plan", model_label="GitHub Copilot",
        snapshot_at=now, reset_cadence="monthly",
    ))

    # ── Usage Records (30 days of history) ───────────────────────────────
    sources_models = [
        ("antigravity", "gmail1_antigravity", [
            ("gemini-3.5-flash-high", "Gemini 3.5 Flash (High)"),
            ("claude-sonnet-4-6-thinking", "Claude Sonnet 4.6 (Thinking)"),
            ("gemini-3.1-pro-high", "Gemini 3.1 Pro (High)"),
        ]),
        ("antigravity", "gmail2_antigravity", [
            ("gemini-3.5-flash-high", "Gemini 3.5 Flash (High)"),
            ("claude-opus-4-6-thinking", "Claude Opus 4.6 (Thinking)"),
        ]),
        ("openrouter", "gmail1_openrouter", [
            ("anthropic/claude-haiku-4.5:free", "Claude Haiku 4.5"),
            ("amazon/nova-micro-v1:free", "Amazon Nova Micro"),
        ]),
        ("openrouter", "gmail2_openrouter", [
            ("anthropic/claude-fable-5:free", "Claude Fable 5"),
        ]),
        ("cursor", "cursor", [
            ("gpt-4o", "GPT-4o"),
            ("claude-3.5-sonnet", "Claude 3.5 Sonnet"),
        ]),
        ("copilot", "copilot", [
            ("claude-haiku-4.5", "Claude Haiku 4.5"),
            ("gpt-5-mini", "GPT-5 mini"),
            ("mai-code-1-flash", "MAI-Code-1-Flash"),
        ]),
        ("gemini", "gmail1_gemini", [
            ("gemini-3.5-flash", "Gemini 3.5 Flash"),
            ("gemini-2.5-pro", "Gemini 2.5 Pro"),
        ]),
    ]

    for day_offset in range(30):
        day = now - timedelta(days=day_offset)
        day = day.replace(hour=12, minute=0, second=0, microsecond=0)

        for source, acct_id, models in sources_models:
            for model_id, model_label in models:
                # Skip some days randomly for variety
                if random.random() < 0.15:
                    continue

                input_t = random.randint(500, 50000)
                output_t = random.randint(200, 20000)
                cache_t = random.randint(0, input_t // 2)
                req_count = random.randint(1, 20)
                cost = None
                if source in ("cursor", "openrouter"):
                    cost = Decimal(str(round(random.uniform(0.001, 0.5), 6)))

                session.add(UsageRecord(
                    id=uuid.uuid4(), account_id=acct_id, source=source,
                    timestamp=day + timedelta(hours=random.randint(0, 12)),
                    model_id=model_id, model_label=model_label,
                    input_tokens=input_t, output_tokens=output_t,
                    cache_tokens=cache_t, request_count=req_count,
                    cost_usd=cost,
                    request_type=random.choice(["agent", "chat", "completion"]),
                ))

    # ── Alert Rules ──────────────────────────────────────────────────────
    alerts = [
        AlertRule(id=uuid.uuid4(), label="Antigravity 75% Warning", source="antigravity", threshold_pct=0.75, channel="desktop", cooldown_minutes=60),
        AlertRule(id=uuid.uuid4(), label="Antigravity 90% Critical", source="antigravity", threshold_pct=0.90, channel="desktop", cooldown_minutes=30),
        AlertRule(id=uuid.uuid4(), label="OpenRouter Daily Limit", source="openrouter", threshold_pct=0.90, channel="desktop", cooldown_minutes=120),
        AlertRule(id=uuid.uuid4(), label="Gemini Pro Quota", source="gemini", model_id="gemini-2.5-pro", threshold_pct=0.80, channel="desktop", cooldown_minutes=60),
    ]
    session.add_all(alerts)

    session.commit()
    session.close()

    print("[OK] QuotaLens database seeded with demo data!")
    print("   - 8 accounts")
    print("   - 6 Gemini quota configs")
    print(f"   - ~{30 * len(sources_models) * 2} usage records (30 days)")
    print("   - Quota snapshots for all sources")
    print("   - 4 alert rules")


if __name__ == "__main__":
    seed()
