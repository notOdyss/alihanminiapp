import asyncio
import logging
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web

from bot.config import settings
from bot.database.connection import db_manager
from bot.middlewares import DatabaseMiddleware, TrackingMiddleware
from bot.routers import get_main_router
from bot.services.logger import telegram_logger
from bot.webapp.api import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def start_bot() -> None:
    """Start Telegram bot polling."""
    logger.info("Starting Exchange Bot...")

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    dp.message.middleware(DatabaseMiddleware())
    dp.message.middleware(TrackingMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(TrackingMiddleware())

    dp.include_router(get_main_router())

    try:
        logger.info("Bot is running...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await telegram_logger.close()
        await bot.session.close()


async def start_api() -> None:
    """Start API web server."""
    logger.info("Starting API server...")

    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

    logger.info("API server is running on http://0.0.0.0:8080")

    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()


async def main() -> None:
    """Main entry point - run bot and API server concurrently."""
    await db_manager.init_db()
    logger.info("Database initialized")

    try:
        await asyncio.gather(
            start_bot(),
            # start_api()  # API provided by api/main.py
        )
    finally:
        await db_manager.close()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
