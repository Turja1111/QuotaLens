# Local Instructions for QuotaLens

This document provides a concise step‑by‑step guide to set up and run the QuotaLens project on a local Windows machine.

## Prerequisites
- **Docker Desktop** (with Docker Compose) installed and running.
- **Python 3.11+** installed and added to `PATH`.
- **Node.js 20+** and **npm** installed (for the frontend).
- **Git** (optional, for cloning the repository).

## 1. Clone the Repository (if not already)
```bash
git clone https://github.com/yourusername/QuotaLens.git
cd QuotaLens
```

## 2. Start Infrastructure (PostgreSQL & Redis)
```bash
docker compose up -d
```
Verify the containers are healthy:
```bash
docker ps
```
You should see `quotalens_postgres` and `quotalens_redis` with status `healthy`.

## 3. Configure Environment Variables
```bash
copy .env.example .env
# Optionally create a backend‑specific .env (useful when running commands from the backend folder)
copy .env.example backend\.env
```
Edit the `.env` (and `backend\.env` if created) and fill in any required API keys, passwords, and secrets.

## 4. Set Up the Python Backend
```bash
cd backend
python -m venv venv
.\\venv\\Scripts\\activate
pip install -r requirements.txt
```
### Initialise the Database & Seed Demo Data
```bash
python seed.py
```
This will create the tables and populate them with realistic demo data.

## 5. Run Backend Services
Open separate terminal windows (or use a terminal multiplexer) for each command.
### FastAPI Server
```bash
cd backend
.\\venv\\Scripts\\uvicorn main:app --host 127.0.0.1 --port 8000
```
### Celery Worker
```bash
cd backend
.\\venv\\Scripts\\celery -A scheduler.celery_app worker --loglevel=info
```
### Celery Beat (Scheduler)
```bash
cd backend
.\\venv\\Scripts\\celery -A scheduler.celery_app beat --loglevel=info
```
The API docs are available at `http://localhost:8000/docs` and the admin panel at `http://localhost:8000/admin`.

## 6. Set Up the React Frontend
```bash
cd ../frontend
npm install
npm run dev
```
The frontend will be served at `http://localhost:5173`.

## 7. Running Tests (Optional)
Make sure the Docker containers are running, then:
```bash
cd backend
.\\venv\\Scripts\\activate
pytest -q
```
All tests should pass.

## 8. Stopping the Project
```bash
# Stop Docker containers
docker compose down
# Stop backend processes (Ctrl+C in each terminal)
```

---
Feel free to modify the `.env` values to point to external PostgreSQL/Redis instances if you prefer not to use Docker.
