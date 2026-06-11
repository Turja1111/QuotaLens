# QuotaLens — Implementation Plan

> **Goal:** Build the complete QuotaLens application — a self-hosted AI model quota & token usage dashboard tracking Cursor, Antigravity, VS Code Copilot, Gemini API, and OpenRouter across two Gmail accounts.

## User Review Required

> [!IMPORTANT]
> **Scale & Scope:** This is a large full-stack project (FastAPI + PostgreSQL + Celery + Redis + React). The plan below implements the full v1.0 spec from the documentation. I'll build everything in-repo and ensure the project is runnable locally.

> [!WARNING]
> **External Services:** The adapters for Cursor, Antigravity gRPC, Copilot, Gemini API, and OpenRouter will be fully coded per the documentation's specs, but will gracefully handle missing API keys / unavailable services. The app will be fully functional with demo/seed data even without live API connections.

> [!IMPORTANT]
> **Docker Requirement:** PostgreSQL 16 and Redis 7 run via Docker Compose. I'll create the `docker-compose.yml` but you'll need Docker installed to start them. Alternatively, the `.env` can point to natively installed PostgreSQL/Redis.

## Proposed Changes

### Phase 1 — Project Scaffolding & Infrastructure

#### [NEW] docker-compose.yml
PostgreSQL 16 + Redis 7 services with the `model_quota` database.

#### [NEW] .env.example
All environment variables from Section 12 of the docs.

#### [NEW] alembic.ini
Alembic configuration pointing to the backend migrations directory.

#### [NEW] README.md
Quick-start guide.

---

### Phase 2 — Backend Core (Config, Database, Models)

#### [NEW] backend/requirements.txt
All Python dependencies: FastAPI, SQLAlchemy, asyncpg, sqladmin, Celery, Redis, httpx, grpcio, pydantic-settings, python-jose, passlib, plyer, alembic, uvicorn, websockets.

#### [NEW] backend/config.py
Pydantic-settings class reading all `.env` variables with typed fields.

#### [NEW] backend/database.py
Async SQLAlchemy engine + `async_session` factory using asyncpg driver.

#### [NEW] backend/models/base.py
SQLAlchemy declarative base.

#### [NEW] backend/models/account.py
`Account` model — Section 6.1.

#### [NEW] backend/models/usage_record.py
`UsageRecord` model — Section 6.2.

#### [NEW] backend/models/quota_snapshot.py
`QuotaSnapshot` model — Section 6.3.

#### [NEW] backend/models/alert_rule.py
`AlertRule` model — Section 6.4.

#### [NEW] backend/models/gemini_quota_config.py
`GeminiQuotaConfig` model — Section 6.5 with RPM/TPM/RPD per model.

#### [NEW] backend/models/__init__.py
Re-exports all models.

#### [NEW] backend/migrations/env.py
Alembic async migration environment.

#### [NEW] backend/migrations/versions/ (initial migration)
Auto-generated initial migration creating all tables.

---

### Phase 3 — Adapters (Data Source Integrations)

#### [NEW] backend/adapters/base.py
Abstract `BaseAdapter` with `fetch_quota()` and `fetch_usage()` async methods.

#### [NEW] backend/adapters/cursor_adapter.py
Cursor REST API client + CSV parser — Section 7.1.

#### [NEW] backend/adapters/antigravity_adapter.py
gRPC-Web client to local Language Server + file fallback — Section 7.2.

#### [NEW] backend/adapters/copilot_adapter.py
GitHub Copilot REST API client — Section 7.3.

#### [NEW] backend/adapters/gemini_adapter.py
Local counter strategy + rate-limit header parser — Section 7.4.

#### [NEW] backend/adapters/openrouter_adapter.py
OpenRouter REST API client (dual-account) — Section 7.5.

#### [NEW] backend/adapters/__init__.py

#### [NEW] backend/normalizer/schema.py
Normalizes raw adapter output into `UsageRecord` / `QuotaSnapshot` objects.

---

### Phase 4 — CRUD & API Layer

#### [NEW] backend/crud/accounts.py
Account CRUD operations.

#### [NEW] backend/crud/usage.py
Usage record queries with filters (source, account, model, date range).

#### [NEW] backend/crud/quota.py
Quota snapshot queries + latest-per-model logic.

#### [NEW] backend/crud/alerts.py
Alert rule CRUD + cooldown check + fire logic.

#### [NEW] backend/api/__init__.py

#### [NEW] backend/api/dashboard.py
`GET /api/v1/dashboard` — summary cards for all tools/accounts.

