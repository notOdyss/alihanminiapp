from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Transaction


class TransactionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        user_id: int,
        payment_method: str,
        amount: Optional[str] = None,
        currency: Optional[str] = None
    ) -> Transaction:
        transaction = Transaction(
            user_id=user_id,
            payment_method=payment_method,
            amount=amount,
            currency=currency,
            status="pending"
        )
        self._session.add(transaction)
        await self._session.flush()
        return transaction

    async def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        result = await self._session.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        transaction_id: int,
        status: str,
        external_id: Optional[str] = None
    ) -> Optional[Transaction]:
        transaction = await self.get_by_id(transaction_id)
        if transaction:
            transaction.status = status
            if external_id:
                transaction.external_id = external_id
            if status == "completed":
                transaction.completed_at = datetime.utcnow()
            await self._session.flush()
        return transaction

    async def get_user_transactions(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> list[Transaction]:
        result = await self._session.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_user_transaction_count(self, user_id: int) -> int:
        result = await self._session.execute(
            select(func.count(Transaction.id)).where(Transaction.user_id == user_id)
        )
        return result.scalar() or 0

    async def get_transaction_stats(self, user_id: int) -> dict:
        result = await self._session.execute(
            select(Transaction.status, func.count(Transaction.id))
            .where(Transaction.user_id == user_id)
            .group_by(Transaction.status)
        )
        return {row[0]: row[1] for row in result.all()}

    async def get_total_count(self) -> int:
        result = await self._session.execute(select(func.count(Transaction.id)))
        return result.scalar() or 0

    async def get_total_by_status(self, status: str) -> int:
        result = await self._session.execute(
            select(func.count(Transaction.id)).where(Transaction.status == status)
        )
        return result.scalar() or 0
