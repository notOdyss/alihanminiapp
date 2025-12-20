from datetime import datetime
from aiogram import Bot
from aiogram.types import User

from bot.config import settings


class TelegramLogger:
    def __init__(self) -> None:
        self._bot: Bot | None = None

    @property
    def bot(self) -> Bot:
        if self._bot is None:
            self._bot = Bot(token=settings.LOG_BOT_TOKEN)
        return self._bot

    async def log_new_user(self, user: User) -> None:
        username = f"@{user.username}" if user.username else "No username"
        language = user.language_code or "unknown"
        current_time = datetime.now().strftime("%H:%M:%S")

        message = (
            "🆕 <b>Новый пользователь</b>\n\n"
            f"👤 User: {username} (<code>{user.id}</code>)\n"
            f"🌍 Язык: {language}\n"
            f"🕐 Время: {current_time}"
        )

        await self.bot.send_message(
            chat_id=settings.LOG_CHAT_ID,
            text=message,
            parse_mode="HTML"
        )

    async def log_session_end(
        self,
        user: User,
        duration_seconds: int,
        action_count: int,
        last_actions: list[str]
    ) -> None:
        username = f"@{user.username}" if user.username else "No username"
        current_time = datetime.now().strftime("%H:%M:%S")

        # Format duration
        if duration_seconds < 60:
            duration_str = f"{duration_seconds}с"
        else:
            minutes = duration_seconds // 60
            seconds = duration_seconds % 60
            duration_str = f"{minutes}м {seconds}с"

        # Format actions
        actions_str = "\n".join(f"  • {a}" for a in last_actions[-5:]) if last_actions else "  Нет действий"

        # Engagement level
        if action_count >= 10:
            engagement = "🟢 Высокая активность"
        elif action_count >= 5:
            engagement = "🟡 Средняя активность"
        else:
            engagement = "🔴 Низкая активность"

        message = (
            "📊 <b>Сессия завершена</b>\n\n"
            f"👤 User: {username} (<code>{user.id}</code>)\n"
            f"⏱ Время в боте: {duration_str}\n"
            f"🔢 Действий: {action_count}\n"
            f"📈 {engagement}\n\n"
            f"🔍 <b>Последние действия:</b>\n{actions_str}\n\n"
            f"🕐 Время: {current_time}"
        )

        await self.bot.send_message(
            chat_id=settings.LOG_CHAT_ID,
            text=message,
            parse_mode="HTML"
        )

    async def log_transaction(self, user: User, payment_method: str) -> None:
        username = f"@{user.username}" if user.username else "No username"
        current_time = datetime.now().strftime("%H:%M:%S")

        message = (
            "💳 <b>Новая транзакция</b>\n\n"
            f"👤 User: {username} (<code>{user.id}</code>)\n"
            f"💰 Метод: {payment_method}\n"
            f"🕐 Время: {current_time}"
        )

        await self.bot.send_message(
            chat_id=settings.LOG_CHAT_ID,
            text=message,
            parse_mode="HTML"
        )

    async def close(self) -> None:
        if self._bot:
            await self._bot.session.close()


telegram_logger = TelegramLogger()
