from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import User as TgUser

from bot.database.models import User, Interaction, Transaction


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self._session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_from_tg_user(self, tg_user: TgUser) -> User:
        user = User(
            id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
            language_code=tg_user.language_code,
            is_premium=tg_user.is_premium or False
        )
        self._session.add(user)
        await self._session.flush()
        return user

    async def get_or_create(self, tg_user: TgUser) -> tuple[User, bool]:
        user = await self.get_by_id(tg_user.id)
        if user:
            user.last_active_at = datetime.utcnow()
            if tg_user.username:
                user.username = tg_user.username
            if tg_user.first_name:
                user.first_name = tg_user.first_name
            if tg_user.last_name:
                user.last_name = tg_user.last_name
            await self._session.flush()
            return user, False
        user = await self.create_from_tg_user(tg_user)
        return user, True

    async def update_webapp_visit(self, user_id: int) -> None:
        user = await self.get_by_id(user_id)
        if user:
            user.webapp_sessions += 1
            user.webapp_last_visit = datetime.utcnow()
            await self._session.flush()

    async def get_total_count(self) -> int:
        result = await self._session.execute(select(func.count(User.id)))
        return result.scalar() or 0

    async def get_user_stats(self, user_id: int) -> dict:
        user = await self.get_by_id(user_id)
        if not user:
            return {}

        interaction_count = await self._session.execute(
            select(func.count(Interaction.id)).where(Interaction.user_id == user_id)
        )
        transaction_count = await self._session.execute(
            select(func.count(Transaction.id)).where(Transaction.user_id == user_id)
        )

        return {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "created_at": user.created_at,
            "last_active_at": user.last_active_at,
            "interactions_count": interaction_count.scalar() or 0,
            "transactions_count": transaction_count.scalar() or 0,
            "webapp_sessions": user.webapp_sessions,
            "is_blocked": user.is_blocked
        }

    async def search_by_username(self, username: str) -> list[User]:
        result = await self._session.execute(
            select(User).where(User.username.ilike(f"%{username}%")).limit(10)
        )
        return list(result.scalars().all())

    async def get_recent_users(self, limit: int = 10) -> list[User]:
        result = await self._session.execute(
            select(User).order_by(User.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
