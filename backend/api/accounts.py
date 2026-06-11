"""Accounts API — CRUD + connectivity test."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from crud import accounts as accounts_crud
from config import settings
from adapters import (
    CursorAdapter,
    AntigravityAdapter,
    CopilotAdapter,
    GeminiAdapter,
    OpenRouterAdapter,
)

router = APIRouter(tags=["Accounts"])


class AccountCreate(BaseModel):
    id: str
    label: str
    email: str | None = None
    gmail_slot: str | None = None
    source: str


class AccountUpdate(BaseModel):
    label: str | None = None
    email: str | None = None
    is_active: bool | None = None


@router.get("/accounts")
async def list_accounts(session: AsyncSession = Depends(get_session)):
    """List all configured accounts."""
    accounts = await accounts_crud.get_all_accounts(session, active_only=False)
    return {"accounts": [a.to_dict() for a in accounts]}


@router.post("/accounts")
async def create_account(
    body: AccountCreate, session: AsyncSession = Depends(get_session)
):
    """Add a new account."""
    existing = await accounts_crud.get_account(session, body.id)
    if existing:
        raise HTTPException(status_code=409, detail="Account ID already exists")

    account = await accounts_crud.create_account(session, body.model_dump())
    return {"account": account.to_dict()}


@router.put("/accounts/{account_id}")
async def update_account(
    account_id: str,
    body: AccountUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Update account details."""
    data = {k: v for k, v in body.model_dump().items() if v is not None}
    account = await accounts_crud.update_account(session, account_id, data)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account": account.to_dict()}


@router.delete("/accounts/{account_id}")
async def delete_account(
    account_id: str, session: AsyncSession = Depends(get_session)
):
    """Delete an account."""
    deleted = await accounts_crud.delete_account(session, account_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted"}


@router.post("/accounts/{account_id}/test")
async def test_account(
    account_id: str, session: AsyncSession = Depends(get_session)
):
    """Test connectivity for one account."""
    account = await accounts_crud.get_account(session, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    adapter = _get_adapter_for_account(account)
    if not adapter:
        return {"ok": False, "message": "No adapter configured for this source"}

    result = await adapter.test_connection()
    return result


def _get_adapter_for_account(account):
    """Instantiate the appropriate adapter for an account."""
    source = account.source
    slot = account.gmail_slot

    if source == "cursor":
        return CursorAdapter(account.id, settings.cursor_api_key)
    elif source == "antigravity":
        dir_path = (
            settings.antigravity_dir_gmail1
            if slot == "gmail1"
            else settings.antigravity_dir_gmail2
        )
        return AntigravityAdapter(account.id, dir_path, slot or "gmail1")
    elif source == "copilot":
        return CopilotAdapter(account.id, settings.github_pat or "", settings.github_org)
    elif source == "gemini":
        key = (
            settings.gemini_api_key_gmail1
            if slot == "gmail1"
            else settings.gemini_api_key_gmail2
        )
        return GeminiAdapter(account.id, key, slot or "gmail1")
    elif source == "openrouter":
        api_key = (
            settings.openrouter_api_key_gmail1
            if slot == "gmail1"
            else settings.openrouter_api_key_gmail2
        )
        mgmt_key = (
            settings.openrouter_mgmt_key_gmail1
            if slot == "gmail1"
            else settings.openrouter_mgmt_key_gmail2
        )
        return OpenRouterAdapter(account.id, api_key or "", mgmt_key, slot or "gmail1")
    return None
