import asyncio
import logging
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import settings
from bot.database.connection import db_manager
from bot.middlewares import DatabaseMiddleware
from logbot.routers import get_logbot_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Starting Log Bot Admin Panel...")

    await db_manager.init_db()
    logger.info("Database initialized")

    bot = Bot(
        token=settings.LOG_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())

    dp.include_router(get_logbot_router())

    try:
        logger.info("Log Bot is running...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await db_manager.close()
        await bot.session.close()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
