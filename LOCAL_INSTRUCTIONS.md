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
Note: Redis is mapped to host port `6380` (container port `6379`) to avoid conflicts with other services on port `6379`.

## 3. Configure Environment Variables
```bash
copy .env.example .env
# Optionally create a backend‑specific .env (useful when running commands from the backend folder)
copy .env.example backend\.env
```
Edit the `.env` (and `backend\.env` if created) and fill in any required API keys, passwords, and secrets.

When running with Docker Compose, update the database and Redis hosts so containers talk to the service names on the Docker network. In `.env` set:

```text
# inside .env (for Docker)
DATABASE_URL=postgresql+asyncpg://quotalens:password@postgres:5432/model_quota
DATABASE_URL_SYNC=postgresql://quotalens:password@postgres:5432/model_quota
REDIS_URL=redis://redis:6379/0
```

Do NOT leave `localhost` in these URLs when running services in Docker — use the service names `postgres` and `redis` so containers can reach each other.

## 4. Set Up the Python Backend (no virtualenv)

You can run the backend without creating a virtual environment. Choose one of the two options below.

Option A — Install dependencies into your system Python (or any active environment):
```bash
cd backend
pip install -r requirements.txt
```

Option B — Run the backend in Docker (recommended if you prefer containerised services). Example `docker-compose` services you can add to `docker-compose.yml`:

```yaml
	backend:
		image: python:3.11-slim
		container_name: quotalens_backend
		working_dir: /app
		volumes:
			- ./backend:/app:cached
			- ./backend/.env:/app/.env:ro
		command: bash -c "pip install -r requirements.txt && uvicorn main:app --host 0.0.0.0 --port 8000"
		ports:
			- "8000:8000"
		depends_on:
			- postgres
			- redis

	frontend:
		image: node:20-slim
		container_name: quotalens_frontend
		working_dir: /app
		volumes:
			- ./frontend:/app:cached
		command: bash -c "npm install && npm run dev -- --host 0.0.0.0"
		ports:
			- "5173:5173"
		depends_on:
			- backend
```

After adding these services run:

```bash
docker compose up -d --build
```

### Initialise the Database Schema
Apply Alembic migrations (recommended) or start the backend which will create tables automatically. **Do not run `seed.py`** if you do not want demo/fake data — the project will not populate demo data unless the seed script is explicitly executed.

Recommended (migrations):
```bash
cd backend
alembic upgrade head
```

Or start the backend (development) to let the app create tables:
```bash
cd backend
uvicorn main:app --host 127.0.0.1 --port 8000
```

## 5. Run Backend Services
Open separate terminal windows (or use a terminal multiplexer) for each command.
### FastAPI Server
```bash
cd backend
uvicorn main:app --host 127.0.0.1 --port 8000
```
### Celery Worker
```bash
cd backend
celery -A scheduler.celery_app worker --loglevel=info
```
### Celery Beat (Scheduler)
```bash
cd backend
celery -A scheduler.celery_app beat --loglevel=info
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
Make sure the Docker containers are running (Postgres/Redis) or that your database settings point to a running service, then run tests from the `backend` folder:
```bash
cd backend
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
