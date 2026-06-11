"""
QuotaLens — FastAPI application entry point.
Assembles all routers, mounts sqladmin, configures CORS and lifespan.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from database import engine, sync_engine
from models import Base
from admin_views import (
    AccountAdmin,
    UsageRecordAdmin,
    QuotaSnapshotAdmin,
    AlertRuleAdmin,
    GeminiQuotaConfigAdmin,
)
from api import dashboard, quota, usage, accounts, alerts, data as data_api
from websocket.quota_stream import router as ws_router
from config import settings


# ── Admin Authentication ─────────────────────────────────────────────────

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if username == settings.admin_username and password == settings.admin_password:
            request.session.update({"authenticated": True})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("authenticated", False)


# ── Lifespan ─────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (for dev; use Alembic migrations in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# ── App Assembly ─────────────────────────────────────────────────────────

app = FastAPI(
    title="QuotaLens",
    description="AI Model Quota & Token Usage Dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API routers
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(quota.router, prefix="/api/v1")
app.include_router(usage.router, prefix="/api/v1")
app.include_router(accounts.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(data_api.router, prefix="/api/v1")

# WebSocket
app.include_router(ws_router)

# sqladmin — admin panel at /admin
authentication_backend = AdminAuth(secret_key=settings.secret_key)
admin = Admin(
    app,
    sync_engine,
    authentication_backend=authentication_backend,
    title="QuotaLens Admin",
)
admin.add_view(AccountAdmin)
admin.add_view(UsageRecordAdmin)
admin.add_view(QuotaSnapshotAdmin)
admin.add_view(AlertRuleAdmin)
admin.add_view(GeminiQuotaConfigAdmin)


# ── Health Check ─────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "QuotaLens", "version": "1.0.0"}
