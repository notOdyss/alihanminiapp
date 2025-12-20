import json
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Interaction


class InteractionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        user_id: int,
        interaction_type: str,
        action: str,
        data: Optional[dict] = None
    ) -> Interaction:
        interaction = Interaction(
            user_id=user_id,
            interaction_type=interaction_type,
            action=action,
            data=json.dumps(data) if data else None
        )
        self._session.add(interaction)
        await self._session.flush()
        return interaction

    async def get_user_interactions(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> list[Interaction]:
        result = await self._session.execute(
            select(Interaction)
            .where(Interaction.user_id == user_id)
            .order_by(Interaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_user_interaction_count(self, user_id: int) -> int:
        result = await self._session.execute(
            select(func.count(Interaction.id)).where(Interaction.user_id == user_id)
        )
        return result.scalar() or 0

    async def get_interaction_stats(self, user_id: int) -> dict:
        result = await self._session.execute(
            select(Interaction.interaction_type, func.count(Interaction.id))
            .where(Interaction.user_id == user_id)
            .group_by(Interaction.interaction_type)
        )
        return {row[0]: row[1] for row in result.all()}

    async def get_total_count(self) -> int:
        result = await self._session.execute(select(func.count(Interaction.id)))
        return result.scalar() or 0
