from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.repositories import UserRepository, InteractionRepository
from bot.services.session_tracker import session_tracker


class TrackingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        session: AsyncSession = data.get("session")
        if not session:
            return await handler(event, data)

        user_repo = UserRepository(session)
        interaction_repo = InteractionRepository(session)

        user = None
        interaction_type = "unknown"
        action = ""

        if isinstance(event, Message):
            if event.from_user:
                db_user, is_new = await user_repo.get_or_create(event.from_user)
                data["db_user"] = db_user
                data["is_new_user"] = is_new

                interaction_type = "message"
                action = event.text[:100] if event.text else "media"
                user = event.from_user

                # Track session
                session_tracker.track_action(user, f"📝 {action}")

        elif isinstance(event, CallbackQuery):
            if event.from_user:
                db_user, is_new = await user_repo.get_or_create(event.from_user)
                data["db_user"] = db_user
                data["is_new_user"] = is_new

                interaction_type = "callback"
                action = event.data or "unknown"
                user = event.from_user

                # Track session with readable action names
                action_names = {
                    "new_transaction": "🆕 Новая транзакция",
                    "faq": "❓ FAQ",
                    "back_to_main": "🏠 Главное меню",
                    "pay_paypal": "💳 PayPal",
                    "pay_crypto": "🪙 Крипто",
                    "pay_stripe": "💳 Stripe",
                }
                readable_action = action_names.get(action, action)
                session_tracker.track_action(user, readable_action)

        if user and action:
            await interaction_repo.create(
                user_id=user.id,
                interaction_type=interaction_type,
                action=action
            )

        return await handler(event, data)
