# QuotaLens 🔍

> **Self-Hosted AI Model Quota & Token Usage Dashboard**

**QuotaLens** is a unified self-hosted web console designed to aggregate, track, and manage token usage, quota consumption, per-model breakdowns, and rate-limit refresh timers across multiple AI coding assistants. It handles bindings across dual Gmail slots (Gmail Account 1 and Gmail Account 2) for maximum flexibility.

---

## 🛠️ Key Features

- **Unified Control Panel** — Consolidated status metrics for all development environments and accounts on one central screen.
- **Antigravity-Style Progress Panels** — Real-time fill levels and ticking countdowns mimicking the built-in quota console.
- **VS Code Integrations Tracker** — Detailed dashboards tracking VS Code Copilot credit allocations, Gemini API (Free Tier) daily query meters, and OpenRouter credit balances side-by-side.
- **Cursor Manual Import fallback** — Manual drag-and-drop CSV parser to import local Individual Pro logs when an official API is absent.
- **Usage History Analytics** — Interactive Recharts visualization (Daily line trends, model stacks, and token shares) and sortable paginated raw record tables with CSV download options.
- **Custom System Alerts** — System notifications (Desktop alerts or Slack/Discord Webhooks) when a quota consumption reaches 75% or 90%.
- **sqladmin Control Console** — direct table CRUD management at `/admin`.

---

## 📦 Covered Tools & Providers

| Integrated Tool | Binding Slot | Primary Data Source | Refresh Cadence |
| :--- | :--- | :--- | :--- |
| **Cursor Pro** | Single Login | REST API / CSV Dashboard Export | Monthly |
| **Antigravity IDE** | Gmail 1 + Gmail 2 | Local Language Server (gRPC-Web) / Local JSON | 5-Hour Rolling |
| **VS Code — Copilot** | Single GitHub PAT | GitHub Copilot Enterprise/Individual API | Monthly |
| **VS Code — Gemini API** | Gmail 1 + Gmail 2 | Local Counter + HTTP Headers parser | Daily (Midnight Pacific) |
| **VS Code — OpenRouter** | Gmail 1 + Gmail 2 | OpenRouter Management/Credits REST API | Daily (Midnight UTC) |

---

## 🚀 Quick Start Guide

### 1. Fire up Infrastructure (Docker)
Ensure Docker Desktop is running on your workstation. Run the following command from the project root to spin up containerized instances of **PostgreSQL 16** and **Redis 7**. 

*Note: PostgreSQL host port is mapped to `5433` to prevent collisions with any native PostgreSQL servers running on the host on `5432`.*
```bash
docker compose up -d
```

### 2. Configure Environment Settings
Copy the `.env.example` template file into a new file named `.env` in both the workspace root and the `backend` folder. Fill in your corresponding IDE keys, database values, and API credentials:
```bash
copy .env.example .env
copy .env.example backend\.env
```

### 3. Setup Python Backend Environment
Create a dedicated virtual environment in the `backend` directory, activate it, and install python dependencies:
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Apply Database Schema & Seed Data
Initialize all PostgreSQL database tables and populate them with 30 days of realistic usage records and configs:
```bash
python seed.py
```

### 5. Setup React Frontend Client
Navigate to the `frontend` folder, install package dependencies, and spin up the development compiler:
```bash
cd ../frontend
npm install
npm run dev
```

---

## 🕹️ Service Access Points

Open four shell sessions or terminals to run the system processes concurrently:

| Service Process | Execution Command | URL Console |
| :--- | :--- | :--- |
| **FastAPI Web Server** | `cd backend && .\venv\Scripts\uvicorn main:app --host 127.0.0.1 --port 8000` | http://localhost:8000/docs |
| **Celery Tasks Worker** | `cd backend && .\venv\Scripts\celery -A scheduler.celery_app worker --loglevel=info` | Background Process |
| **Celery Scheduler Beat** | `cd backend && .\venv\Scripts\celery -A scheduler.celery_app beat --loglevel=info` | Background Process |
| **React Vite Client** | `cd frontend && npm run dev` | http://localhost:5173 |
| **sqladmin Panel** | Included in FastAPI Web Server | http://localhost:8000/admin |

---

## 📝 Documented local instructions PDF
A formatted PDF copy containing local environment setup checklists, database connection details, and commands is available at:
`[QuotaLens_Local_Instructions.pdf](file:///d:/Projects/QuotaLens/QuotaLens_Local_Instructions.pdf)`

## 🛡️ License
Private — Personal Use Only.