#### [NEW] backend/api/quota.py
`GET /api/v1/quota` and `GET /api/v1/quota/{source}/{account_id}`.

#### [NEW] backend/api/usage.py
`GET /api/v1/usage`, `GET /api/v1/usage/summary`, `POST /api/v1/cursor/import`.

#### [NEW] backend/api/accounts.py
Full CRUD for accounts + `POST /api/v1/accounts/{id}/test`.

#### [NEW] backend/api/alerts.py
Alert rule CRUD endpoints.

---

### Phase 5 — WebSocket & Admin Panel

#### [NEW] backend/websocket/quota_stream.py
`WS /ws/quota` — pushes latest quota snapshots every 10 seconds.

#### [NEW] backend/admin_views.py
sqladmin ModelViews for Account, UsageRecord, QuotaSnapshot, AlertRule, GeminiQuotaConfig — Section 9.

---

### Phase 6 — Celery Scheduler

#### [NEW] backend/scheduler/celery_app.py
Celery app with Redis broker + result backend.

#### [NEW] backend/scheduler/tasks.py
All poll tasks (antigravity, openrouter, cursor, gemini, copilot) + alert checker — Section 8.3.

---

### Phase 7 — FastAPI Entry Point

#### [NEW] backend/main.py
FastAPI app assembly: lifespan, routers, sqladmin mount, CORS middleware — Section 8.1.

---

### Phase 8 — React Frontend (Vite + TypeScript)

#### [NEW] frontend/ (Vite project scaffolding)
React 19 + TypeScript + Vite setup with Recharts, React Router, Axios, React Query.

#### [NEW] frontend/src/App.tsx
Main app with React Router layout + sidebar navigation.

#### [NEW] frontend/src/hooks/useQuotaStream.ts
WebSocket hook connecting to `ws://localhost:8000/ws/quota`.

#### [NEW] frontend/src/hooks/useUsageQuery.ts
React Query hooks for API data fetching.

#### [NEW] frontend/src/components/QuotaBar.tsx
Animated single-model quota bar with countdown timer.

#### [NEW] frontend/src/components/QuotaPanel.tsx
Full Antigravity-style panel with all model bars.

#### [NEW] frontend/src/components/ToolCard.tsx
Summary card per tool (icon, quota %, credits, next reset).

#### [NEW] frontend/src/components/AccountTabs.tsx
`[ All Accounts ] [ Gmail 1 ] [ Gmail 2 ]` tab switcher.

#### [NEW] frontend/src/components/UsageChart.tsx
Recharts line/bar/donut charts for usage visualization.

#### [NEW] frontend/src/components/ModelTable.tsx
Sortable/filterable data table for model details.

#### [NEW] frontend/src/components/AlertBanner.tsx
Alert notification banner.

#### [NEW] frontend/src/pages/Dashboard.tsx
Main dashboard: account tabs, tool summary cards, top stats strip.

#### [NEW] frontend/src/pages/AntigravityPage.tsx
Dual-account Antigravity quota panels with live WebSocket countdowns.

#### [NEW] frontend/src/pages/VSCodePage.tsx
Three collapsible sections: Copilot, Gemini API, OpenRouter.

#### [NEW] frontend/src/pages/CursorPage.tsx
Cursor usage and quota display + CSV upload.

#### [NEW] frontend/src/pages/HistoryPage.tsx
Usage history with line/bar/donut/cost charts + data table with CSV export.

#### [NEW] frontend/src/pages/AlertsPage.tsx
Alert rules list + create/edit/delete + notification history.

#### [NEW] frontend/src/pages/SettingsPage.tsx
Tabbed settings: Accounts, Gemini Limits, Polling, Notifications, Data, Admin Link.

---

### Phase 9 — Seed Data & Demo Mode

#### [NEW] backend/seed.py
Script to populate the database with realistic demo data (accounts, usage records, quota snapshots) so the dashboard works immediately without live API connections.

---

## Verification Plan

### Automated Tests
- `python -m pytest backend/tests/` — adapter, API, and normalizer tests.

### Manual Verification
- Start Docker Compose → verify PostgreSQL and Redis are running.
- Run Alembic migrations → verify all tables are created.
- Run seed script → verify demo data populates.
- Start FastAPI → verify Swagger UI at `/docs` and admin at `/admin`.
- Start React dev server → verify dashboard renders with demo data.
- Test WebSocket connection → verify live quota updates.
- Test all frontend pages for responsiveness and visual quality.
