"""CRUD operations for accounts."""

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.account import Account


async def get_all_accounts(session: AsyncSession, active_only: bool = True) -> list[Account]:
    stmt = select(Account)
    if active_only:
        stmt = stmt.where(Account.is_active == True)
    result = await session.execute(stmt.order_by(Account.source, Account.label))
    return list(result.scalars().all())


async def get_account(session: AsyncSession, account_id: str) -> Account | None:
    result = await session.execute(
        select(Account).where(Account.id == account_id)
    )
    return result.scalar_one_or_none()


async def get_accounts_by_source(session: AsyncSession, source: str) -> list[Account]:
    result = await session.execute(
        select(Account)
        .where(Account.source == source, Account.is_active == True)
        .order_by(Account.gmail_slot)
    )
    return list(result.scalars().all())


async def create_account(session: AsyncSession, data: dict) -> Account:
    account = Account(**data)
    session.add(account)
    await session.flush()
    return account


async def update_account(session: AsyncSession, account_id: str, data: dict) -> Account | None:
    account = await get_account(session, account_id)
    if not account:
        return None
    for key, value in data.items():
        if hasattr(account, key):
            setattr(account, key, value)
    await session.flush()
    return account


async def delete_account(session: AsyncSession, account_id: str) -> bool:
    result = await session.execute(
        delete(Account).where(Account.id == account_id)
    )
    return result.rowcount > 0
