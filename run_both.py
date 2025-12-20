#!/usr/bin/env python3
"""Run both bots concurrently."""
import asyncio
import logging
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import settings
from bot.database.connection import db_manager
from bot.middlewares import DatabaseMiddleware, TrackingMiddleware
from bot.routers import get_main_router
from bot.services.logger import telegram_logger
from logbot.routers import get_logbot_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run_main_bot(main_bot: Bot) -> None:
    dp = Dispatcher()

    dp.message.middleware(DatabaseMiddleware())
    dp.message.middleware(TrackingMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(TrackingMiddleware())

    dp.include_router(get_main_router())

    logger.info("Main Bot is running...")
    await dp.start_polling(main_bot, allowed_updates=dp.resolve_used_update_types())


async def run_log_bot(log_bot: Bot) -> None:
    dp = Dispatcher()

    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())

    dp.include_router(get_logbot_router())

    logger.info("Log Bot is running...")
    await dp.start_polling(log_bot, allowed_updates=dp.resolve_used_update_types())


async def main() -> None:
    logger.info("Starting both bots...")

    await db_manager.init_db()
    logger.info("Database initialized")

    main_bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    log_bot = Bot(
        token=settings.LOG_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    try:
        await asyncio.gather(
            run_main_bot(main_bot),
            run_log_bot(log_bot)
        )
    finally:
        await db_manager.close()
        await telegram_logger.close()
        await main_bot.session.close()
        await log_bot.session.close()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
