#!/usr/bin/env python3
"""Run the Web API for Mini App."""
import asyncio
import logging

from aiohttp import web

from bot.database.connection import db_manager
from bot.webapp import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def init_app() -> web.Application:
    await db_manager.init_db()
    logger.info("Database initialized")
    return create_app()


async def cleanup_app(app: web.Application) -> None:
    await db_manager.close()


def main() -> None:
    app = asyncio.get_event_loop().run_until_complete(init_app())
    app.on_cleanup.append(cleanup_app)

    logger.info("Starting Web API on http://0.0.0.0:8080")
    web.run_app(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
