# QuotaLens
## AI Model Quota & Token Usage Dashboard

**Project Documentation — Version 1.0 | June 2026**

> **Stack:** FastAPI · SQLAlchemy 2.0 · sqladmin · Celery · Redis · PostgreSQL 16 · React + Vite
>
> **Database:** Model Quota (PostgreSQL 16)
>
> **Covers:** Cursor · Antigravity (Gmail 1 + Gmail 2) · VS Code Copilot · VS Code Gemini API (Gmail 1 + Gmail 2) · VS Code OpenRouter (Gmail 1 + Gmail 2)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Covered Tools & Data Sources](#2-covered-tools--data-sources)
3. [Feasibility Assessment per Source](#3-feasibility-assessment-per-source)
4. [Dual Gmail Account Architecture](#4-dual-gmail-account-architecture)
5. [Technology Stack](#5-technology-stack)
6. [Data Models](#6-data-models)
7. [API Integration Details](#7-api-integration-details)
8. [Backend Module Design](#8-backend-module-design)
9. [Admin Panel — sqladmin](#9-admin-panel--sqladmin)
10. [Frontend Feature Specification](#10-frontend-feature-specification)
11. [Project File Structure](#11-project-file-structure)
12. [Setup & Configuration Guide](#12-setup--configuration-guide)
13. [Known Limitations & Caveats](#13-known-limitations--caveats)
14. [Roadmap](#14-roadmap)
15. [Security Considerations](#15-security-considerations)

---

## 1. Project Overview

**QuotaLens** is a self-hosted Python web dashboard that tracks token usage, quota consumption, per-model breakdowns, and quota refresh timers across all AI coding tools you use — spanning two Gmail accounts — in a single unified interface.

| Property | Value |
|---|---|
| **Project Name** | QuotaLens |
| **Database** | Model Quota (PostgreSQL 16) |
| **Primary Language** | Python 3.11+ |
| **Frontend** | React 19 + Vite |
| **Admin Panel** | sqladmin at `/admin` |
| **Deployment** | Self-hosted — Docker Compose (PostgreSQL + Redis) + local Python processes |
| **Version** | 1.0 (June 2026) |

### Key Features

- **Unified dashboard** — all tools, all accounts, all models on one screen
- **Per-model quota gauges** — mirrors Antigravity's built-in quota panel, extended cross-tool
- **Live refresh countdowns** — WebSocket-powered timers per model (5-hour, daily, weekly, monthly)
- **Token usage history** — charts of input / output / cache tokens per day, per model
- **Credit & cost tracking** — credits remaining for OpenRouter, USD cost for Cursor and Copilot
- **Dual-account separation** — Gmail 1 and Gmail 2 data tracked and displayed independently
- **Alert system** — desktop / webhook notifications when any quota hits 75% or 90%
- **Admin panel** — sqladmin UI at `/admin` to inspect and manage all database records

---

## 2. Covered Tools & Data Sources

QuotaLens integrates with five AI coding tools across two Gmail accounts.

| Tool | Account Binding | Primary Data Source | Quota Cadence |
|---|---|---|---|
| **Cursor** | Email / password (not Gmail-bound) | Cursor Admin REST API + CSV export | Monthly |
| **Antigravity** | Gmail Account 1 + Gmail Account 2 | Local Language Server (gRPC-Web) + `~/.gemini/` files | Every 5 hours |
| **VS Code — Copilot** | GitHub account (single) | GitHub Copilot REST API | Monthly |
| **VS Code — Gemini API** | Gmail Account 1 + Gmail Account 2 | Local request counter + response headers | Daily (midnight PT) |
| **VS Code — OpenRouter** | Gmail Account 1 + Gmail Account 2 | OpenRouter REST API | Daily (midnight UTC) |

### 2.1 Cursor

- Tracks coding agent sessions — chat, agent, autocomplete
- Teams / Enterprise: full REST API at `api.cursor.com` with token + cost breakdown
- Individual Pro: CSV export from `cursor.com/dashboard` (uploaded manually; treated as static history)
- Billing cycle resets monthly; reset date returned by `GET /v1/me` as `billing_cycle_end`

### 2.2 Antigravity (Google — VS Code fork)

- Agent-first IDE powered by Gemini 3.5 Flash; quota pools are per-model **and** per tier (High / Low / Medium)
- **Models tracked:** Gemini 3.5 Flash (High/Low/Medium), Gemini 3.1 Pro (High/Low), Claude Sonnet 4.6 Thinking, Claude Opus 4.6 Thinking, GPT-OSS 120B (Medium)
- Quota refreshes **every 5 hours** since Antigravity 2.0
- Two Gmail accounts = two independent quota pools in separate local directories
- Live data via gRPC-Web to the local Language Server; automatic fallback to `~/.gemini/*/quota_state.json` when the IDE is not running

### 2.3 VS Code — GitHub Copilot

- Models: Claude Haiku 4.5, GPT-5 mini, MAI-Code-1-Flash, Raptor mini, and others
- Credit-based pricing — In / Out / Cache credits per 1M tokens
- GitHub REST API provides aggregate and per-model usage; per-token detailed breakdown rolling out June 2026

### 2.4 VS Code — Gemini API (Free tier)

- Models: Gemini 2.5 Flash Preview, 2.5 Pro, 3 Flash Preview, 3 Pro Preview, 3.1 Pro Preview, 3.5 Flash
- No official remaining-quota endpoint; QuotaLens maintains a **local per-API-key, per-model, per-day counter** in the Model Quota PostgreSQL database
- Quota limits stored in the `gemini_quota_config` table — editable via sqladmin at any time
- Two Gmail accounts = two API keys = two independent daily quotas

### 2.5 VS Code — OpenRouter (Free models)

- Free models with `:free` suffix — Amazon Nova series, Anthropic Claude 3/3.5 Haiku, Claude Fable 5, Claude Haiku 4.5, Claude Opus 4, AI21 Jamba Large 1.7, and many others
- Rate limited: 20 requests/minute; 50 req/day (< $10 credits) or 1,000 req/day (≥ $10 credits)
- Two Gmail accounts = two separate OpenRouter accounts and API key pairs

---

## 3. Feasibility Assessment per Source

### 3.1 Cursor

| Capability | Status | Notes |
|---|---|---|
| Token breakdown by model (input / output / cache) | ✅ Full | Admin API — Teams / Enterprise |
| Cost in USD per model | ✅ Full | Per request and per model |
| Quota remaining + reset date | ✅ Full | `GET /v1/me` → `billing_cycle_end` |
| Real-time polling | ✅ Full | 15-min cache; ETag supported |
| Individual Pro (no team) | ⚠️ Partial | CSV export only — no personal API key |

### 3.2 Antigravity

| Capability | Status | Notes |
|---|---|---|
| Per-model quota bars (High / Low / Medium pools) | ✅ Full | Local Language Server gRPC-Web |
| Quota refresh countdown per model | ✅ Full | `resetTime` / `timeUntilReset` in gRPC response |
| Credit balance (prompt + flow credits) | ✅ Full | `availablePromptCredits`, `availableFlowCredits` |
| Multi-account support (2 Gmail accounts) | ✅ Full | Separate dirs: `~/.gemini/antigravity/` and `~/.gemini/techgravity/` |
| IDE not running fallback | ✅ Partial | Parse `~/.gemini/*/quota_state.json` directly |

### 3.3 GitHub Copilot

| Capability | Status | Notes |
|---|---|---|
| Daily usage summary with per-model breakdown | ✅ Yes | `GET /orgs/{org}/copilot/usage` |
| Individual user usage | ✅ Preview | `GET /user/copilot/usage` — preview endpoint |
| Token-level billing breakdown | ✅ Rolling out | Copilot token-based billing rolling out June 2026 |
| Quota / credit reset date | ✅ Yes | Monthly billing cycle |

### 3.4 Gemini API (Free tier)

| Capability | Status | Notes |
|---|---|---|
| Remaining quota endpoint | ❌ None | Google provides no remaining-quota API |
| Rate-limit headers in responses | ✅ Yes | `x-ratelimit-remaining-requests`, `x-ratelimit-reset-requests` |
| Daily request tracking | ✅ Yes (local) | App maintains counter in PostgreSQL per key / model / day |
| Quota reset time | ✅ Yes | Midnight Pacific Time — computed locally |

### 3.5 OpenRouter (Free models)

| Capability | Status | Notes |
|---|---|---|
| Credits remaining | ✅ Full | `GET /api/v1/credits` (Management key required) |
| Rate limit + daily requests remaining | ✅ Full | `GET /api/v1/key` |
| Per-request token counts and cost | ✅ Full | `GET /api/v1/generation?id={id}` |
| Full activity history | ✅ Full | `GET /api/v1/generations?limit=N` |
| Per-account separation | ✅ Full | Two separate API key pairs |

---

## 4. Dual Gmail Account Architecture

Two Gmail accounts are a first-class concept throughout QuotaLens. Every data record carries an `account_id` tag so data can be separated, compared, or aggregated at any level.

```
Account A  (label: "Gmail 1")
├── Antigravity     →  ~/.gemini/antigravity/       (primary slot)
├── Gemini API      →  GEMINI_API_KEY_GMAIL1         (Google AI Studio key)
└── OpenRouter      →  OPENROUTER_API_KEY_GMAIL1

Account B  (label: "Gmail 2")
├── Antigravity     →  ~/.gemini/techgravity/        (secondary slot)
├── Gemini API      →  GEMINI_API_KEY_GMAIL2
└── OpenRouter      →  OPENROUTER_API_KEY_GMAIL2

Cursor              →  CURSOR_API_KEY   (single account, email/password)
GitHub Copilot      →  GITHUB_PAT       (single GitHub account)
```

### Dashboard Account Controls

- Top-level **account tab bar:** `[ All Accounts ]  [ Gmail 1 ]  [ Gmail 2 ]`
- Antigravity shows two **side-by-side quota panels** (one per Gmail)
- OpenRouter shows two credit pools, labeled by Gmail account
- Gemini API shows two daily request counters, labeled by Gmail account
- All history charts are filterable by `account_id`
- Alerts can be configured per account or globally

---

## 5. Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **API Framework** | FastAPI | 0.115+ | Async REST API + WebSocket endpoints |
| **Admin UI** | sqladmin | 0.19+ | Django-like admin panel at `/admin` |
| **ORM** | SQLAlchemy | 2.0+ | Async ORM with type annotations |
| **DB Driver** | asyncpg | 0.29+ | Async PostgreSQL driver |
| **Migrations** | Alembic | 1.13+ | Database schema versioning |
| **Task Queue** | Celery | 5.4+ | Periodic polling tasks |
| **Message Broker** | Redis | 7+ | Celery broker + result backend |
| **HTTP Client** | httpx | 0.27+ | Async HTTP calls to all external APIs |
| **gRPC** | grpcio + grpcio-tools | 1.64+ | Antigravity Language Server communication |
| **Settings** | pydantic-settings | 2.0+ | Typed env-var configuration |
| **Auth (admin)** | python-jose + passlib | — | JWT session for admin panel login |
| **Credentials** | python-keyring | 25+ | OS keychain storage for API keys |
| **Notifications** | plyer | 2.1+ | Desktop push notifications |
| **Database** | PostgreSQL | 16+ | Primary data store — database: **Model Quota** |
| **Containers** | Docker + Compose | — | PostgreSQL 16 + Redis 7 infrastructure |
| **Frontend** | React + Vite | React 19 | SPA dashboard |
| **Charts** | Recharts | 2.12+ | Token / quota visualizations |

> **Why FastAPI + sqladmin instead of Django?**
> QuotaLens polls 5+ external APIs concurrently, runs WebSocket countdown streams, and communicates with Antigravity over gRPC — all requiring true async I/O. FastAPI with asyncpg and httpx handles all of this natively in a single event loop. sqladmin provides the full Django admin panel experience (editable tables, filters, CSV export) while mounting directly onto the FastAPI app. Django's ORM has limited async support and would have added unnecessary framework overhead for a data-aggregation dashboard of this type.

---

## 6. Data Models

All tables live in the **Model Quota** PostgreSQL 16 database. Migrations are managed by Alembic.

### 6.1 `accounts`

```python
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
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

### 6.2 `usage_records`

```python
class UsageRecord(Base):
    __tablename__ = "usage_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
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
    cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(10, 8), nullable=True)
    request_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # "agent" | "chat" | "autocomplete" | "completion"

    external_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    # OpenRouter generation ID, Cursor request ID — for deduplication
```

### 6.3 `quota_snapshots`

Point-in-time quota readings written on every poll cycle. One row per account + model + timestamp.

```python
class QuotaSnapshot(Base):
    __tablename__ = "quota_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    account_id: Mapped[str] = mapped_column(String(64), index=True)
    source: Mapped[str] = mapped_column(String(32), index=True)
    model_id: Mapped[str] = mapped_column(String(128), index=True)
    model_label: Mapped[str] = mapped_column(String(128))
    snapshot_at: Mapped[datetime] = mapped_column(DateTime, index=True)

    # For quota-bar tools (Antigravity): 0.0 = empty, 1.0 = full
    quota_remaining_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_exhausted: Mapped[bool] = mapped_column(Boolean, default=False)

    # For request-count tools (Gemini free, OpenRouter free)
    requests_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    requests_total: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # For credit-based tools (OpenRouter paid, Cursor)
    credits_used: Mapped[Decimal | None] = mapped_column(Numeric(14, 6), nullable=True)
    credits_total: Mapped[Decimal | None] = mapped_column(Numeric(14, 6), nullable=True)

    # Refresh timing
    reset_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reset_cadence: Mapped[str] = mapped_column(String(16))
    # "5h" | "daily" | "weekly" | "monthly"
```

### 6.4 `alert_rules`

```python
class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
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
    cooldown_minutes: Mapped[int] = mapped_column(default=60)
    last_fired_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

### 6.5 `gemini_quota_config`

Stores per-model free tier limits for the Gemini API. Editable via sqladmin or the Settings page without code changes.

| Model | RPM | TPM | RPD |
|---|---|---|---|
| `gemini-3.5-flash` | 10 | 250,000 | 1,500 |
| `gemini-3-flash-preview` | 10 | 250,000 | 1,500 |
| `gemini-2.5-flash-preview` | 15 | 1,000,000 | 1,500 |
| `gemini-3.1-pro-preview` | 2 | 32,000 | 50 |
| `gemini-3-pro-preview` | 2 | 32,000 | 50 |
| `gemini-2.5-pro` | 5 | 250,000 | 50 |

---

## 7. API Integration Details

### 7.1 Cursor

```
Base URL:   https://api.cursor.com
Auth:       Authorization: Bearer <CURSOR_API_KEY>
            OR  HTTP Basic — username=<CURSOR_API_KEY>, password=(empty)
```

| Endpoint | Purpose |
|---|---|
| `GET /v1/me` | Account info, plan type, `billing_cycle_end` |
| `GET /analytics/team/usage` | Token + cost breakdown by model |
| `GET /analytics/team/usage?start=DATE&end=DATE` | Historical date range |
| `GET /teams/members` | Member list (Teams plan only) |

- **Polling interval:** Every 15 minutes. Use `ETag` / `If-None-Match` to skip unchanged responses.
- **Individual Pro fallback:** Upload CSV from `cursor.com/dashboard → Usage → Export CSV` via `POST /api/v1/cursor/import`.

---

### 7.2 Antigravity — Local Language Server

```
Protocol:   gRPC-Web (HTTP/1.1)
Host:       localhost
Port:       Read from ~/.gemini/antigravity/server.json  (Account 1)
                    ~/.gemini/techgravity/server.json   (Account 2)
Service:    exa.language_server_pb.LanguageServerService
RPC:        GetUserStatus(GetUserStatusRequest) → UserStatusResponse
Polling:    Every 5 minutes
Fallback:   Parse ~/.gemini/*/quota_state.json when IDE is not running
```

**Response fields used:**

```json
{
  "modelQuotas": [
    {
      "modelId": "gemini-3.5-flash-high",
      "label": "Gemini 3.5 Flash (High)",
      "remainingPercentage": 0.62,
      "isExhausted": false,
      "resetTime": "2026-06-11T08:00:00Z",
      "timeUntilReset": "1h 47m"
    }
  ],
  "planName": "Google AI Pro",
  "monthlyPromptCredits": 2500,
  "availablePromptCredits": 1834,
  "monthlyFlowCredits": 500,
  "availableFlowCredits": 412
}
```

**Python adapter:**

```python
# adapters/antigravity_adapter.py
async def fetch_antigravity_quota(account_dir: str) -> list[dict]:
    server_file = Path(account_dir).expanduser() / "server.json"

    # Try live gRPC first
    if server_file.exists():
        try:
            port = json.loads(server_file.read_text())["port"]
            async with grpc.aio.insecure_channel(f"localhost:{port}") as channel:
                stub = LanguageServerServiceStub(channel)
                response = await stub.GetUserStatus(
                    GetUserStatusRequest(), timeout=3.0
                )
                return parse_grpc_response(response)
        except Exception:
            pass  # fall through to file fallback

    # File fallback
    quota_file = Path(account_dir).expanduser() / "quota_state.json"
    if quota_file.exists():
        return parse_quota_state_file(quota_file.read_text())

    return []
```

---

### 7.3 VS Code — GitHub Copilot

```
Base URL:   https://api.github.com
Auth:       Authorization: Bearer <GITHUB_PAT>
Header:     X-GitHub-Api-Version: 2026-03-10
Scopes:     manage_billing:copilot  OR  read:org
```

| Endpoint | Purpose |
|---|---|
| `GET /orgs/{org}/copilot/usage` | Daily usage with per-model breakdown |
| `GET /orgs/{org}/copilot/usage?since=DATE&until=DATE` | Historical range |
| `GET /user/copilot/usage` | Individual user usage (preview endpoint) |
| `GET /orgs/{org}/copilot/billing` | Seat counts and plan info |

- **Polling interval:** Daily at 02:00 UTC — GitHub usage data updates once per UTC day.
- **Credit cost mapping:** Per-model In/Out/Cache costs are read from the VS Code bundled model registry at `~/.vscode/extensions/github.copilot-*/dist/extension.js` and cached in the database.

---

### 7.4 VS Code — Gemini API (Free tier)

No "remaining quota" endpoint from Google. QuotaLens uses a **local counter strategy:**

- Maintains a per-API-key, per-model, per-day integer counter in the Model Quota PostgreSQL database
- Quota limits stored in `gemini_quota_config` — editable via sqladmin without code changes
- **Remaining = limit − counter;** resets daily at midnight Pacific Time (`America/Los_Angeles`)
- **Bonus:** Parse `x-ratelimit-remaining-requests` and `x-ratelimit-reset-requests` response headers for more accurate real-time counts

**Quota reset computation:**
```python
reset_at = today_midnight_pacific + timedelta(days=1)
```

---

### 7.5 VS Code — OpenRouter (Free models)

```
Base URL:   https://openrouter.ai/api/v1
Auth:       Authorization: Bearer <OPENROUTER_API_KEY>
```

| Endpoint | Purpose |
|---|---|
| `GET /api/v1/key` | Rate limit status and daily remaining requests |
| `GET /api/v1/credits` | Credits purchased and used (Management key required) |
| `GET /api/v1/generation?id={id}` | Per-request token count and cost |
| `GET /api/v1/generations?offset=0&limit=200` | Full activity log |

**Free model daily limits:**
- 20 requests/minute (hard rate limit)
- 50 requests/day — if account has less than $10 in credits
- 1,000 requests/day — if account has $10 or more in credits
- Reset cadence: daily (empirically resets around midnight UTC)

**Python adapter:**

```python
# adapters/openrouter_adapter.py
class OpenRouterAdapter:
    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, account_id: str, api_key: str, mgmt_key: str | None = None):
        self.account_id = account_id
        self.api_key = api_key
        self.mgmt_key = mgmt_key
        self.headers = {"Authorization": f"Bearer {api_key}"}

    async def fetch_quota(self) -> dict:
        async with httpx.AsyncClient() as client:
            key_resp = await client.get(f"{self.BASE_URL}/key", headers=self.headers)
            result = {"key_status": key_resp.json()}

            if self.mgmt_key:
                credit_resp = await client.get(
                    f"{self.BASE_URL}/credits",
                    headers={"Authorization": f"Bearer {self.mgmt_key}"}
                )
                result["credits"] = credit_resp.json()

            return result

    async def fetch_activity(self, limit: int = 200) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.BASE_URL}/generations",
                params={"limit": limit},
                headers=self.headers
            )
            return resp.json().get("data", [])
```

---

## 8. Backend Module Design

### 8.1 FastAPI App Entry Point

```python
# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import engine, Base
from sqladmin import Admin
from admin_views import AccountAdmin, UsageRecordAdmin, QuotaSnapshotAdmin, AlertRuleAdmin
from api import dashboard, quota, usage, accounts, alerts
from websocket.quota_stream import router as ws_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="QuotaLens", lifespan=lifespan)

# REST API routers
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(quota.router,     prefix="/api/v1")
app.include_router(usage.router,     prefix="/api/v1")
app.include_router(accounts.router,  prefix="/api/v1")
app.include_router(alerts.router,    prefix="/api/v1")
app.include_router(ws_router)

# sqladmin — admin panel at /admin
admin = Admin(app, engine)
admin.add_view(AccountAdmin)
admin.add_view(UsageRecordAdmin)
admin.add_view(QuotaSnapshotAdmin)
admin.add_view(AlertRuleAdmin)
```

### 8.2 REST API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/dashboard` | Summary cards — all tools, all accounts |
| `GET` | `/api/v1/quota` | All current quota snapshots |
| `GET` | `/api/v1/quota/{source}/{account_id}` | Quota for one source + account |
| `GET` | `/api/v1/usage` | Historical usage (filters: source, account, model, date range) |
| `GET` | `/api/v1/usage/summary` | Aggregated totals per model / day |
| `GET` | `/api/v1/accounts` | List configured accounts |
| `POST` | `/api/v1/accounts` | Add account + credentials |
| `PUT` | `/api/v1/accounts/{id}` | Update credentials |
| `POST` | `/api/v1/accounts/{id}/test` | Test connectivity for one account |
| `GET` | `/api/v1/alerts` | List alert rules |
| `POST` | `/api/v1/alerts` | Create alert rule |
| `DELETE` | `/api/v1/alerts/{id}` | Remove alert rule |
| `POST` | `/api/v1/cursor/import` | Upload Cursor CSV (Individual Pro) |
| `WS` | `/ws/quota` | Live WebSocket stream — quota updates pushed every 10 seconds |

### 8.3 Celery Task Schedule

```python
# scheduler/tasks.py
app.conf.beat_schedule = {
    "poll-antigravity": {"task": "tasks.poll_antigravity", "schedule": 300},    # every 5 min
    "poll-openrouter":  {"task": "tasks.poll_openrouter",  "schedule": 900},    # every 15 min
    "poll-cursor":      {"task": "tasks.poll_cursor",      "schedule": 900},    # every 15 min
    "poll-gemini":      {"task": "tasks.poll_gemini",      "schedule": 3600},   # every 1 hour
    "poll-copilot":     {"task": "tasks.poll_copilot",     "schedule": crontab(hour=2, minute=0)},  # 02:00 UTC daily
    "check-alerts":     {"task": "tasks.check_alerts",     "schedule": 60},     # every 1 min
}
```

| Task | Interval | Rationale |
|---|---|---|
| `poll_antigravity` | Every 5 minutes | Quota pool refreshes every 5 hours — catch early depletion |
| `poll_openrouter` | Every 15 minutes | API caches data; ETag used to skip unchanged responses |
| `poll_cursor` | Every 15 minutes | API caches data; ETag used to skip unchanged responses |
| `poll_gemini` | Every 1 hour | Local counter only — sync with response header captures |
| `poll_copilot` | Daily at 02:00 UTC | GitHub usage data updates once per UTC day |
| `check_alerts` | Every 1 minute | Fast alert detection; cooldown prevents repeated notifications |

### 8.4 WebSocket Live Countdown

```python
# websocket/quota_stream.py
@router.websocket("/ws/quota")
async def quota_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            async with async_session() as session:
                snapshots = await get_latest_snapshots(session)
            payload = [s.to_dict() for s in snapshots]
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(10)   # push update every 10 seconds
    except Exception:
        await websocket.close()
```

The `/ws/quota` WebSocket pushes all current quota snapshots to every connected frontend client every 10 seconds. The React frontend uses these payloads to drive live countdown timers and animated quota bars without any additional polling.

---

## 9. Admin Panel — sqladmin

sqladmin mounts at `/admin` and is secured with JWT session cookies using credentials set via `ADMIN_USERNAME` / `ADMIN_PASSWORD` environment variables. No separate framework is needed.

```python
# admin_views.py
class AccountAdmin(ModelView, model=Account):
    name = "Account"
    icon = "fa-user"
    column_list = [Account.id, Account.label, Account.email,
                   Account.gmail_slot, Account.source, Account.is_active]
    column_searchable_list = [Account.label, Account.email]
    column_filters = [Account.source, Account.gmail_slot, Account.is_active]

class UsageRecordAdmin(ModelView, model=UsageRecord):
    name = "Usage Record"
    icon = "fa-chart-bar"
    column_list = [UsageRecord.timestamp, UsageRecord.account_id,
                   UsageRecord.source, UsageRecord.model_label,
                   UsageRecord.input_tokens, UsageRecord.output_tokens,
                   UsageRecord.cost_usd]
    column_sortable_list = [UsageRecord.timestamp, UsageRecord.input_tokens]
    column_filters = [UsageRecord.source, UsageRecord.account_id, UsageRecord.model_id]
    can_create = False   # Records created only by adapters
    can_delete = True

class QuotaSnapshotAdmin(ModelView, model=QuotaSnapshot):
    name = "Quota Snapshot"
    icon = "fa-gauge"
    column_list = [QuotaSnapshot.snapshot_at, QuotaSnapshot.account_id,
                   QuotaSnapshot.source, QuotaSnapshot.model_label,
                   QuotaSnapshot.quota_remaining_pct, QuotaSnapshot.reset_at,
                   QuotaSnapshot.is_exhausted]
    column_filters = [QuotaSnapshot.source, QuotaSnapshot.account_id]

class AlertRuleAdmin(ModelView, model=AlertRule):
    name = "Alert Rule"
    icon = "fa-bell"
    column_list = [AlertRule.label, AlertRule.account_id, AlertRule.source,
                   AlertRule.threshold_pct, AlertRule.channel,
                   AlertRule.last_fired_at, AlertRule.is_active]
```

**Admin routes available at `/admin`:**

| Route | Model | Capabilities |
|---|---|---|
| `/admin/account/list` | Account | View, edit, filter by source / gmail_slot / is_active; search by label or email |
| `/admin/usagerecord/list` | UsageRecord | Browse all records; filter by source, account, model; CSV export |
| `/admin/quotasnapshot/list` | QuotaSnapshot | View quota history per model; filter by source / account |
| `/admin/alertrule/list` | AlertRule | Create, edit, delete alert thresholds; toggle active/inactive |
| `/admin/geminiquotaconfig/list` | GeminiQuotaConfig | Edit free-tier RPM / TPM / RPD per model without code changes |

---

## 10. Frontend Feature Specification

### 10.1 Dashboard Overview

- **Account tab bar:** `[ All Accounts ]  [ Gmail 1 ]  [ Gmail 2 ]`
- **Tool summary cards** (one per tool): icon + name, quota fill % with colour coding (green → amber → red), credits / requests remaining, "Refreshes in X h Y m" from latest `QuotaSnapshot`, click to drill-down page
- **Top stats strip:** total tokens today, total estimated cost today, count of exhausted quotas, nearest upcoming reset

### 10.2 Antigravity Quota Panel

Reproduces the Antigravity in-app quota view for **both accounts simultaneously**, with live WebSocket countdowns:

```
┌── Antigravity — Gmail 1 ──────────────────────────────────────────────────┐
│  Gemini 3.5 Flash (High)          ████████░░  62%    Refreshes in 1h 47m  │
│  Gemini 3.5 Flash (Low)           ███████░░░  58%    Refreshes in 1h 47m  │
│  Gemini 3.1 Pro  (High)           █████░░░░░  48%    Refreshes in 1h 47m  │
│  Gemini 3.1 Pro  (Low)            ████░░░░░░  40%    Refreshes in 1h 47m  │
│  Claude Sonnet 4.6 (Thinking)     ██░░░░░░░░  22%    Refreshes in 22m     │
│  Claude Opus 4.6  (Thinking)      █░░░░░░░░░  14%    Refreshes in 22m     │
│  GPT-OSS 120B    (Medium)         ███░░░░░░░  31%    Refreshes in 22m     │
│  Gemini 3.5 Flash (Medium)        █████░░░░░  50%    Refreshes in 1h 47m  │
│  Credits: 1,834 / 2,500 prompt  |  412 / 500 flow                         │
└───────────────────────────────────────────────────────────────────────────┘

┌── Antigravity — Gmail 2 ──────────────────────────────────────────────────┐
│  (same model rows, independent fill levels and reset timers)               │
└───────────────────────────────────────────────────────────────────────────┘
```

Quota bars animate on each WebSocket data push. Countdowns tick in real time.

### 10.3 VS Code Panel (three collapsible sections)

**Copilot Models**
- Table matching the VS Code sidebar columns: name, context size, capabilities, cost (In / Out / Cache per 1M tokens)
- Usage this billing period per model

**Gemini API (Free)**
- Per-model daily counter: `X / 1500 requests today` with colour-coded progress bar
- Countdown to midnight Pacific reset
- Gmail 1 key and Gmail 2 key shown side-by-side

**OpenRouter Free Models**
- Daily free request counter: `X / 1000 today` (or `X / 50` if < $10 credits)
- Credit balance (if Management key is configured)
- Last 10 models used with token counts
- Gmail 1 and Gmail 2 accounts shown side-by-side

### 10.4 Usage History Page

- **Line chart:** Daily token totals over last 30 / 90 days — filterable by tool, account, model
- **Stacked bar chart:** Per-model breakdown within each tool per day
- **Donut chart:** Token share across all tools today
- **Cost chart:** USD spend over time (Cursor + paid OpenRouter)
- **Data table:** Sortable, filterable raw usage records with CSV export

### 10.5 Alerts Page

- List of active alert rules with last-fired timestamps
- Create / edit / delete rules: pick account, source, model, threshold %, channel
- Notification history log with timestamps
- "Test alert" button for each rule

### 10.6 Settings Page

| Tab | Contents |
|---|---|
| **Accounts** | Add / remove / test each account connection; green ✓ or red ✗ connectivity status |
| **Gemini Limits** | Edit free tier RPM / TPM / RPD per model — mirrors `gemini_quota_config` table |
| **Polling** | Adjust polling intervals per source |
| **Notifications** | Configure desktop / webhook / email notification channels |
| **Data** | DB stats, export all data as JSON, purge history older than N days |
| **Admin Link** | Direct link to `/admin` (sqladmin panel) |

---

## 11. Project File Structure

```
quotalens/
│
├── backend/
│   ├── main.py                         # FastAPI app + sqladmin setup
│   ├── config.py                       # pydantic-settings config from .env
│   ├── database.py                     # SQLAlchemy async engine + session
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── account.py
│   │   ├── usage_record.py
│   │   ├── quota_snapshot.py
│   │   ├── alert_rule.py
│   │   └── gemini_quota_config.py      # Editable free tier limits table
│   │
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py                     # Abstract BaseAdapter
│   │   ├── cursor_adapter.py           # Cursor REST API + CSV parser
│   │   ├── antigravity_adapter.py      # gRPC-Web + ~/.gemini/ file reader
│   │   ├── openrouter_adapter.py       # OpenRouter REST API (2 accounts)
│   │   ├── gemini_adapter.py           # Local counter + header parser
│   │   └── copilot_adapter.py          # GitHub Copilot REST API
│   │
│   ├── normalizer/
│   │   └── schema.py                   # Raw adapter output → UsageRecord / QuotaSnapshot
│   │
│   ├── crud/
│   │   ├── usage.py
│   │   ├── quota.py
│   │   ├── accounts.py
│   │   └── alerts.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dashboard.py                # GET /api/v1/dashboard
│   │   ├── quota.py                    # GET /api/v1/quota/...
│   │   ├── usage.py                    # GET /api/v1/usage
│   │   ├── accounts.py                 # CRUD /api/v1/accounts
│   │   └── alerts.py                   # CRUD /api/v1/alerts
│   │
│   ├── websocket/
│   │   └── quota_stream.py             # WS /ws/quota — live quota push
│   │
│   ├── admin_views.py                  # sqladmin ModelView definitions
│   │
│   ├── scheduler/
│   │   ├── celery_app.py               # Celery + Redis config
│   │   └── tasks.py                    # Poll tasks + alert checker
│   │
│   ├── proto/
│   │   ├── language_server.proto       # Antigravity gRPC proto definition
│   │   └── language_server_pb2*.py     # Generated stubs (grpcio-tools)
│   │
│   ├── migrations/                     # Alembic migration scripts
│   │   ├── env.py
│   │   └── versions/
│   │
│   ├── tests/
│   │   ├── test_adapters.py
│   │   ├── test_api.py
│   │   └── test_normalizer.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── QuotaBar.tsx            # Single model bar with animated countdown
│   │   │   ├── QuotaPanel.tsx          # Full Antigravity-style panel
│   │   │   ├── ToolCard.tsx            # Summary card per tool
│   │   │   ├── AccountTabs.tsx         # Gmail 1 / Gmail 2 / All switcher
│   │   │   ├── UsageChart.tsx
│   │   │   ├── ModelTable.tsx
│   │   │   └── AlertBanner.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── AntigravityPage.tsx
│   │   │   ├── VSCodePage.tsx
│   │   │   ├── CursorPage.tsx
│   │   │   ├── HistoryPage.tsx
│   │   │   ├── AlertsPage.tsx
│   │   │   └── SettingsPage.tsx
│   │   ├── hooks/
│   │   │   ├── useQuotaStream.ts       # WebSocket connection + state
│   │   │   └── useUsageQuery.ts        # Axios + React Query
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── docker-compose.yml                  # PostgreSQL 16 + Redis 7
├── alembic.ini
├── .env.example
└── README.md
```

---

## 12. Setup & Configuration Guide

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker + Docker Compose
- Antigravity IDE installed locally (for live gRPC data)
- `grpcio-tools` for regenerating proto stubs if Antigravity updates

### Step 1 — Clone & Install

```bash
git clone https://github.com/yourname/quotalens
cd quotalens

# Backend
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Generate Antigravity gRPC stubs
python -m grpc_tools.protoc \
    -I proto \
    --python_out=proto \
    --grpc_python_out=proto \
    proto/language_server.proto

# Frontend
cd ../frontend
npm install
```

### Step 2 — Start Infrastructure (Docker)

Docker Compose starts **PostgreSQL 16** and **Redis 7**. The application itself (FastAPI, Celery, React) runs as local processes outside Docker.

```bash
docker-compose up -d
```

> **Note:** Docker is used only for the two infrastructure services. You can skip it entirely by installing PostgreSQL and Redis natively and updating `DATABASE_URL` and `REDIS_URL` in your `.env` accordingly.

The `docker-compose.yml` configures PostgreSQL with database name `model_quota`:

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: model_quota
      POSTGRES_USER: quotalens
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"
```

### Step 3 — Configure Environment

Copy `.env.example` to `.env`:

```env
# ── Database & Queue ─────────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://quotalens:password@localhost:5432/model_quota
REDIS_URL=redis://localhost:6379/0

# ── Security ──────────────────────────────────────────────────────────────
SECRET_KEY=change-this-to-a-random-64-char-string
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-password

# ── Cursor ────────────────────────────────────────────────────────────────
CURSOR_API_KEY=                     # Teams/Enterprise; leave blank for CSV import mode

# ── Antigravity ───────────────────────────────────────────────────────────
ANTIGRAVITY_DIR_GMAIL1=~/.gemini/antigravity
ANTIGRAVITY_DIR_GMAIL2=~/.gemini/techgravity

# ── GitHub Copilot ────────────────────────────────────────────────────────
GITHUB_PAT=ghp_xxxxxxxxxxxxxxxxxxxx
GITHUB_ORG=                         # leave blank if individual (non-org) account

# ── Gemini API ────────────────────────────────────────────────────────────
GEMINI_API_KEY_GMAIL1=AIzaSy...
GEMINI_API_KEY_GMAIL2=AIzaSy...

# ── OpenRouter ────────────────────────────────────────────────────────────
OPENROUTER_API_KEY_GMAIL1=sk-or-v1-...
OPENROUTER_API_KEY_GMAIL2=sk-or-v1-...
OPENROUTER_MGMT_KEY_GMAIL1=          # Management key (for credits endpoint)
OPENROUTER_MGMT_KEY_GMAIL2=

# ── Alerts ────────────────────────────────────────────────────────────────
ALERT_THRESHOLD_WARN=0.75
ALERT_THRESHOLD_CRITICAL=0.90
ALERT_WEBHOOK_URL=                   # optional Slack / Discord webhook

# ── App ───────────────────────────────────────────────────────────────────
DEBUG=True
LOG_LEVEL=INFO
```

### Step 4 — Run Migrations

```bash
cd backend
alembic upgrade head
```

### Step 5 — Start All Services

Open four terminal windows:

```bash
# Terminal 1 — FastAPI backend (hot reload)
uvicorn main:app --reload --port 8000

# Terminal 2 — Celery worker
celery -A scheduler.celery_app worker --loglevel=info

# Terminal 3 — Celery beat (scheduler)
celery -A scheduler.celery_app beat --loglevel=info

# Terminal 4 — React frontend
cd ../frontend && npm run dev
```

| Service | URL |
|---|---|
| React Dashboard | `http://localhost:5173` |
| FastAPI REST Docs (Swagger UI) | `http://localhost:8000/docs` |
| Admin Panel (sqladmin) | `http://localhost:8000/admin` |

### Step 6 — First-Time Account Setup

1. Open the dashboard → **Settings → Accounts**
2. Click **Test All Connections** — the system auto-detects:
   - `~/.gemini/antigravity/` → Gmail 1 Antigravity
   - `~/.gemini/techgravity/` → Gmail 2 Antigravity
3. Paste OpenRouter API keys and Management keys for Gmail 1 and Gmail 2
4. Paste Gemini API keys for Gmail 1 and Gmail 2
5. Paste GitHub PAT for Copilot
6. Optional: upload Cursor CSV if on Individual Pro plan
7. Each account shows a green ✓ or red ✗ connectivity status
8. The first Celery poll runs within 5 minutes and data begins appearing in the dashboard

---

## 13. Known Limitations & Caveats

| Source | Limitation | Workaround / Status |
|---|---|---|
| **Antigravity** | gRPC endpoint is reverse-engineered — may break on Antigravity updates | Auto-fallback to `~/.gemini/*/quota_state.json` file parsing |
| **Antigravity** | Language Server must be running for live gRPC data | File fallback gives last-known quota from most recent IDE session |
| **Antigravity** | Google has cut quotas multiple times without notice | No workaround — limits are reflected accurately as they change |
| **Gemini Free Tier** | No official remaining-quota API endpoint | Local PostgreSQL counter per key / model / day |
| **Gemini Free Tier** | Google may change free tier limits without notice | Limits stored in `gemini_quota_config` table, editable via sqladmin |
| **GitHub Copilot** | Per-token detailed breakdown still rolling out (June 2026) | Aggregate request counts available now; full token data coming |
| **Cursor Individual** | No personal API key — CSV export only | CSV import via Settings → manual periodic upload |
| **OpenRouter Mgmt Key** | Separate from inference key — must be created separately in OpenRouter settings | Credits endpoint skipped gracefully if Management key not configured |
| **All Sources** | Token counts are vendor-reported — may include hidden system prompt tokens | Documented in dashboard tooltips with a "what's counted" info link |

---

## 14. Roadmap

| Version | Features | Estimated Effort |
|---|---|---|
| **v1.0** | Antigravity gRPC (both accounts) + file fallback, OpenRouter (both accounts), Gemini counter, Cursor CSV import, basic React dashboard | 3 weeks |
| **v1.1** | GitHub Copilot API, alert engine, WebSocket live countdowns, sqladmin panel fully configured | 1.5 weeks |
| **v1.2** | Cursor real-time API (Teams), usage history charts, account connectivity test UI | 1.5 weeks |
| **v2.0** | Claude Code transcript parser, Gemini response-header proxy mode, Slack + email digest alerts | 2 weeks |
| **v2.1** | Mobile-responsive layout, PWA support, optional full Docker deployment with nginx reverse proxy | 2 weeks |
| **v3.0** | Multi-user support, role-based access control, cloud-sync option, data retention policies | 4 weeks |

---

## 15. Security Considerations

| Area | Implementation |
|---|---|
| **API Key Storage** | `python-keyring` (OS keychain) in development; AES-256 encrypted in PostgreSQL in production. Never stored in plaintext `.env` files committed to version control. |
| **Admin Panel Auth** | sqladmin at `/admin` protected with username + password (`ADMIN_USERNAME` / `ADMIN_PASSWORD`) and JWT session cookie. |
| **Antigravity gRPC** | Connects to `localhost` only — zero external network exposure. |
| **GitHub PAT** | Should be a fine-grained token scoped to `billing:read` only. Create a dedicated token, not your main dev token. |
| **OpenRouter Mgmt Key** | Has key-management permissions — store separately from the inference key and rotate quarterly. |
| **Gemini API Keys** | Create separate keys per account in Google AI Studio; set per-key quota caps in the AI Studio console as an additional safeguard. |
| **Data Privacy** | Fully local or self-hosted — no data leaves your machine, zero third-party telemetry. |
| **Docker Deployment** | Do not expose ports `8000` or `5432` publicly. Use nginx with HTTPS and IP-allowlisting if accessed over a network. |

> **Data stays local.** QuotaLens is entirely self-hosted. No usage data, API keys, or quota information is sent to any external service beyond the individual tool APIs you configure. The Docker containers run locally and are not exposed to the internet by default.

---

*QuotaLens — Documentation v1.0 — June 2026*
*Stack: FastAPI · SQLAlchemy 2.0 (asyncpg) · sqladmin · Alembic · Celery · Redis · PostgreSQL 16 · React + Vite*
*Database: Model Quota*
